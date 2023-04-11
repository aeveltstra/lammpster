#!/usr/bin/env python3
"""
# Easily publish LAMMP registrations as posters for publication
# on social media and phystical printing.
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.1018.2130
#
"""

import datetime
# import json
import os
import sys
from configparser import ConfigParser, NoOptionError
from functools import partial
from string import Template
from typing import Any, List, Union, Optional
from urllib.error import URLError
import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from cairosvg import svg2png, svg2pdf


def list_headers() -> List[str]:
    """
    List the headers in the spread sheet / database.
    List them in the same order as they appear.
    In case of a spread sheet, they appear as column headers
    next to each other. In case of many a database table
    layout, they appear as row headers underneath each other.
    """

    # we need an empty 0 header. if we don't supply one,
    # the spreadsheet won't find the 1st column.
    return [
        "",
        "Case ID",
        "Created At",
        "Created By",
        "Last Modified At",
        "Last Modified By",
        "Case Status",
        "Poster Generated At",
        "Given Name",
        "Chosen Name",
        "Aliases",
        "Birth Year",
        "Birth Year Accuracy",
        "Last Seen Date",
        "Last Seen Date Accuracy",
        "Last Seen Location",
        "Last Seen Wearing",
        "Last Seen Activity",
        "Who to Contact If Found",
        "Image Path",
        "Image Path 2",
        "Disappearance Circumstances",
        "Eyes",
        "Hair",
        "Height",
        "Identifying Features",
        "Other Notes",
        "Pronouns",
        "Race",
        "Weight",
    ]


def get_cell_value_for_header(
    page,
    row_index: int,
    header: str
) -> Union[str, None]:
    """
    Retrieve the value of the cell specified by row_index
    for the column specified by header.

    Parameters
    ----------
    page: Google Sheets Page, required
        The Google Sheets Page to look in.
    row_index: int, required
        The row in which to look.
    header: str, required
        The caption of the column in which to look.

    Returns
    -------
    str | None
          None if the cell was not found. Otherwise its
          contents as a string. We are not going to
          pretend that sheet data types exist.
    """

    header_index = list_headers().index(header)
    if not header_index:
        return None
    cell = page.cell(row_index, header_index)
    if not cell:
        return None
    return cell.value


def get_current_year() -> int:
    """
    Retrieves the year number of today's date,
    whatever that is at the moment of execution.
    """
    return datetime.date.today().year


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


def create_profile(
    page,
    case_row_index: int
) -> Union[dict[str, Any], None]:
    """
    Takes the cell values from a row, and turns them into a profile
    for injecting into a poster.
    """

    if not page or not case_row_index:
        return None
    get_cells_for_row = partial(get_cell_value_for_header, page)
    get_cell_value = partial(get_cells_for_row, case_row_index)
    birth_year = get_cell_value("Birth Year")
    age = None
    if birth_year:
        age = get_current_year() - int(birth_year)
    return {
        "Age": age,
        "Birth Year": birth_year,
        "Case ID": get_cell_value("Case ID"),
        "Chosen Name": get_cell_value("Chosen Name"),
        "Disappearance Circumstances": get_cell_value(
            "Disappearance Circumstances"
        ),
        "Eyes": get_cell_value("Eyes"),
        "Hair": get_cell_value("Hair"),
        "Height": get_cell_value("Height"),
        "Identifying Features": get_cell_value("Identifying Features"),
        "Image 1 Path": get_cell_value("Image Path"),
        "Image 2 Path": get_cell_value("Image Path 2"),
        "Last Seen Date": get_cell_value("Last Seen Date"),
        "Last Seen Location": get_cell_value("Last Seen Location"),
        "Last Seen Wearing": get_cell_value("Last Seen Wearing"),
        "Other Notes": get_cell_value("Other Notes"),
        "Pronouns": get_cell_value("Pronouns"),
        "Race": get_cell_value("Race"),
        "Weight": get_cell_value("Weight"),
        "Who to Contact If Found": get_cell_value("Who to Contact If Found"),
    }


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


def read_case_id_from_command_line():
    """
    Reads the case id from the command line. Assumes that the 1st
    command-line argument is the case identifier, to be used to
    locate the data for that case in the spreadsheet.
    """

    if len(sys.argv) > 1:
        return sys.argv[1]
    return None


def must_list_sheet_column_names():
    """
    Returns true, if the command-line argument --list-column-names
    was added to the run invocation.
    """

    return "--list-column-names" in sys.argv


def must_list_sheet_page_names():
    """
    Returns true, if the command-line argument --list-sheet-pages
    was added to the run invocation.
    """

    return "--list-sheet-pages" in sys.argv


def must_list_column_values():
    """
    Returns true, if the command-line argument --list-column-values
    was added to the run invocation.
    """

    return "--list-column-values" in sys.argv


def list_values_for_which_column():
    """
    Returns the index number of the column that needs to have its
    values listed. This comes from the command-line invocation,
    from the argument following the switch --list-column-values.
    That argument is expected to be a whole number (integer),
    0 (zero) or larger. If it is something else, chances are the
    program will break.
    """

    i = sys.argv.index("--list-column-values")
    if (i + 1) < len(sys.argv):
        return int(sys.argv[i + 1])
    return None


def apply_profile_to_template(profile, template_contents) -> str:
    """
    Substitutes known variables in the template contents
    with values from the profile. This will fail if expected
    variables do not exist in the template contents.

    Parameters
    ----------
    - profile: dict, required, with fields expected but not required:
      - Chosen Name,
      - Age,
      - Race,
      - Height,
      - Weight,
      - Eyes,
      - Hair,
      - Pronouns,
      - Last Seen Date,
      - Last Seen Location,
      - Last Seen Wearing,
      - Identifying Features,
      - Disappearance Circumstances,
      - Who to Contact If Found,
      - Image Path,
      - Image Path 2,
      - Other Notes

    - template_contents: str, required, with these required variables:
      - name,
      - age,
      - race,
      - height,
      - weight,
      - eyes,
      - hair,
      - pronouns,
      - last_seen_on,
      - last_seen_where,
      - last_seen_wearing,
      - identifying_features,
      - disappearance_circumstances,
      - contact_if_found,
      - image_path_1,
      - image_path_2,
      - other_notes

    Returns
    -------
    str: The substitution result.
    """

    if not profile or not template_contents:
        return None

    try:
        result = Template(template_contents).substitute(
            name=profile.get("Chosen Name", ""),
            age=profile.get("Age", ""),
            race=profile.get("Race", ""),
            height=profile.get("Height", ""),
            weight=profile.get("Weight", ""),
            eyes=profile.get("Eyes", ""),
            hair=profile.get("Hair", ""),
            pronouns=profile.get("Pronouns", ""),
            last_seen_on=profile.get("Last Seen Date", ""),
            last_seen_where=profile.get("Last Seen Location", ""),
            last_seen_wearing=profile.get("Last Seen Wearing", ""),
            identifying_features=profile.get("Identifying Features", ""),
            disappearance_circumstances=profile.get(
                "Disappearance Circumstances",
                ""
            ),
            contact_if_found=profile.get("Who to Contact If Found", ""),
            image_path_1=profile.get(
                "Image Path", "templates/transparent-1020x1024.png"
            ),
            image_path_2=profile.get(
                "Image Path 2", "templates/transparent-1020x1024.png"
            ),
            other_notes=profile.get("Other Notes", ""),
        )
        return result
    except KeyError as err:
        msg = (
            "Error: failed to apply profile. "
            "Either the placeholder was not found, "
            f"or it was not given a substitute: {err}."
        )
        print(msg)
        raise


def create_poster(
    profile,
    channel,
    template_path,
    output_folder,
    file_prefix=""
) -> None:
    """
    Creates the poster. Writes the result out to the specified output
    folder. The file name will start with the file prefix, followed by
    the case id, the string literal '-poster-', the channel, and eah
    of the string literals '.svg', '.pdf', and '.png'.

    Parameters
    ----------
    - profile: dict, required. Should come from the function
      create_profile().
    - channel: str, required. The name of a known channel. Will be used
      to name the output file. Channels are identified in the
      configuration file.
    - template_path: str, required. The file location of the template
      to be converted into a poster.
    - output_folder: str, required. The folder to which new posters
      need to get written.
    - file_prefix: str, optional. Will be used in naming the poster
      files that get written, as the first part of the file name.

    Returns
    -------
    None
    """

    if (
        not profile
        or not channel
        or not template_path
        or not output_folder
    ):
        return None
    prefix = output_folder + file_prefix
    case_id = profile.get("Case ID")

    print(f"Creating poster for case {case_id}, for channel {channel}...")

    svg_poster = None
    try:
        with open(template_path, "r", encoding="utf-8") as template:
            svg_poster = apply_profile_to_template(
                             profile,
                             template.read()
                         )
    except FileNotFoundError:
        msg = (
            f"For channel {channel} no template was found "
            f"named {template_path}."
        )
        print(msg)
        return None

    if not svg_poster:
        print("Failed to create poster contents.")
        return None

    file_path = f"{prefix}{case_id}-poster-{channel}.svg"
    print(f"Saving SVG poster to {file_path}...")
    with open(file_path, "w", encoding="utf-8") as output_file:
        output_file.write(svg_poster)
        output_file.close()
    file_path = f"{prefix}{case_id}-poster-{channel}.png"
    print(f"Saving PNG poster to {file_path}...")
    try:
        svg2png(bytestring=svg_poster, write_to=file_path)
    except URLError as err:
        print(f"Error: file not found: {err}.")
    except FileNotFoundError as err:
        print(f"Error: file not found: {err}.")
    file_path = f"{prefix}{case_id}-poster-{channel}.pdf"
    print(f"Saving PDF poster to {file_path}...")
    try:
        svg2pdf(bytestring=svg_poster, write_to=file_path)
    except URLError as err:
        print(f"Error: file not found: {err}.")
    except FileNotFoundError as err:
        print(f"Error: file not found: {err}.")
    return None


def maybe_get_config_section_items(
    config: ConfigParser, section_name: str, default: Optional[dict] = None
) -> Union[dict, None]:
    """
    Reads items from sections of the configuration file and returns them
    as a dict. Used for instance, to turn the listing of channels into
    an enumeration.

    Parameters
    ----------
    - config: ConfigParser, required
        The thing that can parse the configuration file.
    - section_name: str, required
        Identifies which section of the configuration file to read.
    - default: dict, optional
        Something to return in case the section name or entire
        configuration file cannot be found.

    Returns
    -------
    A dict containing the keys and values of a configuration section.

    """

    result = None

    try:
        result = config.items(section_name)
        return dict(result)

    except (KeyError, NoOptionError):
        if default:
            msg = (
                f"Info: found no configuration section {section_name}."
                f" Defaulting to {default}."
            )
            print(msg)
            result = default
        else:
            msg = (
                f"Warning: found no configuration section {section_name}."
                " No default was provided."
            )
            print(msg)
            result = None

    return result


def maybe_get_config_entry(
    config: ConfigParser,
    section_name: str,
    entry_name: str,
    default: Optional[str] = None,
) -> Union[str, None]:
    """
    Hopes to retrieve a value from the configuration file, identified
    by the section name and entry name. If no such entry was found,
    the default value is returned.
    """

    result = None

    try:
        result = config.get(section_name, entry_name)

    except (KeyError, NoOptionError):
        if default:
            msg = (
                f"Info: found no entry {entry_name} in configuration "
                f"section {section_name}. Defaulting to {default}."
            )
            print(msg)
            result = default
        else:
            msg = (
                f"Warning: found no entry {entry_name} in configuration "
                f"section {section_name}. No default was provided."
            )
            print(msg)
            result = None

    return result


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

    page_name = maybe_get_config_entry(config, "sheet", "page_name")
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

    sheet_id = maybe_get_config_entry(config, "sheet", "google_drive_sheet_id")
    keys_file = maybe_get_config_entry(config, "account", "keys_file")
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


def run_on_demand_functions(
    config,
    sheet,
    page
):
    """
    Runs the functions that are requested by the command-line
    arguments during the run invocation. See the readme file for
    documentation of the command-line switches.
    """

    if must_list_sheet_page_names():
        print("All page names in the spread sheet:")
        print(get_page_names(sheet))
        sys.exit()

    if must_list_sheet_column_names():
        print("All column names in page:")
        page_column_names_row = maybe_get_config_entry(
            config, "sheet", "page_column_names_row", "0"
        )
        columns = get_page_column_names(page, int(page_column_names_row))
        print(columns)
        sys.exit()

    if must_list_column_values():
        column_index = list_values_for_which_column()
        if not column_index:
            msg = (
                "Specify the column index of which to list the "
                "values. First column has index 1."
            )
            sys.exit(msg)
        elif 1 > column_index:
            msg = (
                "Column index must be larger than 0. "
                "First column has index 1."
            )
            sys.exit(msg)

        msg = (
            "All column values in column "
            "{str(column_index)} of page:"
        )
        print(msg)
        cells = get_column_values(page, column_index)
        print(cells)
        sys.exit()


def main() -> None:
    """
    Main entry point of the program. Checks the environment, reads
    the configuration, uses that to contact the spreadsheet which
    contains the database, attempts to connect to it, and then
    attempts to execute the functions asked for by the command-line
    switches. The default function is to generate the posters.
    Consult the readme documentation to see what command-line options
    are available.
    """

    if not os.path.exists("./.config"):
        msg = (
            "Expected configuration file '.config' was not found. "
            "Please consult the documentation."
        )
        sys.exit(msg)
    else:
        print("Retrieving configuration...")

    config = ConfigParser()
    config.read("./.config")
    maybe_sheet = get_configured_sheet(config)
    if isinstance(maybe_sheet, KeyError):
        sys.exit(maybe_sheet)

    maybe_page = get_sheet_page(config, maybe_sheet)
    if isinstance(maybe_page, KeyError):
        sys.exit(maybe_page)

    run_on_demand_functions(config, maybe_sheet, maybe_page)

    case_id = read_case_id_from_command_line()
    if not case_id:
        msg = """Error: missing case identifier.
  Specify the identity of the case/profile to print.
  Place it as the first argument of the application
  run invocation, like so:
  $ python3 ./lammpster.py abc1234
  To find out what case identifiers exist, use the
  command-line switch --list-column-values i,
  in which you substitute i for the column that
  holds the case identifiers, like so:
  $ python3 ./lammpster.py --list-column-values 1"""
        sys.exit(msg)
    else:
        msg = (
            "Lammpster will create posters for the profile based "
            f"on row {case_id}..."
        )
        print(msg)

        case_row_index = find_row_index(maybe_page, case_id)
        if not case_row_index:
            msg = (
                f"Error: No case found with id {case_id}. Use the "
                "command-line switch --list-column-values to find "
                "existing case identifiers."
            )
            sys.exit(msg)

        print(f"Found case with id {case_id}. Creating profile...")
        profile = create_profile(maybe_page, case_row_index)

        output_folder = maybe_get_config_entry(
            config,
            "output",
            "folder",
            "~/"
        )
        output_file_prefix = maybe_get_config_entry(
            config,
            "output",
            "file_prefix",
            ""
        )

        poster_choices = maybe_get_config_section_items(
             config,
             "posters",
             {}
        )
        if not poster_choices:
            raise Exception(
               "Error: missing posters configuration. Check the manual."
            )

        print("Profile created.")
        print("Generating and saving posters....")
        for channel, template in poster_choices.items():
            create_poster(
                profile,
                channel,
                template,
                output_folder,
                output_file_prefix
            )

        print("Done. Check the folder for new posters.")
        sys.exit()


# Normally, python will execute any script statements not
# part of a function, upon reading it.
# That also happens when using mypy or pydoc. But it should
# be skipped in those cases.
# Thus, the following makes sure the main() function gets
# executed only when python calls this script directly.
if __name__ == "__main__":
    main()
