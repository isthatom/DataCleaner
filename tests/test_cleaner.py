
import pytest
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

class TestStandardizeColumnNames:
    def test_makes_columns_lowercase(self, sample_df):
        result = standardize_column_names(sample_df)

        assert all(col == col.lower() for col in result.columns)

    def test_replaces_spaces_with_underscores(self, sample_df):
        """
        "Join Date" should become "join_date" (space → underscore).
        """
        result = standardize_column_names(sample_df)

        # Check no column name contains a space
        assert all(" " not in col for col in result.columns)

    def test_strips_whitespace_from_column_names(self):
        # ARRANGE — create a DataFrame with messy column names
        df = pd.DataFrame({"  Name  ": [1], "  Age  ": [2]})

        # ACT
        result = standardize_column_names(df)

        # ASSERT — column names should now be clean
        assert "name" in result.columns
        assert "age" in result.columns

    def test_raises_error_if_not_dataframe(self):
        # pytest.raises() acts as a context manager (the "with" block)
        # It expects a TypeError to be raised inside the block
        with pytest.raises(TypeError):
            standardize_column_names(["not", "a", "dataframe"])



class TestRemoveDuplicates:

    def test_removes_exact_duplicate_rows(self, sample_df):
        # ARRANGE — confirm we start with 4 rows (Alice appears twice)
        assert len(sample_df) == 4

        # ACT
        result = remove_duplicates(sample_df)

        # ASSERT — should now have 3 rows (one Alice removed)
        assert len(result) == 3

    def test_removes_duplicates_based_on_subset(self, sample_df):
        result = remove_duplicates(sample_df, subset=["Name", "City"])

        # Alice in München appears twice — one should be removed
        alice_rows = result[result["Name"] == "Alice"]
        assert len(alice_rows) == 1

    def test_keeps_first_occurrence(self, sample_df):
        result = remove_duplicates(sample_df)

        # Reset index so row numbers are 0, 1, 2...
        result = result.reset_index(drop=True)

        # Alice should still be in the result (first occurrence kept)
        assert "Alice" in result["Name"].values

    def test_no_duplicates_returns_same_length(self):
        # ARRANGE — DataFrame with no duplicates
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age":  [28, 35, 22]
        })

        result = remove_duplicates(df)

        # ASSERT — length unchanged
        assert len(result) == 3

    def test_raises_error_if_not_dataframe(self):
        with pytest.raises(TypeError):
            remove_duplicates("not a dataframe")

class TestCleanMissingValues:

    def test_drop_strategy_removes_rows_with_nulls(self):
        """
        strategy="drop" should delete any row that has an empty cell.
        """
        # ARRANGE — create a DataFrame where row 1 has a missing value
        df = pd.DataFrame({
            "name":   ["Alice", "Bob",  "Charlie"],
            "salary": [55000,   None,   48000],     # Bob has no salary
        })

        # ACT
        result = clean_missing_values(df, strategy="drop")

        # ASSERT — Bob's row should be gone, only 2 rows remain
        assert len(result) == 2
        assert "Bob" not in result["name"].values

    def test_fill_strategy_replaces_nulls_with_value(self):
        """
        strategy="fill" with fill_value=0 should replace all empty cells with 0.
        """
        df = pd.DataFrame({
            "name":   ["Alice", "Bob"],
            "salary": [55000,   None],
        })

        result = clean_missing_values(df, strategy="fill", fill_value=0)

        # Bob's salary should now be 0, not None
        assert result.loc[1, "salary"] == 0

        # There should be zero missing values in the whole DataFrame
        assert result.isnull().sum().sum() == 0

    def test_fill_strategy_with_string_value(self):
        """
        fill_value can also be a string like "Unknown".
        """
        df = pd.DataFrame({
            "name": ["Alice", None],
            "city": ["München", None],
        })

        result = clean_missing_values(df, strategy="fill", fill_value="Unknown")

        assert result.loc[1, "name"] == "Unknown"
        assert result.loc[1, "city"] == "Unknown"

    def test_raises_error_on_invalid_strategy(self):
        """
        If someone passes strategy="delete" (not a valid option),
        the function should raise a ValueError.
        """
        df = pd.DataFrame({"name": ["Alice"]})

        with pytest.raises(ValueError):
            clean_missing_values(df, strategy="delete")

    def test_raises_error_if_not_dataframe(self):
        with pytest.raises(TypeError):
            clean_missing_values({"name": "Alice"})


class TestStandardizeTextColumns:

    def test_strips_leading_and_trailing_spaces(self):
        """
        "  München  " should become "München" after cleaning.
        """
        df = pd.DataFrame({"city": ["  München  ", "  Berlin  "]})

        result = standardize_text_columns(df, columns=["city"])

        assert result.loc[0, "city"] == "München"
        assert result.loc[1, "city"] == "Berlin"

    def test_title_cases_the_text(self):
        """
        "münchen" and "MÜNCHEN" should both become "München".
        .title() capitalises the first letter of each word.
        """
        df = pd.DataFrame({"city": ["münchen", "BERLIN", "hAmBuRg"]})

        result = standardize_text_columns(df, columns=["city"])

        assert result.loc[0, "city"] == "München"
        assert result.loc[1, "city"] == "Berlin"
        assert result.loc[2, "city"] == "Hamburg"

    def test_cleans_multiple_columns_at_once(self):
        """
        You should be able to pass multiple column names and
        all of them get cleaned in one call.
        """
        df = pd.DataFrame({
            "city":       ["  münchen  "],
            "department": ["  ENGINEERING  "],
        })

        result = standardize_text_columns(df, columns=["city", "department"])

        assert result.loc[0, "city"] == "München"
        assert result.loc[0, "department"] == "Engineering"

    def test_raises_error_if_column_does_not_exist(self):
        """
        If you ask to clean a column that doesn't exist,
        the function should raise a ValueError — not silently do nothing.
        """
        df = pd.DataFrame({"city": ["München"]})

        with pytest.raises(ValueError):
            standardize_text_columns(df, columns=["nonexistent_column"])

    def test_raises_error_if_columns_not_a_list(self):
        """
        columns must be a list. Passing a string like "city"
        instead of ["city"] should raise a TypeError.
        """
        df = pd.DataFrame({"city": ["München"]})

        with pytest.raises(TypeError):
            standardize_text_columns(df, columns="city")   # string, not list


class TestValidateNumericColumn:

    def test_converts_valid_numbers(self):
        """
        Strings that look like numbers ("28") should be converted
        to actual numbers (28).
        """
        df = pd.DataFrame({"age": ["28", "35", "22"]})

        result = validate_numeric_column(df, "age")

        # Check that the column type is now numeric
        assert pd.api.types.is_numeric_dtype(result["age"])

    def test_replaces_invalid_values_with_nan(self):
        """
        Non-numeric values like "abc" should be replaced with NaN.
        The rest of the column should be unaffected.
        """
        df = pd.DataFrame({"age": [28, "abc", 22]})

        result = validate_numeric_column(df, "age")

        # Row 1 ("abc") should now be NaN
        assert pd.isna(result.loc[1, "age"])

        # Rows 0 and 2 should still have their original values
        assert result.loc[0, "age"] == 28
        assert result.loc[2, "age"] == 22

    def test_raises_error_if_column_not_found(self):
        df = pd.DataFrame({"age": [28, 35]})

        with pytest.raises(ValueError):
            validate_numeric_column(df, "nonexistent")


class TestValidateDateColumn:

    def test_converts_valid_date_strings(self):
        """
        "2023-01-15" should be converted to a proper datetime object.
        """
        df = pd.DataFrame({"join_date": ["2023-01-15", "2023-03-22"]})

        result = validate_date_column(df, "join_date")

        # Check the column type is now datetime
        assert pd.api.types.is_datetime64_any_dtype(result["join_date"])

    def test_replaces_invalid_dates_with_nat(self):
        """
        "not a date" is invalid and should become NaT (Not a Time).
        Valid dates should stay intact.
        """
        df = pd.DataFrame({
            "join_date": ["2023-01-15", "not a date", "2023-07-10"]
        })

        result = validate_date_column(df, "join_date")

        # Row 1 should be NaT
        assert pd.isna(result.loc[1, "join_date"])

        # Rows 0 and 2 should be valid dates
        assert not pd.isna(result.loc[0, "join_date"])
        assert not pd.isna(result.loc[2, "join_date"])

    def test_raises_error_if_column_not_found(self):
        df = pd.DataFrame({"join_date": ["2023-01-15"]})

        with pytest.raises(ValueError):
            validate_date_column(df, "wrong_column")


class TestGenerateReport:

    def test_report_contains_correct_keys(self, sample_df):
        """
        The report dictionary should always have these exact keys.
        """
        # Simulate a cleaned version (just remove one row)
        cleaned = sample_df.iloc[1:].reset_index(drop=True)

        report = generate_report(sample_df, cleaned)

        # Check every expected key is present in the report
        assert "rows_before"    in report
        assert "rows_after"     in report
        assert "rows_removed"   in report
        assert "missing_before" in report
        assert "missing_after"  in report
        assert "columns"        in report

    def test_rows_removed_is_correct(self, sample_df):
        """
        If we go from 4 rows to 3 rows, rows_removed should be 1.
        """
        cleaned = sample_df.iloc[:3].reset_index(drop=True)

        report = generate_report(sample_df, cleaned)

        assert report["rows_before"] == 4
        assert report["rows_after"]  == 3
        assert report["rows_removed"] == 1

    def test_missing_count_is_correct(self):
        """
        If before has 2 missing values and after has 0,
        the report should reflect that accurately.
        """
        before = pd.DataFrame({
            "name":   ["Alice", None],
            "salary": [55000,   None],
        })
        after = pd.DataFrame({
            "name":   ["Alice"],
            "salary": [55000],
        })

        report = generate_report(before, after)

        assert report["missing_before"] == 2
        assert report["missing_after"]  == 0

    def test_raises_error_if_inputs_not_dataframes(self, sample_df):
        with pytest.raises(TypeError):
            generate_report(sample_df, "not a dataframe")
