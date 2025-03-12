import pandas as pd
import numpy as np
import re
import string

# ----------------------------------------
# 1. HELPER FUNCTIONS
# ----------------------------------------

def get_keyword_fraction(series, keywords):
    """
    Returns the fraction of non-null string values in `series` that contain any of the provided `keywords`.
    Uses a vectorized regex search for improved performance.
    """
    values = series.dropna().astype(str).str.lower().str.strip()
    if values.empty:
        return 0
    pattern = '|'.join(re.escape(keyword) for keyword in keywords)
    matches = values.str.contains(pattern, regex=True)
    return matches.mean()

def detect_keyword_based_column(
    df,
    candidate_columns,
    keywords,
    bonus_pattern=None,
    threshold=0.5,
    bonus_multiplier=1.1
):
    """
    Computes the fraction of values that match any of the given keywords using regex for each candidate column.
    Optionally applies a bonus multiplier if the column name matches the bonus pattern.
    Returns the best candidate column if its score exceeds the threshold.
    """
    possible = {}
    for col in candidate_columns:
        fraction = get_keyword_fraction(df[col], keywords)
        # Apply column-name bonus
        if bonus_pattern and re.search(bonus_pattern, col, re.IGNORECASE):
            fraction *= bonus_multiplier
        possible[col] = fraction

    if not possible:
        return None

    best_col = max(possible, key=possible.get)
    if possible[best_col] >= threshold:
        return best_col
    return None

def detect_exact_match_column(
    df,
    candidate_columns,
    expected_values,
    bonus_pattern=None,
    threshold=0.5,
    bonus_multiplier=1.1
):
    """
    Computes the fraction of values that exactly match any of the expected_values for each candidate column.
    Optionally applies a bonus multiplier if the column name matches the bonus pattern.
    Returns the best candidate column if its score exceeds the threshold.
    """
    expected_set = {str(val).lower().strip() for val in expected_values}
    possible = {}
    for col in candidate_columns:
        values = df[col].dropna().astype(str).str.lower().str.strip()
        if values.empty:
            continue
        fraction = values.isin(expected_set).mean()
        # Apply column-name bonus
        if bonus_pattern and re.search(bonus_pattern, col, re.IGNORECASE):
            fraction *= bonus_multiplier
        possible[col] = fraction

    if not possible:
        return None

    best_col = max(possible, key=possible.get)
    if possible[best_col] >= threshold:
        return best_col
    return None

# ----------------------------------------
# 2. REFAC: DETECTION SUBROUTINES
# ----------------------------------------

def detect_numeric_column(df, col_name='sat_score', min_fraction=0.9):
    """
    Detect a single numeric column (by default for 'sat_score').
    Returns the name of the column or None.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # 1) If there's exactly one numeric column, just pick it.
    if len(numeric_cols) == 1:
        return numeric_cols[0]
    
    # 2) Otherwise, pick the column that is numeric for the largest fraction of rows.
    #    We only accept it if that fraction is above `min_fraction`.
    possible_numeric = {}
    for col in df.columns:
        conv = pd.to_numeric(df[col], errors='coerce')
        fraction_numeric = conv.notna().mean()
        possible_numeric[col] = fraction_numeric

    if not possible_numeric:
        return None

    best_col = max(possible_numeric, key=possible_numeric.get)
    if possible_numeric[best_col] >= min_fraction:
        return best_col
    return None

def detect_freeform_answer_column(df, penalty_for_low_uniqueness=0.4):
    """
    Detect the 'freeform_answer' column using heuristics: average length, punctuation, uniqueness.
    Returns the most likely column name or None.
    """
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    if not text_cols:
        return None

    scores = {}
    for col in text_cols:
        series = df[col].dropna().astype(str)
        if series.empty:
            continue
        avg_len = series.apply(len).mean()
        punct_counts = series.apply(lambda x: sum(1 for char in x if char in string.punctuation))
        avg_punct = punct_counts.mean()
        total = len(series)
        unique_ratio = series.nunique() / total if total else 0

        # Weighted composite
        weight_length = 0.4
        weight_punct  = 0.3
        weight_unique = 0.3
        norm_factor = 1e-9  # avoid dividing by 0
        scores[col] = {
            'avg_len': avg_len,
            'avg_punct': avg_punct,
            'unique_ratio': unique_ratio,
        }

    if not scores:
        return None

    # Normalizing across all columns
    max_len   = max(s['avg_len']   for s in scores.values()) or 1e-9
    max_punct = max(s['avg_punct'] for s in scores.values()) or 1e-9

    composite = {}
    for col, s in scores.items():
        norm_len   = s['avg_len'] / max_len
        norm_punct = s['avg_punct'] / max_punct
        comp_score = (0.4 * norm_len) + (0.3 * norm_punct) + (0.3 * s['unique_ratio'])

        # Bonus/penalty for column names
        if "additional_comment" in col.lower():
            comp_score *= 3.1
        if "usage_reason" in col.lower():
            comp_score *= 0.5
        
        # Penalize low uniqueness
        if s['unique_ratio'] < penalty_for_low_uniqueness:
            comp_score *= 0.5

        composite[col] = comp_score
    
    return max(composite, key=composite.get)

def detect_date_column(df, detected_cols):
    """
    Detect a date column by parsing and measuring fraction_valid + uniqueness ratio.
    Returns the best date column or None.
    """
    # We exclude columns already detected for something else
    remaining = [col for col in df.columns if col not in detected_cols.values()]

    possible_dates = {}
    for col in remaining:
        # Attempt to parse the column as a date
        dt_series = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
        fraction_valid = dt_series.notna().mean()
        total = len(dt_series)
        uniqueness_ratio = dt_series.nunique() / total if total > 0 else 0
        # Weighted composite
        score = 0.6 * fraction_valid + 0.4 * uniqueness_ratio

        # Name-based bonus
        if re.search(r'date|time', col, re.IGNORECASE):
            score *= 1.2
        possible_dates[col] = score

    if not possible_dates:
        return None

    best_col = max(possible_dates, key=possible_dates.get)
    # Adjust threshold logic or do multiple checks if you like
    if possible_dates[best_col] >= 0.6:
        return best_col

    # Fallback: if there's a partial match, you could do another pass
    if possible_dates[best_col] >= 0.5:
        return best_col
    return None

# ----------------------------------------
# 3. MAIN AUTO-DETECT FUNCTION
# ----------------------------------------

def auto_detect_columns(df):
    """
    Automatically detect and label DataFrame columns based on heuristics.
    Returns a dictionary mapping semantic names to the corresponding column names.
    """
    detected = {}

    # 1. Detect numeric column (for example, 'sat_score')
    sat_score_col = detect_numeric_column(df, col_name='sat_score', min_fraction=0.9)
    if sat_score_col:
        detected['sat_score'] = sat_score_col

    # 2. Detect natural language response (freeform_answer)
    freeform_col = detect_freeform_answer_column(df)
    if freeform_col:
        detected['freeform_answer'] = freeform_col

    # Helper functino for skipping columns that have already been detected
    def remaining_text_cols():
        return [
            col for col in df.select_dtypes(include=['object']).columns 
            if col not in detected.values()
        ]

    # 3. Detect "career" column
    career_keywords = ["ks3", "parent", "sen", "tutor", "grade", "esl"]
    career_candidate = detect_keyword_based_column(
        df,
        remaining_text_cols(),
        career_keywords,
        bonus_pattern="career",
        threshold=0.5
    )
    if career_candidate:
        detected['career'] = career_candidate

    # 4. Detect "country" column
    country_keywords = [
        'poland','england','united states','romania','jordan','kazakhstan','thailand',
        'italy','philippines','australia','india','south africa','south korea','vietnam',
        'norway','moldova','malaysia','austria','chile','cameroon'
    ]
    country_candidate = detect_keyword_based_column(
        df,
        remaining_text_cols(),
        country_keywords,
        bonus_pattern="country",
        threshold=0.5
    )
    if country_candidate:
        detected['country'] = country_candidate

    # 5. Detect "exit_reason" column
    exit_reason_values = [
        "I can't afford it right now",
        "I'm not using the membership enough",
        "Other",
        "I am on family leave",
        "I can't find the resources I need",
        "I've changed careers",
        "I'm using an alternative resource provider",
        "My school has subscribed",
        "I'm unwell and not working at the moment",
        "I'm retiring"
    ]
    exit_reason_candidate = detect_exact_match_column(
        df,
        remaining_text_cols(),
        exit_reason_values,
        bonus_pattern=r'exit|reason',
        threshold=0.5
    )
    if exit_reason_candidate:
        detected['exit_reason'] = exit_reason_candidate

    # 6. Detect "secondary_reason" column
    secondary_reason_values = [
        'Customer Service','Resource Quality','Variety of Materials',
        'Price','Ease of Website','other'
    ]
    secondary_reason_candidate = detect_exact_match_column(
        df,
        remaining_text_cols(),
        secondary_reason_values,
        bonus_pattern=r'secondary|reason',
        threshold=0.5
    )
    if secondary_reason_candidate:
        detected['secondary_reason'] = secondary_reason_candidate

    # 7. Detect date column 
    date_col = detect_date_column(df, detected)
    if date_col:
        detected['date'] = date_col

    print("Auto-detected columns:", detected)
    print("All columns:", df.columns.tolist())

    return detected
