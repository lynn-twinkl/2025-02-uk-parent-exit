import pandas as pd
import re
from typing import Any

# Precompile regex for special-only strings.
SPECIAL_ONLY_REGEX = re.compile(r'^[^A-Za-z0-9]+$')

def is_numeric_or_special(s: Any) -> bool:
    """
    Check if the provided value is numeric or consists solely of special characters.
    
    Parameters:
        s (Any): The input value to check.
        
    Returns:
        bool: True if the value is numeric or special-only, False otherwise.
    """
    if pd.isnull(s):
        return False
    # Ensure the input is a string.
    s = str(s).strip()

    # Check if the string can be converted to a float.
    try:
        float(s)
        return True
    except ValueError:
        pass

    # Check if the string is composed exclusively of special characters.
    if SPECIAL_ONLY_REGEX.match(s):
        return True

    return False

def remove_numeric_or_special_responses(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """
    Remove rows from the DataFrame where the target column's value is either numeric or 
    consists solely of special characters.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame.
        target_col (str): The name of the column to filter.
        
    Returns:
        pd.DataFrame: A DataFrame with the undesired responses removed.
    """
    filtered_df = df[~df[target_col].map(is_numeric_or_special)].reset_index(drop=True)
    return filtered_df


#####################
# DATE CONVERT
#####################

import pandas as pd
import datetime
from dateutil import parser

def robust_convert_date(date_series):
    """
    Convert a pandas Series containing dates in various formats to datetime objects.

    This function tries:
    1. The built-in pd.to_datetime() with infer_datetime_format and dayfirst options.
    2. Falls back to dateutil.parser.parse for any values that remain unparsed.

    Parameters:
        date_series (pd.Series): A pandas Series with date values (as strings, numbers, etc.)

    Returns:
        pd.Series: A Series of datetime objects (or pd.NaT if conversion fails)
    """
    def convert_single(x):
        # If the value is already a datetime, just return it.
        if pd.isnull(x):
            return pd.NaT
        if isinstance(x, (pd.Timestamp, datetime.datetime)):
            return x
        # First, try using pd.to_datetime with coercion.
        dt = pd.to_datetime(x, errors='coerce', infer_datetime_format=True, dayfirst=True)
        if pd.notnull(dt):
            return dt
        # Fallback: use dateutil.parser to attempt parsing.
        try:
            return parser.parse(str(x), dayfirst=True)
        except Exception:
            return pd.NaT

    return date_series.apply(convert_single)

