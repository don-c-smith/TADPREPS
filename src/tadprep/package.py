import pandas as pd
from .core.transforms import (
    _file_info_core,
    _reshape_core,
    _rename_and_tag_core,
    _feature_stats_core,
    _impute_core,
    _encode_and_scale_core
)


def prep_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full TADPREPS pipeline on an existing DataFrame.

    This function provides the complete TADPREPS interactive experience without file I/O
    or logging, allowing users to prepare their data through a series of guided steps.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be prepared

    Returns
    -------
    pandas.DataFrame
        The prepared DataFrame after all user-selected transformations

    Examples
    --------
    >>> import pandas as pd
    >>> from tadpreps import prep_df
    >>> df_raw = pd.DataFrame(...)
    >>> df_prepared = prep_df(df_raw)
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    df = reshape(df)
    df = rename_and_tag(df)
    cat_cols, ord_cols, num_cols = feature_stats(df)
    df = impute(df)
    df = encode_and_scale(df, cat_cols, ord_cols, num_cols)

    return df


def file_info(df: pd.DataFrame, verbose: bool = True) -> None:
    """
    Prints top-level information about a DataFrame's structure and contents.

    Basic information (always shown):
    - Total number of instances (rows)
    - Total number of features (columns)
    - Count and percentage of instances containing any missing values

    When verbose=True, the method also displays:
    - Names of all features
    - Data type of each feature
    - Non-null value count for each feature

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be analyzed
    verbose : bool, default=True
        Controls whether detailed feature information is displayed

    Returns
    -------
    None
        This is a void method which prints file information to the console

    Notes
    -----
    Use verbose=True (default) when you need to understand the structure and data types of your features.
    Use verbose=False when you just need quick size and missingness statistics.

    Examples
    --------
    >>> import pandas as pd
    >>> import tadprep
    >>> df = pd.DataFrame({
    ...     'A': [1, 2, None, 4],
    ...     'B': ['x', 'y', 'z', 'w']
    ... })
    >>> tadprep.file_info(df, verbose=True)  # Shows full file information
    >>> tadprep.file_info(df, verbose=False)  # Shows reduced file information
    """
    # Ensure input is a Pandas dataframe
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    # Ensure dataframe is not empty
    if df.empty:
        raise ValueError('Input DataFrame is empty')

    _file_info_core(df, verbose)


def reshape(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Interactively reshapes the input DataFrame according to user specification.
    Allows deletion of missing values, dropping columns, and random sub-setting of instances.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be reshaped
    verbose : bool, default=True
        Controls whether detailed process information is displayed

    Returns
    -------
    pandas.DataFrame
        The reshaped DataFrame as modified by user's specifications

    Examples
    --------
        >>> import pandas as pd
        >>> import tadprep
        >>> df = pd.DataFrame({'A': [1, 2, None], 'B': [4, 5, 6]})
        >>> reshaped_df = tadprep.reshape(df)  # Shows detailed status messages
        >>> quiet_df = tadprep.reshape(df, verbose=False)  # Shows only necessary user prompts
    """
    # Ensure input is a Pandas dataframe
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    # Ensure dataframe is not empty
    if df.empty:
        raise ValueError('Input DataFrame is empty')

    return _reshape_core(df, verbose)


def rename_and_tag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interactively rename features and tag them as ordinal or target variables.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose features need to be renamed/tagged

    Returns
    -------
    pandas.DataFrame
        The DataFrame with renamed/tagged features
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    return _rename_and_tag_core(df)


def feature_stats(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    """
    Analyze and display feature-level statistics and return feature type classifications.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to analyze

    Returns
    -------
    tuple[list[str], list[str], list[str]]
        Lists of categorical, ordinal, and numerical column names
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    return _feature_stats_core(df)


def impute(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interactively impute missing values in the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing missing values to impute

    Returns
    -------
    pandas.DataFrame
        The DataFrame with imputed values
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    return _impute_core(df)


def encode_and_scale(df: pd.DataFrame, cat_cols: list[str],
                     ord_cols: list[str], num_cols: list[str]) -> pd.DataFrame:
    """
    Interactively encode categorical features and scale numerical features.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to encode and scale
    cat_cols : list[str]
        List of categorical column names
    ord_cols : list[str]
        List of ordinal column names
    num_cols : list[str]
        List of numerical column names

    Returns
    -------
    pandas.DataFrame
        The DataFrame with encoded and scaled features
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Input must be a pandas DataFrame')

    return _encode_and_scale_core(df, cat_cols, ord_cols, num_cols)
