import pandas as pd


def standardize_column_names(df):

    # Check that the input is actually a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    # .columns gives you all column names
    # .str.strip() removes spaces from edges: "  Name  " → "Name"
    # .str.lower() makes everything lowercase: "Name" → "name"
    # .str.replace(" ", "_") replaces spaces with underscores: "join date" → "join_date"
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    return df

def remove_duplicates(df, subset=None):
    # Removes rows that are exact copies of another row.

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    # drop_duplicates() removes duplicate rows
    # keep="first" means keep the first occurrence, delete the rest
    # .reset_index(drop=True) resets row numbers to 0,1,2,3... after deletion
    df = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)

    return df


def clean_missing_values(df, strategy="drop", fill_value=None):
    # Handles empty/blank cells in the DataFrame.


    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    # Make sure strategy is one of the two valid options
    if strategy not in ("drop", "fill"):
        raise ValueError("strategy must be either 'drop' or 'fill'")

    if strategy == "drop":
        # dropna() removes any row that contains at least one empty cell
        df = df.dropna().reset_index(drop=True)

    elif strategy == "fill":
        # fillna() replaces all empty cells with the fill_value you provide
        df = df.fillna(fill_value)

    return df


def standardize_text_columns(df, columns):

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if not isinstance(columns, list):
        raise TypeError("columns must be a list, e.g. ['city', 'department']")

    for col in columns:
        # Check this column actually exists before trying to clean it
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the DataFrame")

        # .str.strip() → remove leading/trailing spaces
        # .str.title()  → capitalise first letter of each word: "münchen" → "München"
        df[col] = df[col].str.strip().str.title()

    return df

def validate_numeric_column(df, column):

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame")
# pd.to_numeric() converts text to numbers, e.g. "42" → 42
    df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


# ── FUNCTION 6 ───────────────────────────────────────────────────────────────

def validate_date_column(df, column):
# Converts text to proper date objects. If it can't parse a date, it becomes NaT (Not a Time).
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame")

    # pd.to_datetime() converts text to proper date objects
    # errors="coerce" replaces anything it can't parse with NaT (Not a Time)
    # infer_datetime_format=True lets pandas guess the format automatically
    df[column] = pd.to_datetime(df[column], errors="coerce", infer_datetime_format=True)

    return df

def generate_report(df_before, df_after):
# Compares the original and cleaned DataFrames and generates a report on what changed.
    if not isinstance(df_before, pd.DataFrame) or not isinstance(df_after, pd.DataFrame):
        raise TypeError("Both inputs must be pandas DataFrames")

    report = {
        # How many rows were in the original file
        "rows_before": len(df_before),

        # How many rows are in the cleaned file
        "rows_after": len(df_after),

        # How many rows were removed (before minus after)
        "rows_removed": len(df_before) - len(df_after),

        # .isnull() returns True/False for each cell (True = empty)
        # .sum().sum() counts all the Trues — total missing cells
        "missing_before": int(df_before.isnull().sum().sum()),
        "missing_after":  int(df_after.isnull().sum().sum()),

        # List of column names in the cleaned file
        "columns": list(df_after.columns),
    }

    return report
