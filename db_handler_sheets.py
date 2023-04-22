"""
# Connects to Google Sheets as a data store.
# Used as part of Lammpster.
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.420.2300
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
    page,
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


def get_sheet(keys_file: str, sheet_id: str):
    """
    Finds and returns a Google Sheet based on its ID and
    the credentials to access it, as specified in keys_file.

    Parameters
    ----------
    keys_file: str, required
        File path that specifies in which file the keys are
        stored, that give access to the Google Sheet that is
        specified in sheet_id. Check the gspread docs to see
        what format it must have and how to obtain them.
    sheet_id: str, required
        An identity for the Google Sheet as provided by Google.
        When you open the sheet in your web browser, its ID is
        shown as the weird code with numbers and letters in the
        address bar.

    Returns
    -------
    sheet | KeyError
        KeyError, if the gspread module was unable to retrieve a
        service account based on the provided keys file
        or if the passed-in sheet_id does not lead to an
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
    if not sheet_id:
        return KeyError(
            "Please set the identity of the sheet to read in config."
        )
    client = gspread.service_account(keys_file)
    if not client:
        return KeyError(
            "Failed to create a client to talk to Google Sheets."
        )
    maybe_sheet = client.open_by_key(sheet_id)
    if not maybe_sheet:
        return KeyError(
            "Failed to open the requested Google Sheet."
        )
    return maybe_sheet


def get_page_names(sheet) -> List[str]:
    """
    Gets all names of the pages found in the sheet.

    Parameters
    ----------
    - sheet: required
        The Google Worksheet that contains the
        pages of which the names must be returned.

    Returns
    -------
    page names: a list of strings. May be empty.

    Exceptions
    ----------
    - When no sheet was provided.
    - When sheet is not a Google Worksheet.

    """

    pages = sheet.worksheets()
    titles = [page.title for page in pages]
    return titles


def get_page(sheet, page_name: str):
    """
    Finds and returns a named page in
    a Google Worksheet.

    Parameters
    ----------
    - sheet : Google Worksheet, required
        The source that contains the page
        to return.
    - page_name : str, required
        The name of the page to find in the
        passed-in sheet.

    Returns
    -------
    page
        The found Google Worksheet Page.
        May be None.

    Exceptions
    ----------
    - When sheet is not a Google Worksheet.
    - When no page was located that bears
      the passed-in page_name.
    """

    return sheet.worksheet(page_name)


def get_page_column_names(page, row_index: int) -> Union[List[str], None]:
    """
    Finds all the column names of a spreadsheet page.
    Column names are assumed to be the values found in the cells of the
    row indicated by the row_index, in the order of appearance from
    low (left) to high (right).
    """

    if not page:
        return None
    cells = page.row_values(row_index)
    if not cells:
        return None
    return cells


def get_column_values(page, column_index: int) -> Union[List[str], None]:
    """
    Finds the contents of all the cells in the given page, that are
    part of the column indicated by the column_index, in the order
    of appearance from low (top) to high (bottom).
    """

    if not page:
        return None
    if 0 == column_index:
        return None
    cells = page.col_values(column_index)
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


def get_sheet_page(config, sheet):
    """
    Attempts to retrieve the page within the sheet, that is identified
    by the configuration file.

    Parameters
    ----------
    - config: ConfigParser, required. The configuration file parser,
      with the configuration file already loaded.

    Returns
    -------
    Either a KeyError, or a Google Sheet page.
    """

    page_name = config_handler.maybe_get_config_entry(
        config,
        "sheet",
        "page_name"
    )
    if not page_name:
        msg = (
            "Aborting. Missing configuration key: "
            "'page_name'. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    maybe_page = get_page(sheet, page_name)
    if not maybe_page:
        msg = (
            f"Spreadsheet has no page named {page_name}. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    return maybe_page


def get_configured_sheet(config):
    """
    Attempts to connect to the spreadsheet,
    as configured by the configuration file.

    Parameters
    ----------
    - config: ConfigParser, required. The configuration file parser,
      with the configuration file already loaded.

    Returns
    -------
    Either a KeyError, or a Google Sheet sheet.
    """

    sheet_id = config_handler.maybe_get_config_entry(
        config,
        "sheet",
        "google_drive_sheet_id"
    )
    keys_file = config_handler.maybe_get_config_entry(
        config,
        "account",
        "keys_file"
    )
    if not sheet_id or not keys_file:
        msg = (
            "Aborting. Missing 1 or more configuration keys: "
            "'google_drive_sheet_id' or 'keys_file'. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    maybe_sheet = get_sheet(keys_file, sheet_id)
    if not maybe_sheet:
        msg = (
            "Aborting. No sheet found with identity {sheet_id}. "
            "Read the manual about setting up the configuration file."
        )
        return KeyError(msg)
    return maybe_sheet
