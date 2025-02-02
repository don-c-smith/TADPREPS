import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler


def _file_info_core(df: pd.DataFrame, verbose: bool = True) -> None:
    """
    Core function to print general top-level information about the full, unaltered datafile for the user.

    Args:
        df (pd.DataFrame): A Pandas dataframe containing the full, unaltered dataset.
        verbose (bool): Whether to print more detailed information about the file. Defaults to True.

    Returns:
        None. This is a void function.
    """
    # Print number of instances in file
    print(f'The unaltered file has {df.shape[0]} instances.')  # [0] is rows

    # Print number of features in file
    print(f'\nThe unaltered file has {df.shape[1]} features.')  # [1] is columns

    # Instances with missing values
    row_missing_cnt = df.isnull().any(axis=1).sum()  # Compute count
    row_missing_rate = (row_missing_cnt / len(df) * 100).round(2)  # Compute rate
    print(f'\n{row_missing_cnt} instances ({row_missing_rate}%) contain at least one missing value.')

    if verbose:
        print('-' * 50)  # Visual separator
        # Print names and datatypes of features in file
        print('Names and datatypes of features:')
        print(df.info(memory_usage=False, show_counts=True))
        print('-' * 50)  # Visual separator


def _reshape_core(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Core function for reshaping a DataFrame by handling missing values, dropping features, and subsetting data.

    Args:
        df (pd.DataFrame): Input DataFrame to reshape
        verbose (bool): Whether to print detailed information about operations. Defaults to True.

    Returns:
        pd.DataFrame: Reshaped DataFrame

    Raises:
        ValueError: If invalid indices are provided for column dropping
        ValueError: If an invalid subsetting proportion is provided
    """
    row_missing_cnt = df.isnull().any(axis=1).sum()  # Compute count
    # Ask if the user wants to delete *all* instances with any missing values, if any exist
    if row_missing_cnt > 0:
        user_drop_na = input('Do you want to drop all instances with *any* missing values? (Y/N): ')
        if user_drop_na.lower() == 'y':
            df = df.dropna()
            if verbose:
                print(f'After deletion of instances with missing values, {len(df)} instances remain.')

    # Ask if the user wants to drop any of the columns/features in the dataset
    user_drop_cols = input('Do you want to drop any of the features in the dataset? (Y/N): ')
    if user_drop_cols.lower() == 'y':
        print('The full set of features in the dataset is:')
        for col_idx, column in enumerate(df.columns, 1):  # Create enumerated list of features starting at 1
            print(f'{col_idx}. {column}')

        while True:  # We can justify 'while True' because we have a cancel-out input option
            try:
                drop_cols_input = input('\nEnter the index integers of the features you wish to drop '
                                        '(comma-separated) or enter "C" to cancel: ')

                # Check for user cancellation
                if drop_cols_input.lower() == 'c':
                    if verbose:
                        print('Feature deletion cancelled.')
                    break

                # Create list of column indices to drop
                drop_cols_idx = [int(idx.strip()) for idx in drop_cols_input.split(',')]  # Splitting on comma

                # Verify that all index numbers of columns to be dropped are valid/in range
                if not all(1 <= idx <= len(df.columns) for idx in drop_cols_idx):  # Using a generator
                    raise ValueError('Some feature index integers entered are out of range/invalid.')

                # Convert specified column numbers to actual column names
                drop_cols_names = [df.columns[idx - 1] for idx in drop_cols_idx]  # Subtracting 1 from indices

                # Drop the columns
                df = df.drop(columns=drop_cols_names)
                if verbose:
                    print(f'Dropped features: {",".join(drop_cols_names)}')  # Note dropped columns
                break

            # Catch invalid user input
            except ValueError:
                print('Invalid input. Please enter valid feature index integers separated by commas.')
                continue  # Restart the loop

    # Ask if the user wants to sub-set the data
    user_subset = input('Do you want to sub-set the data by randomly deleting a specified proportion of '
                        'instances? (Y/N): ')
    if user_subset.lower() == 'y':
        while True:  # We can justify 'while True' because we have a cancel-out input option
            try:
                subset_input = input('Enter the proportion of instances to DROP (0.0-1.0) or '
                                     'enter "C" to cancel: ')

                # Check for user cancellation
                if subset_input.lower() == 'c':
                    if verbose:
                        print('Random sub-setting cancelled.')
                    break

                subset_rate = float(subset_input)  # Convert string input to float
                if 0 < subset_rate < 1:  # If the float is valid (i.e. between 0 and 1)
                    retain_rate = 1 - subset_rate  # Compute retention rate
                    retain_row_cnt = int(len(df) * retain_rate)  # Select count of rows to keep in subset

                    df = df.sample(n=retain_row_cnt)  # No random state set b/c we want true randomness
                    if verbose:
                        print(f'Randomly dropped {subset_rate}% of instances. {retain_row_cnt} instances remain.')
                    break

                # Catch user input error for invalid/out-of-range float
                else:
                    print('Enter a value between 0.0 and 1.0.')

            # Catch outer-level user input errors
            except ValueError:
                print('Invalid input. Enter a float value between 0.0 and 1.0 or enter "C" to cancel.')
                continue  # Restart the loop

    return df  # Return the trimmed dataframe


def _rename_and_tag_core(df: pd.DataFrame, verbose: bool = True, tag_features: bool = False) -> pd.DataFrame:
    """
    Core function to rename features and to append the '_ord' and/or '_target' suffixes to ordinal or target features,
    if desired by the user.

    Args:
        df (pd.DataFrame): Input DataFrame to reshape
        verbose (bool): Whether to print detailed information about operations. Defaults to True.
        tag_features (bool): Whether to activate the feature-tagging process. Defaults to False.

    Returns:
        pd.DataFrame: Reshaped DataFrame

    Raises:
        ValueError: If invalid indices are provided for column renaming
        ValueError: If any other invalid input is provided
    """
    if verbose:
        print('Beginning feature renaming process.')
        print('The list of features currently present in the dataset is:')

    else:
        print('Features:')

    for col_idx, column in enumerate(df.columns, 1):  # Create enumerated list of features starting at 1
        print(f'{col_idx}. {column}')

    while True:  # We can justify 'while True' because we have a cancel-out input option
        try:
            rename_cols_input = input('\nEnter the index integer of the feature you wish to rename '
                                      'or enter "C" to cancel: ')

            # Check for user cancellation
            if rename_cols_input.lower() == 'c':
                if verbose:
                    print('Feature renaming cancelled.')
                break

            col_idx = int(rename_cols_input)  # Convert input to integer
            if not 1 <= col_idx <= len(df.columns):  # Validate entry
                raise ValueError('Column index is out of range.')

            # Get new column name from user
            col_name_old = df.columns[col_idx - 1]
            col_name_new = input(f'Enter new name for feature "{col_name_old}": ').strip()

            # Validate name to make sure it doesn't already exist
            if col_name_new in df.columns:
                print(f'Feature name "{col_name_new}" already exists. Choose a different name.')
                continue  # Restart the loop

            # Rename column in-place
            df = df.rename(columns={col_name_old: col_name_new})
            if verbose:
                print(f'Renamed feature "{col_name_old}" to "{col_name_new}".')

            # Ask if user wants to rename another column
            if input('Do you want to rename another feature? (Y/N): ').lower() != 'y':
                break

        # Catch input errors
        except ValueError as exc:
            print(f'Invalid input: {exc}')

    if tag_features:
        if verbose:
            print('\nBeginning ordinal feature tagging process.')
            print('You may now select any ordinal features which you know to be present in the dataset and append the '
                  '"_ord" suffix to their feature names.')
            print('If no ordinal features are present in the dataset, simply enter "C" to bypass this process.')
        else:
            print('\nOrdinal feature tagging:')

        print('\nFeatures:')
        for col_idx, column in enumerate(df.columns, 1):
            print(f'{col_idx}. {column}')

        while True:  # We can justify 'while True' because we have a cancel-out input option
            try:
                ord_input = input('\nEnter the index integers of ordinal features (comma-separated) '
                                  'or enter "C" to cancel: ')

                if ord_input.lower() == 'c':  # If user cancels
                    if verbose:
                        print('Ordinal feature tagging cancelled.')  # Note the cancellation
                    break  # Exit the loop

                ord_idx_list = [int(idx.strip()) for idx in ord_input.split(',')]  # Create list of index integers

                # Validate that all entered index integers are in range
                if not all(1 <= idx <= len(df.columns) for idx in ord_idx_list):
                    raise ValueError('Some feature indices are out of range.')

                ord_names_pretag = [df.columns[idx - 1] for idx in ord_idx_list]  # Create list of pretag names

                # Generate mapper for renaming columns with '_ord' suffix
                ord_rename_map = {name: f'{name}_ord' for name in ord_names_pretag if not name.endswith('_ord')}

                # Validate that tags for the selected columns are not already present (i.e. done pre-import)
                if not ord_rename_map:  # If the mapper is empty
                    print('WARNING: All selected features are already tagged as ordinal.')  # Warn the user
                    break

                df.rename(columns=ord_rename_map, inplace=True)  # Perform tagging
                if verbose:
                    print(f'Tagged the following features as ordinal: {", ".join(ord_rename_map.keys())}')
                break

            # Catch invalid input
            except ValueError as exc:
                print(f'Invalid input: {exc}')
                continue

        if verbose:
            print('\nBeginning target feature tagging process.')
            print('You may now select any target features which you know to be present in the dataset and append the '
                  '"_target" suffix to their feature names.')
            print(' If no target features are present in the dataset, simply enter "C" to bypass this process.')
        else:
            print('\nTarget feature tagging:')

        print('\nFeatures:')
        for col_idx, column in enumerate(df.columns, 1):
            print(f'{col_idx}. {column}')

        while True:  # We can justify 'while True' because we have a cancel-out input option
            try:
                target_input = input('\nEnter the index integers of target features (comma-separated) '
                                     'or enter "C" to cancel: ')

                # Check for user cancellation
                if target_input.lower() == 'c':
                    if verbose:
                        print('Target feature tagging cancelled.')
                    break

                target_idx_list = [int(idx.strip()) for idx in target_input.split(',')]  # Create list of index integers

                # Validate that all entered index integers are in range
                if not all(1 <= idx <= len(df.columns) for idx in target_idx_list):
                    raise ValueError('Some feature indices are out of range.')

                target_names_pretag = [df.columns[idx - 1] for idx in target_idx_list]  # List of pretag names

                # Generate mapper for renaming columns with '_target' suffix
                target_rename_map = {name: f'{name}_target' for name in target_names_pretag if
                                     not name.endswith('_target')}

                # Validate that tags for the selected columns are not already present (i.e. done pre-import)
                if not target_rename_map:  # If the mapper is empty
                    print('WARNING: All selected features are already tagged as targets.')  # Warn the user
                    break

                df = df.rename(columns=target_rename_map)  # Perform tagging
                if verbose:
                    print(f'Tagged the following features as targets: {", ".join(target_rename_map.keys())}')
                break

            # Catch invalid input
            except ValueError as exc:
                print(f'Invalid input: {exc}')
                continue  # Restart the loop

    return df  # Return dataframe with renamed and tagged columns


def _feature_stats_core(df: pd.DataFrame, verbose: bool = True, summary_stats: bool = False) -> None:
    """
    Core function to aggregate the features by class (i.e. feature type) and print top-level missingness and
    descriptive statistics information at the feature level.
    It can build and display summary tables at the feature-class level if requested by the user.

    Args:
        df (pd.DataFrame): The input dataframe for analysis.
        verbose (bool): Whether to print more detailed information/visuals for each feature. Defaults to True.
        summary_stats (bool): Whether to print summary statistics at the feature-class level. Defaults to False.

    Returns:
        None. This is a void function.
    """
    if verbose:
        print('Displaying top-level information for features in dataset...')
        print('-' * 50)  # Visual separator

    # Create a list of columns which are categorical (object or categorical dtype)
    cat_cols = [column for column in df.columns if isinstance(df[column].dtype, pd.CategoricalDtype)]

    # Create a list of columns which are numerical
    num_cols = [column for column in df.columns
                if isinstance(df[column].dtype, (np.number, pd.Float64Dtype, pd.Int64Dtype))]

    if verbose:
        if cat_cols:
            print('The categorical features are:')
            print(', '.join(cat_cols))
            print('-' * 50)
        else:
            print('No categorical features were found in the dataset.')
            print('-' * 50)

        if num_cols:
            print('The numerical features are:')
            print(', '.join(num_cols))
            print('-' * 50)
        else:
            print('No numerical features were found in the dataset.')
            print('-' * 50)

        print('Producing key values at the feature level...')

    def show_key_vals(column: str, df: pd.DataFrame, feature_type: str):
        """This helper function calculates and prints key values and missingness info at the feature level."""
        if verbose:
            print('-' * 50)
            print(f'Key values for {feature_type} feature "{column}":')
            print('-' * 50)
        else:
            print(f'\nFeature: "{column}" - ({feature_type})')

        # Calculate missingness at feature level
        missing_cnt = df[column].isnull().sum()  # Total count
        missing_rate = (missing_cnt / len(df) * 100).round(2)  # Missingness rate
        print(f'Missing values: {missing_cnt} ({missing_rate}%)')

        # Ensure the feature is not fully null before producing value counts
        if not df[column].isnull().all():
            if feature_type == 'Categorical':
                value_counts = df[column].value_counts()
                mode_val = df[column].mode().iloc[0] if not df[column].mode().empty else 'No mode exists'
                print(f'Unique values: {df[column].nunique()}')
                print(f'Mode: {mode_val}')
                if verbose:
                    print('\nValue counts:')
                    print(value_counts)

            if feature_type == 'Numerical':
                stats = df[column].describe()
                print(f'Mean: {stats["mean"]:.4f}')

                if verbose:
                    print(f'Median: {stats["50%"]:.4f}')
                    print(f'Std Dev: {stats["std"]:.4f}')

                print(f'Min: {stats["min"]:.4f}')
                print(f'Max: {stats["max"]:.4f}')

    # Display feature-level statistics
    if cat_cols:
        if verbose:
            print('\nKEY VALUES FOR CATEGORICAL FEATURES:')
        for column in cat_cols:
            show_key_vals(column, df, 'Categorical')

    if num_cols:
        if verbose:
            print('\nKEY VALUES FOR NUMERICAL FEATURES:')
        for column in num_cols:
            show_key_vals(column, df, 'Numerical')

    # Display feature-class level statistics if requested
    if summary_stats:
        if cat_cols:
            if verbose:
                print('\nCATEGORICAL FEATURES SUMMARY STATISTICS:')
                print('-' * 50)

            cat_summary = pd.DataFrame({
                'Unique_values': [df[column].nunique() for column in cat_cols],
                'Missing_count': [df[column].isnull().sum() for column in cat_cols],
                'Missing_rate': [(df[column].isnull().sum() / len(df) * 100).round(2)
                                 for column in cat_cols]
            }, index=cat_cols)
            print('\nCategorical Features Summary Table:')
            print(str(cat_summary))

        if num_cols:
            if verbose:
                print('\nNUMERICAL FEATURES SUMMARY STATISTICS:')
                print('-' * 50)

            num_summary = df[num_cols].describe()
            print('\nNumerical Features Summary Table:')
            print(str(num_summary))


def _impute_core(df: pd.DataFrame, verbose: bool = True, skip_warnings: bool = False) -> pd.DataFrame:
    """
    Core function to perform simple imputation for missing values at the feature level.
    Supports mean, median, and mode imputation based on feature type.

    Args:
        df (pd.DataFrame): Input DataFrame containing features to impute.
        verbose (bool): Whether to display detailed guidance and explanations. Defaults to True.
        skip_warnings (bool): Whether to skip missingness threshold warnings. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with imputed values where specified by user.
    """
    # Check if there are no missing values - if no missing values exist, skip imputation
    if not df.isnull().any().any():
        print('WARNING: No missing values present in dataset. Skipping imputation. Dataframe was not modified.')
        return df

    # Identify initial feature types using list comprehensions
    categorical_cols = [col for col in df.columns if pd.api.types.is_object_dtype(df[col])
                        or isinstance(df[col].dtype, pd.CategoricalDtype)]

    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    # Top-level feature classification information if Verbose is True
    if verbose:
        print('\nInitial feature type identification:')
        print(f'Categorical features: {", ".join(categorical_cols) if categorical_cols else "None"}')
        print(f'Numerical features: {", ".join(numeric_cols) if numeric_cols else "None"}')
        print('-' * 50)

    # Check for numeric features that might actually be categorical in function/intent
    true_numeric = numeric_cols.copy()  # Start with all numeric columns
    for col in numeric_cols:
        unique_vals = sorted(df[col].dropna().unique())

        # We suspect that any all-integer column with five or fewer unique values is actually categorical
        if len(unique_vals) <= 5 and all(float(x).is_integer() for x in unique_vals if pd.notna(x)):
            if verbose:
                print(f'\nFeature "{col}" has only {len(unique_vals)} unique integer values: {unique_vals}')
                print('ALERT: This could be a categorical feature encoded as numbers, e.g. a 1/0 representation of '
                      'Yes/No values.')
                print('-' * 50)

            # Ask the user to assess and reply
            user_cat = input(f'Should "{col}" actually be treated as categorical? (Y/N): ')

            # If user agrees, recast the feature to string-type and append to list of categorical features
            if user_cat.lower() == 'y':
                df[col] = df[col].astype(str)
                categorical_cols.append(col)
                true_numeric.remove(col)  # Remove from numeric if identified as categorical
                if verbose:
                    print(f'Converted numerical feature "{col}" to categorical type.')
                    print('-' * 50)

    # Final feature classification info if Verbose is True
    if verbose:
        print('\nFinal feature type classification:')
        print(f'Categorical features: {", ".join(categorical_cols) if categorical_cols else "None"}')
        print(f'Numerical features: {", ".join(true_numeric) if true_numeric else "None"}')
        print('-' * 50)

    # For each feature, calculate missingness statistics
    if verbose:
        print('Count and rate of missingness for each feature:')

    # Calculate missingness values
    missingness_vals = {}
    for column in df.columns:
        missing_cnt = df[column].isnull().sum()
        missing_rate = (missing_cnt / len(df) * 100).round(2)
        missingness_vals[column] = {'count': missing_cnt, 'rate': missing_rate}

    if verbose:
        for column, vals in missingness_vals.items():
            print(f'Feature {column} has {vals["count"]} missing values. ({vals["rate"]}% missing)')

    if not skip_warnings and verbose:
        print('\nWARNING: Imputing missing values for features with a missing rate over 10% is not recommended '
              'due to potential bias introduction.')

    # Build list of good candidates for imputation
    imp_candidates = [key for key, value in missingness_vals.items() if 0 < value['rate'] <= 10]

    # We only walk through the imputation missingess-rate guidance if the user hasn't set skip_warnings to False
    if not skip_warnings:
        if imp_candidates and verbose:
            print('Based on missingness rates, the following features are good candidates for imputation:')
            for key in imp_candidates:
                print(f'- {key}: {missingness_vals[key]["rate"]}% missing')
        elif verbose:
            print('No features fall within the recommended rate range for imputation.')
            print('WARNING: Statistical best practices indicate you should not perform imputation.')

    # Ask if user wants to override the recommendation
    while True:
        try:
            user_override = input('\nDo you wish to:\n'
                                  '1. Impute only for recommended features (<= 10% missing)\n'
                                  '2. Override the warning and consider all features with missing values\n'
                                  '3. Skip imputation\n'
                                  'Enter choice: ').strip()

            # Catch bad input
            if user_override not in ['1', '2', '3']:
                raise ValueError('Please enter 1, 2, or 3.')

            if user_override == '3':
                print('Skipping imputation. No changes made to dataset.')
                return df

            # Build list of features to be imputed
            imp_features = (imp_candidates if user_override == '1'
                            else [key for key, value in missingness_vals.items() if value['count'] > 0])

            # If user wants to follow missingness guidelines and no good candidates exist, skip imputation
            if not imp_features:
                print('No features available for imputation given user input. Skipping imputation.')
                return df

            # Exit the loop once the imp_features list is built
            break

        # Catch all other input errors
        except ValueError as exc:
            print(f'Invalid input: {exc}')
            continue  # Restart loop

    # Offer methodology explanations if desired by user if Verbose is True
    if verbose:
        print('\nWARNING: TADPREP supports only mean, median, and mode imputation.')
        print('For more sophisticated methods (e.g. imputation-by-modeling), skip this step and write '
              'your own imputation code.')

        user_impute_refresh = input('Do you want to see a brief refresher on these imputation methods? (Y/N): ')
        if user_impute_refresh.lower() == 'y':
            print('\nSimple Imputation Methods Overview:'
                  '\n- Mean: Best for normally-distributed data. Theoretically practical. Highly sensitive to outliers.'
                  '\n- Median: Better for skewed numerical data. Robust to outliers.'
                  '\n- Mode: Useful for categorical and fully-discrete numerical data.')

    # Begin imputation at feature level
    for feature in imp_features:
        if verbose:
            print(f'\nProcessing feature {feature}...')
            print(f'- Datatype: {df[feature].dtype}')
            print(f'- Missing rate: {missingness_vals[feature]["rate"]}%')

        # Build list of available/valid imputation methods based on feature datatype
        if feature in true_numeric:
            val_methods = ['Mean', 'Median', 'Mode', 'Skip imputation for this feature']
        else:
            val_methods = ['Mode', 'Skip imputation for this feature']

        # Prompt user to select an imputation method
        while True:
            method_items = [f'{idx}. {method}' for idx, method in enumerate(val_methods, 1)]
            method_prompt = f'Choose imputation method:\n{"\n".join(method_items)}\nEnter the number of your choice: '
            user_imp_choice = input(method_prompt)

            # Reset method index
            try:
                method_idx = int(user_imp_choice) - 1

                # Choose imputation method and exit loop
                if 0 <= method_idx < len(val_methods):
                    imp_method = val_methods[method_idx]
                    break

                # Catch bad user input
                else:
                    print('Invalid input. Enter a valid number.')

            except ValueError:
                print('Invalid input. Enter a valid number.')

        # Notify user of skips if Verbose is True
        if imp_method == 'Skip imputation for this feature':
            if verbose:
                print(f'Skipping imputation for feature: "{feature}"')
            continue

        # Begin actual imputation process
        try:
            # Calculate impute values based on method selection
            if imp_method == 'Mean':
                imp_val = df[feature].mean()

            elif imp_method == 'Median':
                imp_val = df[feature].median()

            else:  # Mode
                mode_vals = df[feature].mode()

                # Catch and notify if no mode value exists
                if len(mode_vals) == 0:
                    if verbose:
                        print(f'No mode value exists for feature {feature}. Skipping imputation for this feature.')
                    continue

                imp_val = mode_vals[0]  # Note that we select the first mode

            # Impute missing values at feature level
            feature_missing_cnt = missingness_vals[feature]['count']
            if verbose:
                print(f'Replacing {feature_missing_cnt} missing values for {feature} '
                      f'using {imp_method} value of {imp_val}.')
            df = df.fillna({feature: imp_val})

        # Catch all other imputation errors
        except Exception as exc:
            print(f'Error during imputation for feature {feature}: {exc}')
            if verbose:
                print('Skipping imputation for this feature.')
            continue  # Restart loop

    return df  # Return dataframe with imputed values


# TODO: This helper function should get folded into both the impute and encode functions
def handle_numeric_cats(df: pd.DataFrame, init_num_cols: list[str]) -> tuple[list[str], list[str]]:
    """
    This internal helper function identifies numerical features that might actually be categorical in function.
    If such a feature is identified as categorical, the function converts its values to strings in-place.
    It returns two lists: one of confirmed numerical columns and another for newly-identified categorical columns.
    """
    # Instantiate empty lists to hold the features after parsing
    true_num_cols = []
    true_cat_cols = []

    for column in init_num_cols:  # For each feature that was initially identified as numeric
        unique_vals = sorted(df[column].unique())  # Calculate number of unique values
        if (len(unique_vals) <= 5 and  # If that value is small
                all(float(x).is_integer() for x in unique_vals if pd.notna(x))):  # And all values are integers

            print(f'\nFeature "{column}" has only {len(unique_vals)} unique integer values: {unique_vals}')
            print('ALERT: This could be a categorical feature encoded as numbers, e.g. a 1/0 representation of '
                  'Yes/No values.')

            user_cat = input(f'Should "{column}" actually be treated as categorical? (Y/N): ')  # Ask user to choose
            if user_cat.lower() == 'y':
                df[column] = df[column].astype(str)  # Cast the values to strings in-place
                true_cat_cols.append(column)  # Add the identified feature to the true_cat_cols list
                print(f'Converted numerical feature "{column}" to categorical type.')  # Log the choice
                print('-' * 50)  # Visual separator

            # Otherwise, if user says no, treat the feature as truly numeric
            else:
                true_num_cols.append(column)

        # If the feature fails the checks, treat the feature as truly numeric
        else:
            true_num_cols.append(column)

    return true_num_cols, true_cat_cols  # Return the lists of true numerical and identified categorical features


# TODO: Major refactor is needed
# TODO: This needs to be broken out into separate encode and scale functions, which will drive two separate methods
# TODO: We should probably not ask the user for lists-by-type but rather a list of the features they want to encode
# TODO: The encoding function needs to also use handle_numeric_cats to make sure "actually categorical numeric features" are presented as encoding candidates
# TODO: Rather than make the user categorize every feature (if they don't pass a list of features to encode), we should use datatypes to pre-fill the lists, ask user if the lists of feature-by-type are correct, and if not, ask which features need to have their datatypes changed
# TODO: We also need a line in the docstring and a 'verbose' print statement which reminds the user that target features should not be encoded
# TODO: There are a lot of explanatory print statements and offers of explanation which need to get housed inside verbose conditionals
# TODO: We need a skip_warnings boolean parameter which doesn't show the print statements about null values, low frequency categories, high cardinality, etc.
# TODO: We actually can't have unclassified features, so the 'skip this feature' option in the categorization process needs to go
# TODO: Additionally, we need the ability to get some simple descriptives printed for each feature during categorization in case the user doesn't know anything about the feature
# TODO: We also need a line in the docstring and a 'verbose' print statement which reminds the user that the original features are dropped once they've been encoded
def _encode_and_scale_core(
        df: pd.DataFrame,
        cat_features: list[str] | None = None,
        ord_features: list[str] | None = None,
        num_features: list[str] | None = None
) -> pd.DataFrame:
    """
    This method allows the user to use appropriate encoding methods on the categorical and ordinal features in
    the dataset. It also allows the user to apply scaling methods to the numerical features.
    Lists of features by datatype may be directly passed to the method by the user. If no lists of features by type
    are passed to the method, the method will work interactively with the user to define these lists.
    Note that the actual 'engine' of this method is the set of three helper functions
    defined within its scope.
    Args:
        df (pd.Dataframe): Input dataframe.
        cat_features (list[str], optional): List of categorical column names for encoding
        ord_features (list[str], optional): List of ordinal column names
        num_features (list[str], optional): List of numerical column names for scaling
    Returns:
        df (pd.DataFrame): A dataframe with encoded and scaled features.
    """
    # Fetch all features which have been type-specified
    specified_features = set()
    if cat_features:
        specified_features.update(cat_features)
    if ord_features:
        specified_features.update(ord_features)
    if num_features:
        specified_features.update(num_features)

    # Validate specified features exist in dataframe
    if not all(col in df.columns for col in specified_features):
        missing = [col for col in specified_features if col not in df.columns]
        raise ValueError(f'Features not found in dataframe: {missing}')

    # Initialize empty lists if None was provided
    cat_features = cat_features or []
    ord_features = ord_features or []
    num_features = num_features or []

    # Find features that haven't been categorized
    uncat_features = [col for col in df.columns if col not in specified_features]

    # If any features remain uncategorized, ask user about those specific features
    if uncat_features:
        print('Some features have not been categorized. Please identify their types:')

        for col in uncat_features:
            while True:
                print(f'\nFeature: {col}')
                print(f'Current dtype: {df[col].dtype}')
                print('1. Categorical (Unordered categories)')
                print('2. Ordinal (Ordered categories, e.g. a Likert scale)')
                print('3. Numerical')
                print('4. Skip this feature')

                user_choice = input('Enter choice (1-4): ').strip()

                if user_choice == '1':
                    cat_features.append(col)
                    break
                elif user_choice == '2':
                    ord_features.append(col)
                    break
                elif user_choice == '3':
                    num_features.append(col)
                    break
                elif user_choice == '4':
                    break
                else:
                    print('Invalid choice. Please enter 1, 2, 3, or 4.')

    def handle_cats():
        """This internal helper function facilitates the encoding of categorical features, if desired by the user."""
        nonlocal df  # Specify that this object comes from the outer scope

        if not cat_features:  # If the list of categorical columns is empty
            print('No categorical features to process. Skipping encoding.')  # Note this
            return  # And exit the process

        print(f'The dataset contains {len(cat_features)} categorical feature(s).')  # Print # of categorical features

        # Notify user that TADPREP only supports common encoding methods
        print('\nNOTE: TADPREP only supports One-Hot and Dummy encoding.')
        print('If you wish to use other, more complex encoding methods, skip this step and write your own code.')

        # Ask if user wants to proceed
        user_encode = input('\nDo you want to Dummy or One-Hot encode any of the categorical features? (Y/N): ')
        if user_encode.lower() != 'y':  # If not
            print('Skipping encoding of categorical features.')  # Log that fact
            return  # And exit the process

        # Ask if user wants a refresher on One-Hot vs. Dummy encoding
        user_encode_refresh = input('Do you want to see a brief refresher on One-Hot vs. Dummy encoding? (Y/N): ')
        if user_encode_refresh.lower() == 'y':  # If so, display refresher
            print('\nOverview of One-Hot vs. Dummy Encoding:'
                  '\nOne-Hot Encoding: '
                  '\n- Creates a new binary column for every unique category.'
                  '\n- No information is lost, which preserves interpretability, but more features are created.'
                  '\n- This method is preferred for non-linear models like decision trees.'
                  '\n'
                  '\nDummy Encoding:'
                  '\n- Creates n-1 binary columns given n categories in the feature.'
                  '\n- One category becomes the reference class, and is represented by all zeros.'
                  '\n- Dummy encoding is preferred for linear models, as it avoids perfect multi-collinearity.'
                  '\n- This method is more computationally- and space-efficient, but is less interpretable.')

        encoded_cols = []  # Instantiate an empty list to hold the encoded columns for final reporting
        encoded_dfs = []  # Instantiate an empty list to collect encoded DataFrames
        columns_to_drop = []  # Instantiate an empty list to collect the original columns to drop

        # Begin encoding process at the feature level
        for column in cat_features:
            print(f'\nProcessing feature: "{column}"')

            # Check if user wants to encode this feature
            user_encode_feature = input(f'Do you want to encode "{column}"? (Y/N): ')
            if user_encode_feature.lower() != 'y':  # If not
                print(f'Skipping encoding for feature: "{column}"')  # Log that choice
                continue  # And move to the next feature

            # Show unique value count
            unique_cnt = df[column].nunique()
            print(f'Feature "{column}" has {unique_cnt} unique values.')

            # Check for nulls before proceeding
            null_cnt = df[column].isnull().sum()
            if null_cnt > 0:  # If nulls are present
                # Print a warning
                print(f'Feature "{column}" contains {null_cnt} null values. Encoding may produce unexpected results.')
                # Ask if the user wants to proceed anyway
                user_proceed = input('Do you want to proceed with encoding this feature? (Y/N): ')
                if user_proceed.lower() != 'y':  # If not
                    print(f'Skipping encoding for feature: "{column}"')  # Log the choice
                    continue  # Move on to the next feature

            # Check for single-value features and log a warning if this feature is single-value
            if unique_cnt == 1:
                print(f'Feature "{column}" has only one unique value. Consider dropping this feature.')
                continue  # Move on to the next feature

            # Check for low-frequency categories
            value_counts = df[column].value_counts()
            low_freq_cats = value_counts[value_counts < 10]  # Using 10 as minimum category size
            if not low_freq_cats.empty:
                print(f'\nWARNING: Found {len(low_freq_cats)} categories with fewer than 10 instances:')
                print(low_freq_cats)
                print('Consider grouping rare categories before encoding.')

                user_proceed = input('Do you want to proceed with encoding despite the presence of '
                                     'low-frequency categories? (Y/N): ')
                if user_proceed.lower() != 'y':
                    print(f'Skipping encoding for feature "{column}" due to presence of low-frequency categories.')
                    continue  # Move to next feature

            # Display warning if the unique value count is too high
            if unique_cnt > 20:
                print(f'\nWARNING: Feature "{column}" contains more than 20 unique values.')
                print('Consider using remapping or other dimensionality reduction techniques instead of encoding.')
                print('Encoding high-cardinality features can create the curse of dimensionality.')
                print('It can also result in having overly-sparse data in your feature set.')

                # Ask if user wants to proceed despite this warning
                user_proceed = input(f'\nDo you still want to encode "{column}" despite this warning? (Y/N): ')
                if user_proceed.lower() != 'y':  # If not
                    print(f'Skipping encoding for high-cardinality feature "{column}".')  # Note the choice
                    continue  # And move to the next feature

            # Display (do not log) unique values
            print(f'\nUnique values (alphabetized) for {column}:')
            unique_vals = df[column].unique()

            # Filter out None and NaN values for sorting
            non_null_vals = [value for value in unique_vals if pd.notna(value)]
            sorted_vals = sorted(non_null_vals)

            # Add None/NaN values back if they existed in the original data
            if df[column].isnull().any():
                sorted_vals.append(None)

            for value in sorted_vals:
                if pd.isna(value):
                    print(f'- Missing/NaN')
                else:
                    print(f'- {value}')

            # Display (do not log) value counts
            print(f'\nValue counts for {column}:')
            print(df[column].value_counts())

            # Ask if user wants to see a distribution plot
            user_show_plot = input('\nWould you like to see a plot of the feature distribution? (Y/N): ')
            if user_show_plot.lower() == 'y':  # If so, send call to Seaborn
                # Attempt plot creation
                try:
                    plt.figure(figsize=(12, 8))
                    value_counts = df[column].value_counts()
                    plt.bar(range(len(value_counts)), value_counts.values)
                    plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
                    plt.title(f'Distribution of {column}')
                    plt.xlabel(column)
                    plt.ylabel('Count')
                    plt.tight_layout()
                    plt.show()
                    plt.close()  # Explicitly close the figure

                # Catch plotting errors
                except Exception as plot_exc:
                    print(f'Error creating plot: {plot_exc}')
                    print('Unable to display plot. Continuing with analysis.')
                    if plt.get_fignums():  # If any figures are open
                        plt.close('all')  # Close all figures

            # Ask user to select encoding method
            while True:  # We can justify 'while True' because we have a cancel-out input option
                try:
                    print(f'\nSelect encoding method for feature {column}:')
                    print('1. One-Hot Encoding')
                    print('2. Dummy Encoding')
                    print('3. Skip encoding for this feature')
                    enc_method = input('Enter your choice (1, 2, or 3): ')

                    if enc_method == '3':  # If user wants to skip
                        print(f'Skipping encoding for feature {column}.')  # Note that choice
                        break  # Exit the while loop

                    elif enc_method in ['1', '2']:  # If a valid encoding choice is made

                        if enc_method == '1':  # Perform one-hot encoding
                            # Create binary columns for each unique value in the feature
                            encoded = pd.get_dummies(df[column], prefix=column, prefix_sep='_')

                            # Store encoded DataFrame for later use
                            encoded_dfs.append(encoded)

                            # Store original column name to allow dropping of all original columns at once
                            columns_to_drop.append(column)

                            # Track this column for reporting purposes
                            encoded_cols.append(f'{column} (One-Hot)')

                            # Note the action
                            print(f'Applied one-hot encoding to feature {column}.')

                        else:  # If enc_method is '2', perform dummy encoding
                            # Create n-1 binary columns, dropping first category as reference
                            encoded = pd.get_dummies(df[column], prefix=column, prefix_sep='_', drop_first=True)

                            # Store encoded DataFrame for later use
                            encoded_dfs.append(encoded)

                            # Store original column name to drop all original columns at once later
                            columns_to_drop.append(column)

                            # Track this column for reporting purposes
                            encoded_cols.append(f'{column} (Dummy)')

                            # Note the action
                            print(f'Applied dummy encoding to feature {column}.')

                        break  # Exit the while loop

                    else:  # Catch invalid input
                        print('Invalid input. Please enter 1, 2, or 3.')
                        continue  # Restart the while loop

                # Catch other errors
                except Exception as exc:
                    print(f'Error during encoding of feature {column}: {exc}')
                    print('An error occurred. Skipping encoding for this feature.')
                    break  # Exit the while loop

        # Perform single concatenation if any encodings were done
        if encoded_dfs:
            df = df.drop(columns=columns_to_drop)
            df = pd.concat([df] + encoded_dfs, axis=1)

        # After all features are processed, log a summary of encoding results
        # If any features were encoded, log the encoded features
        if encoded_cols:
            print('-' * 50)  # Visual separator
            print('The following features were encoded:')
            for column in encoded_cols:
                print(f'- {column}')

        # If no features were encoded, log that fact
        else:
            print('No features were encoded.')

    def handle_ords():
        """This internal helper function facilitates the remapping of ordinal features, if desired by the user."""
        nonlocal df  # Specify that this object comes from the outer scope

        if not ord_features:  # If no columns are tagged as ordinal
            print('No ordinal features to process. Skipping remapping.')  # Note this
            return  # And exit the process

        print('-' * 50)  # Visual separator
        print(f'The dataset contains {len(ord_features)} ordinal feature(s).')

        # Create list to track which features get remapped for final reporting
        remapped_cols = []

        # Create list of string-type ordinal features using Pandas' data-type methods
        str_ords = [column for column in ord_features if not pd.api.types.is_numeric_dtype(df[column])]

        # If all ordinal features are already numerical, they don't need remapping
        if not str_ords:  # If there are no string-type ordinal features
            print('All ordinal features are already in a numerical format.')  # Note that fact

            # Print (do not log) a notification/explanation for the user
            print('\nNOTE: Ordinal features in numerical form do not need to be scaled.')
            print('Scaling ordinal features distorts the meaningful distances between values.')
            print('Skipping remapping of ordinal features.')  # Log the auto-skip for the entire process
            return  # Return the unmodified data

        # If there are string-type ordinal features, ask if user wants to remap them with numerical values
        print(f'{len(str_ords)} ordinal feature(s) contain non-numeric values.')
        print('NOTE: Ordinal features should be expressed numerically to allow for proper analysis.')
        user_remap = input('\nDo you want to consider remapping any string-type ordinal features with '
                           'appropriate numerical values? (Y/N): ')
        if user_remap.lower() != 'y':  # If not
            print('Skipping numerical remapping of ordinal features.')  # Log the choice
            return  # Return the unmodified data

        # Process each string-type ordinal feature
        for column in str_ords:
            print(f'\nProcessing string-type ordinal feature: "{column}"')

            # Ask if user wants to remap this specific feature
            user_remap_feature = input(f'Do you want to remap "{column}" with numerical values? (Y/N): ')
            if user_remap_feature.lower() != 'y':  # If not
                print(f'Skipping remapping for feature: "{column}"')  # Note the choice
                continue  # Move to next feature

            # Check for nulls before proceeding
            null_cnt = df[column].isnull().sum()
            # If nulls are present, ask if user wants to proceed
            if null_cnt > 0:
                print(f'Feature "{column}" contains {null_cnt} null values.')
                user_proceed = input('Do you still want to proceed with remapping this feature? (Y/N): ')
                if user_proceed.lower() != 'y':  # If not
                    print(f'Skipping remapping for feature: "{column}"')
                    continue  # Move on to the next feature

            # Validate unique values
            unique_vals = sorted(df[column].unique())
            if len(unique_vals) < 2:
                print(f'Feature "{column}" has only 1 unique value. Skipping remapping.')
                continue

            # Display the feature's current unique values
            print(f'\nCurrent unique values in "{column}" (alphabetized):')
            for value in unique_vals:
                print(f'- {value}')

            while True:  # We can justify 'while True' because we have a cancel-out input option
                try:
                    print('\nProvide comma-separated numbers to represent the ordinal order of these values.')
                    print('Example: For [High, Low, Medium], you might enter: 2,0,1')
                    print('Or, for a Likert-type agreement scale [Agree, Disagree, Neither agree nor disagree], '
                          'you might enter: 3,1,2')
                    print('You may also enter "C" to cancel the remapping process for this feature.')

                    user_remap_input = input('\nEnter your mapping values: ')

                    # Check for user cancellation
                    if user_remap_input.lower() == 'c':
                        print(f'Cancelled remapping for feature: "{column}"')
                        break

                    # Convert user remapping input to a list of integers
                    new_vals = [int(x.strip()) for x in user_remap_input.split(',')]

                    # Validate that the user input length matches the number of categories
                    if len(new_vals) != len(unique_vals):
                        raise ValueError('Number of mapping values must match number of categories.')

                    mapping = dict(zip(unique_vals, new_vals))  # Build a mapping dictionary

                    # Display the proposed remapping
                    print('\nProposed mapping:')
                    for old_val, new_val in mapping.items():
                        print(f'- {old_val} → {new_val}')

                    # Ask for user confirmation
                    user_confirm = input('\nDo you want to apply this mapping? (Y/N): ')
                    if user_confirm.lower() == 'y':
                        df[column] = df[column].map(mapping)  # Apply the mapping

                        # Add the feature to the list of remapped features
                        remapped_cols.append(column)

                        # Note the remapping
                        print(f'Successfully remapped ordinal feature: {column}')

                        break  # Exit the while loop

                    # Otherwise, restart the remapping attempt
                    else:
                        print('Remapping cancelled. Please try again.')
                        continue

                # Catch input errors
                except ValueError as exc:
                    print(f'Invalid input: {exc}')
                    print('Please try again or enter "C" to cancel.')
                    continue  # Restart the loop

                # Catch all other errors
                except Exception as exc:
                    print(f'Error during remapping of feature {column}: {exc}')  # Log the error
                    print('An error occurred. Skipping remapping for this feature.')
                    break  # Exit the loop

        # After all features are processed, log a summary of remapping results
        # If any features were remapped, log the encoded features
        if remapped_cols:
            print('The following ordinal feature(s) were remapped to numerical values:')
            for column in remapped_cols:
                print(f'- {column}')

        # If no features were remapped, log that fact
        else:
            print('No ordinal features were remapped.')

    def handle_nums():
        """This internal helper function facilitates the scaling of numerical features, if desired by the user."""
        nonlocal df  # Specify that this object comes from the outer scope

        if not num_features:  # If no columns are tagged as numerical
            print('No numerical features to process. Skipping scaling.')  # Note this
            return  # Exit the process

        print('-' * 50)  # Visual separator
        print(f'The dataset contains {len(num_features)} non-target numerical feature(s).')

        # Create list to track which features get scaled for final reporting
        scaled_cols = []

        # Print warning that TADPREP only supports common scaling methods
        print('\nWARNING: TADPREP supports only the Standard, Robust, and MinMax scalers.')
        print('For more sophisticated methods (e.g. Quantile or PowerTrans methods), skip this step and write '
              'your own scaler code.')
        # Ask if the user wants to scale any numerical features
        user_scale = input('Do you want to scale any numerical features? (Y/N): ')
        if user_scale.lower() != 'y':
            print('Skipping scaling of numerical features.')
            return  # Exit the process

        # Ask if user wants a refresher on the three scaling methods
        user_scale_refresh = input('Do you want to see a brief refresher on TADPREP-supported scalers? (Y/N): ')
        if user_scale_refresh.lower() == 'y':  # If so, display refresher
            print('\nOverview of the Standard, Robust, and MinMax Scalers:'
                  '\nStandard Scaler (Z-score normalization):'
                  '\n- Transforms features to have zero mean and unit variance.'
                  '\n- Best choice for comparing measurements in different units (e.g., combining age, income, '
                  'and test scores).'
                  '\n- Good for methods that assume normally distributed data like linear regression.'
                  '\n- Not ideal when data has many extreme values or outliers.'
                  '\n'
                  '\nRobust Scaler (Uses median and IQR):'
                  '\n- Scales using statistics that are resistant to extreme values.'
                  '\n- Great for data where outliers are meaningful (e.g., rare but important market events).'
                  '\n- Useful for survey data where some respondents give extreme ratings.'
                  '\n- A good choice when you can\'t simply remove outliers because they contain important information.'
                  '\n'
                  '\nMinMax Scaler (scales to 0-1 range):'
                  '\n- Scales all values to a fixed range between 0 and 1.'
                  '\n- Good for image pixel data or whenever features must be strictly positive.'
                  '\n- Good for visualization and neural networks that expect bounded inputs.'
                  '\n- Works well with sparse data (data with many zeros or nulls).')

        # For each numerical feature
        for column in num_features:
            print(f'\nProcessing numerical feature: "{column}"')

            # Ask if user wants to scale this feature
            user_scale_feature = input(f'Do you want to scale "{column}"? (Y/N): ')
            if user_scale_feature.lower() != 'y':
                print(f'Skipping scaling for feature: "{column}"')
                continue  # Move to the next feature

            # Validate feature before scaling
            try:
                # Check for nulls
                null_cnt = df[column].isnull().sum()
                # If nulls are present, ask if user wants to proceed
                if null_cnt > 0:
                    print(f'Feature "{column}" contains {null_cnt} null value(s).')
                    user_proceed = input('Do you still want to proceed with scaling this feature? (Y/N): ')
                    if user_proceed.lower() != 'y':
                        print(f'Skipping scaling for feature: "{column}"')
                        continue  # Move on to the next feature

                # Check for infinite values
                inf_cnt = np.isinf(df[column]).sum()
                # If infinite values are present, ask if user wants to proceed
                if inf_cnt > 0:
                    print(f'Feature "{column}" contains {inf_cnt} infinite values.')
                    user_proceed = input('Do you want still to proceed with scaling this feature? (Y/N): ')
                    if user_proceed.lower() != 'y':
                        print(f'Skipping scaling for feature: "{column}"')
                        continue  # Move on to the next feature

                # Check for constant/near-constant features, e.g. with only 1 unique value or minimal variance
                if df[column].nunique() <= 1:
                    # Log a warning
                    print(f'Feature "{column}" has no meaningful variance. Consider dropping this feature.')
                    continue  # Move on to the next feature

                # Check for extreme skewness in the feature
                skewness = df[column].skew()  # Calculate skew
                if abs(skewness) > 2:  # Using 2 as threshold for extreme skewness
                    # If skewness is extreme, log a warning and ask if user wants to proceed
                    print(f'Feature "{column}" is highly skewed (skewness={skewness:.2f}). '
                          'Consider transforming this feature before scaling.')

                    user_proceed = input('Do you want still to proceed with scaling this feature? (Y/N): ')
                    if user_proceed.lower() != 'y':
                        print(f'Skipping scaling for feature: "{column}"')
                        continue  # Move on to the next feature

            # Catch validation errors
            except Exception as exc:
                print(f'Error validating feature "{column}": {exc}')
                print('Skipping scaling for this feature.')
                continue  # Move to next feature

            # Print descriptive statistics for the feature
            print(f'\nDescriptive statistics for {column}:')
            print(df[column].describe())

            # Ask if user wants to see a distribution plot for the feature
            user_show_plot = input('\nWould you like to see a histogram of the feature distribution? (Y/N): ')
            if user_show_plot.lower() == 'y':  # If so, send call to Seaborn
                # Attempt plot creation
                try:
                    plt.figure(figsize=(12, 8))
                    sns.histplot(data=df, x=column)
                    plt.title(f'Distribution of {column}')
                    plt.tight_layout()
                    plt.show()
                    plt.close()  # Explicitly close the figure

                # Catch plotting errors
                except Exception as plot_exc:
                    print(f'Error creating plot: {plot_exc}')
                    print('Unable to display plot. Continuing with analysis.')
                    if plt.get_fignums():  # If any figures are open
                        plt.close('all')  # Close all figures

            # Ask user to select a scaling method
            while True:  # We can justify 'while True' because we have a cancel-out input option
                try:
                    print(f'\nSelect scaling method for feature {column}:')
                    print('1. Standard Scaler (Z-score normalization)')
                    print('2. Robust Scaler (uses median and IQR)')
                    print('3. MinMax Scaler (scales to 0-1 range)')
                    print('4. Skip scaling for this feature')
                    scale_method = input('Enter your choice: ')

                    if scale_method == '4':  # If user wants to skip
                        print(f'Skipping scaling for feature: {column}')
                        break  # Exit the while loop

                    elif scale_method in ['1', '2', '3']:  # If a valid scaling choice is made
                        # Reshape the data for use by scikit-learn
                        reshaped_data = df[column].values.reshape(-1, 1)

                        # Instantiate selected scaler and set scaler name
                        if scale_method == '1':
                            scaler = StandardScaler()
                            method_name = 'Standard'
                        elif scale_method == '2':
                            scaler = RobustScaler()
                            method_name = 'Robust'
                        else:  # At this point, scale_method selection must be '3'
                            scaler = MinMaxScaler()
                            method_name = 'MinMax'

                        # Perform scaling and replace original values
                        df[column] = scaler.fit_transform(reshaped_data)

                        # Add the feature to the list of scaled features
                        scaled_cols.append(f'{column} ({method_name})')

                        print(f'Applied {method_name} scaling to feature {column}.')  # Note the scaling action
                        print('-' * 50)  # Visual separator
                        break  # Exit the while loop

                    else:  # If an invalid choice was entered
                        print('Invalid input. Please enter 1, 2, 3, or 4.')
                        continue  # Restart the while loop

                # Catch all other errors
                except Exception as exc:
                    print(f'Error during scaling of feature "{column}": {exc}')  # Log the error
                    print('An error occurred. Skipping scaling for this feature.')
                    break  # Exit the while loop

        # After all features are processed, log a summary of scaling results
        if scaled_cols:
            print('-' * 50)  # Visual separator
            print('The following feature(s) were scaled:')
            for col in scaled_cols:
                print(f'- {col}')
            print('-' * 50)  # Visual separator

        # If no features were scaled, log that fact
        else:
            print('-' * 50)  # Visual separator
            print('No features were scaled.')
            print('-' * 50)  # Visual separator

    # Call the three helper functions in sequence
    handle_cats()  # Encode categorical features
    handle_ords()  # Transform and remap ordinal features
    handle_nums()  # Scale numerical features

    # Return the final dataset with encoded and scaled features
    return df
