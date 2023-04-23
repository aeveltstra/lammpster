"""
# Unit tester for LAMMPster.
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.420.2300
#
"""

from typing import Union
import db_handler_sheets
import config_handler
import profile_maker
import gspread


def test_configured_db_is_spreadsheet(config):
    maybe_db = db_handler_sheets.maybe_get_configured_db(
        config
    )
    return isinstance(maybe_db, gspread.spreadsheet.Spreadsheet)


def test_db_store_is_worksheet(config):
    db_store = db_handler_sheets.get_db_store(
        config,
        db_handler_sheets.maybe_get_configured_db(
            config
        )
    )
    return isinstance(db_store, gspread.worksheet.Worksheet)


def test_can_read_profile_mapping(config):
    profile_mapping = config_handler.maybe_get_config_section_items(
        config,
        "profile_map",
        {}
    )
    return (
        profile_mapping is not None
        and 'case_id' in profile_mapping.keys()
        and profile_mapping['case_id'] == "Case ID"
    )


def test_can_create_profile(config):
    db_store = db_handler_sheets.get_db_store(
        config,
        db_handler_sheets.maybe_get_configured_db(
            config
        )
    )
    # remember that index 1 is the header row
    profile = profile_maker.create(
        config,
        db_store,
        2
    )
    try:
        return (
            profile["case_id"] is not None
            and profile["name"] is not None
            and profile["case_id"] != "Case ID"
            and profile["name"] != "Chosen Name"
        )
    except:
        for k,v in profile.items():
            print(f"profile[{k}] = {v}")
        return False


def test_can_get_expected_fields(config):
    fields = db_handler_sheets.get_expected_fields(config)
    return (
        fields is not None
        and 0 < len(fields)
    )


def test_can_read_store_names(config):
    maybe_db = db_handler_sheets.maybe_get_configured_db(config)
    names = db_handler_sheets.get_store_names(maybe_db)
    return (
        names is not None
        and 0 < len(names)
    )


def test_can_apply_profile_to_template():
    profile = {
        "one": "Einz",
        "two": "Zwo",
        "three": "Drei"
    }
    template = "The road goes $one, $two, $three."
    output = profile_maker.apply_profile_to_template(profile, template)
    return (output == "The road goes Einz, Zwo, Drei.")


def test(config):
    """
    Runs all tests.

    Parameters
    ----------
    - config: ConfigParser, required
       Should be the config parser preloaded with the configuration. 
    """
    results = {
        "test_configured_db_is_spreadsheet": test_configured_db_is_spreadsheet(config),
        "test_db_store_is_worksheet": test_db_store_is_worksheet(config),
        "test_can_read_profile_mapping": test_can_read_profile_mapping(config),
        "test_can_get_expected_fields": test_can_get_expected_fields(config),
        "test_can_read_store_names": test_can_read_store_names(config),
        "test_can_create_profile": test_can_create_profile(config),
        "test_can_apply_profile_to_template":
        test_can_apply_profile_to_template()
    }
    succeeded = True
    fail_count = 0
    test_count = 0
    for k, v in results.items():
        test_count += 1
        if not v:
            succeeded = False
            fail_count += 1
            print(f"Failed test '{k}'.")
    if succeeded:
        print(f"Success! All {test_count} tests passed.")
        print("That's, like 100% success! Awesome!")
    else:
        msg = (
            f"Ah, dude! {fail_count} out of {test_count} tests failed!"
            f" That's, like {round((fail_count/test_count*100))}%!"
            f" That means the success rate is "
            f"{round((test_count - fail_count)/test_count*100)}%."
        )
        print(msg)

