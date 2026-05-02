import pytest
import pandas as pd


@pytest.fixture
def sample_df():
    data = {
        "Name":       ["Alice", "Bob", "Charlie", "Alice"],
        "Age":        [28, 35, 22, 28],
        "City":       ["München", "Berlin", "Hamburg", "München"],
        "Salary":     [55000, 62000, 48000, 55000],
        "Join Date":  ["2023-01-15", "2023-03-22", "2023-07-10", "2023-01-15"],
        "Department": ["Engineering", "Marketing", "Sales", "Engineering"],
    }
    # pd.DataFrame(data) turns the dictionary into a table
    return pd.DataFrame(data)


@pytest.fixture
def messy_df():
    data = {
        "First Name":  ["  alice  ", "BOB", "Charlie", None],
        "age":         [28, "abc", 22, None],   # "abc" is invalid for age
        "city":        ["münchen", "BERLIN", "  Hamburg  ", None],
        "salary":      [55000, 62000, None, None],
        "join_date":   ["2023-01-15", "not a date", "2023-07-10", None],
        "department":  ["engineering", "MARKETING", "Sales", None],
    }
    return pd.DataFrame(data)


@pytest.fixture
def empty_df():

    return pd.DataFrame()


@pytest.fixture
def single_row_df():

    data = {
        "name":   ["Alice"],
        "age":    [28],
        "city":   ["München"],
        "salary": [55000],
    }
    return pd.DataFrame(data)
