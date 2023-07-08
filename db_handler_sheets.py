"""
# Connects to Google Sheets as a data store.
# Used as part of Lammpster.
#
# Copyright OmegaJunior Consultancy, LLC.
# Since 2021-10-11
# Version 2.23.607.2211
#
"""

import os
from typing import List, Union
import gspread
import config_handler


def get_expected_fields(config) -> List[str]:
    """
    List the headers in the profile data store.
    List them in the same order as they appear.
    In case of a spread sheet, they appear as column headers
    next to each other. In case of many a database table
    layout, they appear as row headers underneath each other.

    Parameters
    ----------
    - config: ConfigParser, required
        Must be preloaded with the local configuration file.
    """
    return [
        field.strip()
        for field in config_handler.maybe_get_config_entry(
            config,
            "profile",
            "fields",
            []
        ).split(',')
    ]


def get_value_for_field_by_name(
    config,
    page: gspread.worksheet.Worksheet,
    row_index: int,
    field_name: str
) -> Union[str, None]:
    """
    Retrieve the value of the cell specified by row_index
    for the column specified by header.

    Parameters
    ----------
    - config: ConfigParser, required
        A config parser with the configuration file preloaded.
    - page: Google Sheets Page, required
        The Google Sheets Page to look in.
    - row_index: int, required
        The row in which to look.
    - field_name: str, required
        The caption of the column in which to look.

    Returns
    -------
    str | None
          None if the cell was not found. Otherwise its
          contents as a string. We are not going to
          pretend that sheet data types exist.
    """

    field_index = get_expected_fields(config).index(field_name)
    if not field_index:
        return None
    field = page.cell(row_index, field_index)
    if not field:
        return None
    return field.value


def get_db(
    keys_file: str,
    db_id: str
) -> gspread.spreadsheet.Spreadsheet:
    """
    Finds and returns a Google Sheet based on its ID and
    the credentials to access it, as specified in keys_file.

    Parameters
    ----------
    - keys_file: str, required
        File path that specifies in which file the keys are
        stored, that give access to the Google Sheet that is
        specified in db_id. Check the gspread docs to see
        what format it must have and how to obtain them.
    - db_id: str, required
        An identity for the Google Sheet as provided by Google.
        When you open the sheet in your web browser, its ID is
        shown as the weird code with numbers and letters in the
        address bar.

    Returns
    -------
    sheet | KeyError
        KeyError, if the gspread module was unable to retrieve a
        service account based on the provided keys file
        or if the passed-in db_id does not lead to an
        existing or accessible Google Sheet.
        Otherwise, the Google Sheet.
    """

    if not keys_file:
        return KeyError(
            "Please set file name for service account in config."
        )
    if not os.path.exists(keys_file):
        msg = (
            "The file name for service account set in the config file, "
            "does not lead to any existing file. Please check. The "
            f"setting points to: {keys_file}."
        )
        return KeyError(msg)
    if not db_id:
        return KeyError(
            "Please set the identity of the sheet to read in config."
        )
    client = gspread.service_account(keys_file)
    if not client:
        return KeyError(
            "Failed to create a client to talk to Google Sheets."
        )
    maybe_db = client.open_by_key(db_id)
    if not maybe_db:
        return KeyError(
            "Failed to open the requested Google Sheet."
        )
    return maybe_db


def get_store_names(db) -> List[str]:
    """
    Gets all names of the stores found in the database.
    For this Google Sheets handler, that is all the Page names 
    found in the passed-in Google Sheet.

    Parameters
    ----------
    - db: required
        The Google Worksheet that contains the Pages of which the 
        names must be returned.

    Returns
    -------
    names: a list of strings. May be empty.

    Exceptions
    ----------
    - When no db was provided.
    - When db is not a Google Sheet.
    """

    pages = db.worksheets()
    return [page.title for page in pages]


def get_store(db, store_name: str) -> gspread.worksheet.Worksheet:
    """
    Finds and returns a named store within the db. For this Google Sheets
    handler, that is a named Page with the Google Sheets sheet.

    Parameters
    ----------
    - db : Google Worksheet, required
        The source that contains the Page to return.
    - store_name : str, required
        The name of the Page to find in the passed-in Sheet.

    Returns
    -------
    page
        The found Google Worksheet Page.  May be None.

    Exceptions
    ----------
    - When db is not a Google Worksheet.
    - When no Page was located that bears the passed-in store_name.
    """

    return db.worksheet(store_name)


def get_column_names(store, row_index: int) -> Union[List[str], None]:
    """
    Finds all the column names of a data store. For this Google Sheets
    handler, column names are assumed to be the values found in the 
    cells of the row indicated by the row_index, in the order of 
    appearance from low (left) to high (right).
    """

    if not store:
        return None
    cells = store.row_values(row_index)
    if not cells:
        return None
    return cells


def get_column_values(store, column_index: int) -> Union[List[str], None]:
    """
    Finds the contents of all the cells in the given page, that are
    part of the column indicated by the column_index, in the order
    of appearance from low (top) to high (bottom).
    """

    if not store:
        return None
    if 0 == column_index:
        return None
    cells = store.col_values(column_index)
    if not cells:
        return None
    return cells


def find_first(predicate, haystack):
    """
    Hopes to find the first item in haystack, that matches predicate.
    """

    return next((i for i in haystack if predicate(i)), None)


def is_first_column(cell):
    """
    Determines whether the passed-in cell is the first in a row.
    """

    return cell.col == 1


def find_row_index(page, case_identifier):
    """
    Attempts to find the row index of the cell that contains the
    passed-in case identifier. You could pass in any value known
    to exist, but you should pass in case identifiers. You do you,
    though.
    """

    if not page or not case_identifier:
        return None
    cells = page.findall(case_identifier)
    if not cells:
        return None
    cell = find_first(is_first_column, cells)
    if not cell:
        return None
    return cell.row


def get_db_store(config, db):
    """
    Attempts to retrieve the data store within the db, that is 
    identified by the configuration file. For a Google Sheets
    handler, that is a Page within a Sheet.

    Parameters
    ----------
    - config: ConfigParser, required. The configuration file parser,
      with the configuration file already loaded.
    - db: the Google Sheet returned from maybe_get_configured_db().

    Returns
    -------
    Either a KeyError, or a Google Sheets Page.
    """

    store_name = config_handler.maybe_get_config_entry(
        config,
        "sheet",
        "page_name"
    )
    if not store_name:
        msg = (
            "Aborting. Missing configuration key: "
            "'page_name'. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    maybe_store = get_store(db, store_name)
    if not maybe_store:
        msg = (
            f"Google Sheet has no Page named {store_name}. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    return maybe_store


def maybe_get_configured_db(config):
    """
    Attempts to connect to the database, as configured by the 
    configuration file. For this Google Sheets handler, that is 
    going to be a Google Sheets Sheet.

    Parameters
    ----------
    - config: ConfigParser, required. The configuration file parser,
      with the configuration file already loaded.

    Returns
    -------
    Either a KeyError, or a Google Sheets Sheet.
    """

    db_id = config_handler.maybe_get_config_entry(
        config,
        "sheet",
        "id"
    )
    keys_file = config_handler.maybe_get_config_entry(
        config,
        "account",
        "keys_file"
    )
    if not db_id or not keys_file:
        msg = (
            "Aborting. Missing 1 or more configuration keys: "
            "'google_drive_sheet_id' or 'keys_file'. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    maybe_db = get_db(keys_file, db_id)
    if not maybe_db:
        msg = (
            "Aborting. No Google Sheet found with identity {db_id}. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    return maybe_db
