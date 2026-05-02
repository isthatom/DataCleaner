import pandas as pd
from data_cleaner import (
    standardize_column_names,
    remove_duplicates,
    clean_missing_values,
    standardize_text_columns,
    validate_numeric_column,
    validate_date_column,
    generate_report,
)


print(" Loading messy data...")
df = pd.read_csv("sample_data/messy_data.csv")
df_original = df.copy()   # save a copy so we can compare at the end

print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
print(f"   Missing values: {df.isnull().sum().sum()}")
print()


print(" Standardizing column names...")
df = standardize_column_names(df)
print(f"   Columns: {list(df.columns)}")
print()

print("  Removing duplicates...")
before = len(df)
df = remove_duplicates(df)
print(f"   Removed {before - len(df)} duplicate rows")
print()

print(" Validating numeric and date columns...")
df = validate_numeric_column(df, "age")
df = validate_date_column(df, "join_date")
print("   Done")
print()

print("  Standardizing text columns...")
df = standardize_text_columns(df, columns=["city", "department"])
print("   Done")
print()


print(" Cleaning missing values...")
df = clean_missing_values(df, strategy="drop")
print(f"   {len(df)} rows remaining after dropping incomplete rows")
print()


df.to_csv("sample_data/clean_data.csv", index=False)
print(" Saved to sample_data/clean_data.csv")
print()

report = generate_report(df_original, df)
print(" Cleaning Report:")
print(f"   Rows before:    {report['rows_before']}")
print(f"   Rows after:     {report['rows_after']}")
print(f"   Rows removed:   {report['rows_removed']}")
print(f"   Missing before: {report['missing_before']}")
print(f"   Missing after:  {report['missing_after']}")
