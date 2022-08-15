import pandas as pd

def check_item_with_dataframe_equal(item_a, item_b, name, diff, special_types=()):
    result = True
    try:
        if type(item_a) == dict:
            result, diff = check_dict_with_dataframe_equal(item_a, item_b, name, diff, special_types)
        elif type(item_a) == list:
            result, diff = check_list_with_dataframe_equal(item_a, item_b, name, diff, special_types)
        elif isinstance(item_a, (pd.DataFrame, pd.Series)):
            if not item_a.equals(item_b):
                result = False
                if isinstance(item_a, pd.Series):
                    item_a = pd.DataFrame(item_a).reset_index()
                    item_b = pd.DataFrame(item_b).reset_index()
                    
                df_diff = pd.concat([item_a, item_b]).drop_duplicates(keep=False)
                rows = df_diff.index.unique().to_list()
                msg = f"{len(rows)} row(s) not equal:\n"
                row_diffs = []
                for row in rows:
                    for col in df_diff.columns:
                        if True not in df_diff.loc[row, col].duplicated().values:
                            vals = df_diff.loc[row, col].values
                            row_diffs.append(
                                f"    Row: {row}, Col: '{col}' - left: {vals[0]}, right: {vals[1]}"
                            )
                msg += '\n'.join(row_diffs)
                diff.append((name, msg))
        elif isinstance(item_a, special_types):
            # item is a Unit or other fmapi class
           result, new_diff = item_a._get_diff(item_b)
           diff.extend(new_diff)
        else:
            if not item_a == item_b:
                result = False
                diff.append((name, f"{item_a} != {item_b}"))
    except Exception as e:
        result = False
        diff.append((name, f"Error encountered when comparing: {e.args[0]}"))
    
    return result, diff

def check_dict_with_dataframe_equal(dict_a, dict_b, name, diff, special_types):
    """ Used to recursively check equivalence where there may be dataframe objects """
    result = True
    try:
        for key, item in dict_a.items():
            try:
                _result, diff = check_item_with_dataframe_equal(
                    item, dict_b[key], name=F"{name}->{key}", diff=diff, special_types=special_types
                )
                if not _result:
                    result = False
            except KeyError as ke:
                result = False
                diff.append((name, f"Key: '{ke.args[0]}' missing in other"))
                continue

        for key in dict_b.keys():
            if key not in dict_a:
                result = False
                diff.append((name, f"Key: {key} missing from first object"))
    except Exception as e:
        result = False
        diff.append((name, "Error encountered when comparing"))
    
    return result, diff

def check_list_with_dataframe_equal(list_a, list_b, name, diff, special_types):
    result = True
    try:
        for idx, item in enumerate(list_a):
            _result, diff = check_item_with_dataframe_equal(
                item, list_b[idx], name=f"{name}->itm[{idx}]", diff=diff, special_types=special_types)
            if not _result:
                result = False

        if len(list_a) != len(list_b):
            result = False
            diff.append((name, f"Mismatch in list length"))
    except Exception as e:
        result = False
        diff.append((name, "Error encountered when comparing"))

    return result, diff