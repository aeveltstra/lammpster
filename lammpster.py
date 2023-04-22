#!/usr/bin/env python3
"""
# Easily publish LAMMP registrations as posters for publication
# on social media and phystical printing.
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.420.2300
#
"""

import os
import sys
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
import config_handler
import db_handler_sheets
import profile_maker


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
        try:
            return int(sys.argv[i + 1])
        except Exception as _:
            msg = (
                "The value that should identify the column, "
                "of which the values should get returned, "
                "must be a whole number (integer), "
                "larger than 0 (zero). Please correct the "
                "invocation and try again."
            )
            sys.exit(msg)
    return None


def get_webdriver():
    """
    Attempts to obtain a web driver based on any
    web browser installed on the system.
    """
    desired_dpi = 2.0
    try:
        options = webdriver.chrome.options.Options()
        options.add_argument('-headless')
        options.add_argument(
            f"--force-device-scale-factor={desired_dpi}"
        )
        attempt = webdriver.Chrome(options=options)
        if attempt:
            return attempt
    except Exception as _:
        attempt = None
    if not attempt:
        try:
            attempt = webdriver.Safari()
            if attempt:
                return attempt
        except Exception as _:
            attempt = None
    if not attempt:
        try:
            options = webdriver.firefox.options.Options()
            options.add_argument('-headless')
            options.set_preference(
                "layout.css.devPixelsPerPx",
                str(desired_dpi)
            )
            attempt = webdriver.Firefox(options=options)
            if attempt:
                return attempt
        except Exception as _:
            attempt = None
    if not attempt:
        try:
            attempt = webdriver.Edge()
            if attempt:
                return attempt
        except Exception as _:
            attempt = None
    return None


def transform_svg_2_pdf(svg_browser_element, out_pdf_path):
    """
    Turns the input SVG file into a PDF file and writes it
    to the output path.

    Parameters
    ----------
    svg_browser_element: required
        the result of load_svg_in_browser(path)
    out_pdf_path: str, required
        the path to which the PDF file needs to get written

    Returns
    -------
    The same SVG browser element as passed in.
    """

    png = svg_browser_element.screenshot_as_png
    img = Image.open(BytesIO(png))
    img.save(out_pdf_path, "PDF", quality=100)
    return svg_browser_element


def transform_svg_2_png(svg_browser_element, out_png_path):
    """
    Turns the input SVG browser element into a PNG file and writes it
    to the output path.

    Parameters
    ----------
    svg_browser_element: required
        the result of load_svg_in_browser(path)
    out_png_path: str, required
        the path to which the PNG file needs to get written

    Returns
    -------
    The same SVG browser element as passed in.
    """

    png = svg_browser_element.screenshot_as_png
    img = Image.open(BytesIO(png))
    img.save(out_png_path, "PNG", quality=100)
    return svg_browser_element


def load_svg_in_browser(svg_path, driver):
    """
    Opens the passed-in file path in the first web browser
    that can be found installed on the system.
    """

    driver.get(f"file://{os.path.abspath(svg_path)}")
    driver.implicitly_wait(5)
    return driver.find_element(By.TAG_NAME, "svg")


def create_poster(
    config,
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
    - config: ConfigParser, required.
        Should be a config parser with the configuration preloaded.
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
        not config
        or not profile
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
            svg_poster = profile_maker.apply_profile_to_template(
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

    file_name_bare = f"{prefix}{case_id}-poster-{channel}"
    file_name_svg = f"{file_name_bare}.svg"
    print(f"Saving SVG poster to {file_name_svg}...")
    with open(file_name_svg, "w", encoding="utf-8") as output_file:
        output_file.write(svg_poster)
        output_file.close()
    with get_webdriver() as driver:
        browser_element = load_svg_in_browser(file_name_svg, driver)
        transform_svg_2_png(browser_element, f"{file_name_bare}.png")
        transform_svg_2_pdf(browser_element, f"{file_name_bare}.pdf")
    return None


def run_on_demand_functions(
    config,
    db,
    store
):
    """
    Runs the functions that are requested by the command-line
    arguments during the run invocation. See the readme file for
    documentation of the command-line switches.
    """

    if must_list_sheet_page_names():
        print("All page names in the spread sheet:")
        print(db_handler_sheets.get_store_names(db))
        sys.exit()

    if must_list_sheet_column_names():
        print("All column names in page:")
        page_column_names_row = config_handler.maybe_get_config_entry(
            config,
            "sheet",
            "page_column_names_row", "0"
        )
        columns = db_handler_sheets.get_column_names(
            store,
            int(page_column_names_row)
        )
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
            f"{str(column_index)} of page:"
        )
        print(msg)
        cells = db_handler_sheets.get_column_values(store, column_index)
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

    config = config_handler.read_config()
    maybe_db = db_handler_sheets.maybe_get_configured_db(config)
    if isinstance(maybe_db, KeyError):
        sys.exit(maybe_db)

    db_store = db_handler_sheets.get_db_store(config, maybe_db)
    if isinstance(db_store, KeyError):
        sys.exit(db_store)

    run_on_demand_functions(config, maybe_db, db_store)

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
            "Lammpster will create posters for the profile identified "
            f"by {case_id}..."
        )
        print(msg)

        profile = profile_maker.try_read_cached_profile(
            config,
            case_id
        )
        if profile:
            print("Found profile in cache.")
        else:
            print("Found no cache for this profile. Reaching out...")
            case_row_index = db_handler_sheets.find_row_index(
                db_store,
                case_id
            )
            if not case_row_index:
                msg = (
                    f"Error: No case found with id {case_id}. Use the "
                    "command-line switch --list-column-values to find "
                    "existing case identifiers."
                )
                sys.exit(msg)

            print(f"Found case with id {case_id}. Creating profile...")
            profile = profile_maker.create(
                config,
                db_store,
                case_row_index
            )

        output_folder = config_handler.maybe_get_config_entry(
            config,
            "output",
            "folder",
            "~/"
        )
        output_file_prefix = config_handler.maybe_get_config_entry(
            config,
            "output",
            "file_prefix",
            ""
        )

        poster_choices = config_handler.maybe_get_config_section_items(
             config,
             "posters",
             {}
        )
        if not poster_choices:
            raise Exception(
               "Error: missing posters configuration. Check the manual."
            )

        print("Generating and saving posters....")
        for channel, template in poster_choices.items():
            create_poster(
                config,
                profile,
                channel,
                template,
                output_folder,
                output_file_prefix
            )

        print(f"Done. Check the folder '{output_folder}' for new posters.")
        sys.exit()


# Normally, python will execute any script statements not
# part of a function, upon reading it.
# That also happens when using mypy or pydoc. But it should
# be skipped in those cases.
# Thus, the following makes sure the main() function gets
# executed only when python calls this script directly.
if __name__ == "__main__":
    main()
