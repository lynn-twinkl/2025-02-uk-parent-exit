import pandas as pd

def generate_cancellation_reasons_overview(df, source_col):
    category_counts = df[source_col].value_counts()
    percentages = (category_counts / len(df)) * 100

    # Assigning Priority Thresholds
    low_threshold = category_counts.quantile(0.33)
    high_threshold = category_counts.quantile(0.67)

    # Assigning Priorities
    def assign_priority(count):
        if count >= high_threshold:
            return 'High'
        elif count >= low_threshold:
            return 'Medium'
        else:
            return 'Low'

    # Creating the overview DataFrame
    overview_df = pd.DataFrame({
        'Category': category_counts.index,
        'Count': category_counts.values,
        'Percentage': percentages.round(1).values,
        'Priority': category_counts.apply(assign_priority).values,
    }).reset_index(drop=True)

    return overview_df
