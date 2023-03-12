#!/usr/bin/env python3
# Easily publish LAMMP registrations as posters for publication 
# on social media and phystical printing. 
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.1018.2130
#

import datetime
import gspread
import os
from functools import partial
from oauth2client.service_account import ServiceAccountCredentials
from configparser import ConfigParser,NoOptionError
from typing import Any, List, Union, Optional
import sys
from string import Template
import json
from cairosvg import svg2png, svg2pdf
from urllib.error import URLError


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
  return [  ''
          , 'Case ID'
          , 'Created At'
          , 'Created By'
          , 'Last Modified At'
          , 'Last Modified By'
          , 'Case Status'
          , 'Poster Generated At'
          , 'Given Name'
          , 'Chosen Name'
          , 'Aliases'
          , 'Birth Year'
          , 'Birth Year Accuracy'
          , 'Last Seen Date'
          , 'Last Seen Date Accuracy'
          , 'Last Seen Location'
          , 'Last Seen Wearing'
          , 'Last Seen Activity'
          , 'Who to Contact If Found'
          , 'Image Path'
          , 'Image Path 2'
          , 'Disappearance Circumstances'
          , 'Eyes'
          , 'Hair'
          , 'Height'
          , 'Identifying Features'
          , 'Other Notes'
          , 'Pronouns'
          , 'Race'
          , 'Weight'
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


def get_sheet(
  keys_file: str, 
  sheet_id: str
):
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
  sheet | None
      None, if the gspread module was unable to retrieve a 
      service account based on the provided keys file.
      None, if the passed-in sheet_id does not lead to an 
      existing or accessible Google Sheet. 
      Otherwise, the Google Sheet.
  """

  if not keys_file:
    print('Please set file name for service account in config.')
  if not sheet_id:
    print('Please set the identity of the sheet to read in config.')
  if not keys_file or not sheet_id:
    sys.exit('Aborting.')
  client = gspread.service_account(keys_file)
  if not client:
    return None
  sheet = client.open_by_key(sheet_id)
  return sheet


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


def get_page(
  sheet, 
  page_name: str
):
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


def get_page_column_names(
  page, 
  row_index: int
) -> Union[List[str], None]:
  if not page: 
    return None
  cells = page.row_values(row_index)
  if not cells:
    return None
  return cells


def get_column_values(
  page, 
  column_index: int
) -> Union[List[str], None]:
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
  if not page or not case_row_index:
    return None
  g1 = partial(get_cell_value_for_header, page)
  g2 = partial(g1, case_row_index)
  birth_year = g2('Birth Year')
  age = None
  if birth_year:
    age = get_current_year() - int(birth_year)
  return {
    'Age': age,
    'Birth Year': birth_year,
    'Case ID': g2('Case ID'),
    'Chosen Name': g2('Chosen Name'),
    'Disappearance Circumstances': g2('Disappearance Circumstances'),
    'Eyes': g2('Eyes'),
    'Hair': g2('Hair'),
    'Height': g2('Height'),
    'Identifying Features': g2('Identifying Features'),
    'Image 1 Path': g2('Image Path'),
    'Image 2 Path': g2('Image Path 2'),
    'Last Seen Date': g2('Last Seen Date'),
    'Last Seen Location': g2('Last Seen Location'),
    'Last Seen Wearing': g2('Last Seen Wearing'),
    'Other Notes': g2('Other Notes'),
    'Pronouns': g2('Pronouns'),
    'Race': g2('Race'),
    'Weight': g2('Weight'),
    'Who to Contact If Found': g2('Who to Contact If Found')
  }


def find_first(predicate, haystack):
  return next((i for i in haystack if predicate(i)), None)


def is_first_column(cell):
  return cell.col == 1


def find_row_index(page, case_identifier):
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
  if len(sys.argv) > 1:
    return sys.argv[1]
  return None


def must_list_sheet_column_names():
  if len(sys.argv) == 0:
    return False
  for arg in sys.argv:
    if arg == "--list-column-names":
      return True
  return False


def must_list_sheet_page_names():
  return "--list-sheet-pages" in sys.argv


def must_list_column_values():
  return "--list-column-values" in sys.argv


def list_values_for_which_column():
  i = sys.argv.index("--list-column-values")
  if (i+1) < len(sys.argv):
    return int(sys.argv[i+1])
  return None


def apply_profile_to_template(profile, template_contents):
  if not profile or not template_contents:
    return None

  try:
    result = Template(template_contents).substitute(
        name=profile.get('Chosen Name', '')
      , age=profile.get('Age', '')
      , race=profile.get('Race', '')
      , height=profile.get('Height', '')
      , weight=profile.get('Weight', '')
      , eyes=profile.get('Eyes', '')
      , hair=profile.get('Hair', '')
      , pronouns=profile.get('Pronouns', '')
      , last_seen_on=profile.get('Last Seen Date', '')
      , last_seen_where=profile.get('Last Seen Location', '')
      , last_seen_wearing=profile.get('Last Seen Wearing', '')
      , identifying_features=profile.get('Identifying Features', '')
      , disappearance_circumstances=profile.get('Disappearance Circumstances', '')
      , contact_if_found=profile.get('Who to Contact If Found', '')
      , image_path_1=profile.get('Image Path', 'templates/transparent-1020x1024.png')
      , image_path_2=profile.get('Image Path 2', 'templates/transparent-1020x1024.png')
      , other_notes=profile.get('Other Notes', '')
    )
    return result
  except KeyError as e:
    print(f'Error: failed to apply profile. Either the placeholder was not found, or it was not given a substitute: {e}.')
    raise


def create_poster(profile, channel, template_path, output_folder, file_prefix) -> None:
  if not profile or not channel or not template_path or not output_folder:
    return None
  prefix = output_folder + file_prefix
  case_id = profile.get("Case ID")

  print(f'Creating poster for case {case_id}, for channel {channel}...')
  
  svg_poster = None
  try: 
    with open(template_path, 'r') as template: 
      svg_poster = apply_profile_to_template(profile, template.read())
  except FileNotFoundError:
    print(f'For channel {channel} no template was found named {template_path}.')
    return None

  if not svg_poster:
      print(f'Failed to create poster contents.')
      return None

  file_path = f'{prefix}{case_id}-poster-{channel}.svg'
  print(f'Saving SVG poster to {file_path}...')
  output_file = open(file_path, 'w')
  output_file.write(svg_poster)
  output_file.close()
  file_path = f'{prefix}{case_id}-poster-{channel}.png'
  print(f'Saving PNG poster to {file_path}...')
  try:
     svg2png(bytestring=svg_poster, write_to=file_path)
  except URLError as e:
     print(f'Error: file not found: {e}.')
  except FileNotFoundError as e:
     print(f'Error: file not found: {e}.')
  file_path = f'{prefix}{case_id}-poster-{channel}.pdf'
  print(f'Saving PDF poster to {file_path}...')
  try:
      svg2pdf(bytestring=svg_poster, write_to=file_path)
  except URLError as e:
     print(f'Error: file not found: {e}.')
  except FileNotFoundError as e:
     print(f'Error: file not found: {e}.')


def maybe_get_config_section_items(
    config: ConfigParser,
    section_name: str,
    default: Optional[dict]=None
) -> Union[dict,None]:
    result = None

    try:
      result = config.items(section_name)
      return dict(result)
    
    except (KeyError, NoOptionError) as e:
      if default:
        print(f'Info: found no configuration section {section_name}. Defaulting to {default}.')
        result = default
      else:
        print(f'Warning: found no configuration section {section_name}. No default was provided.')
        result = None

    return result


def maybe_get_config_entry(
    config: ConfigParser,
    section_name: str,
    entry_name: str,
    default: Optional[str]=None
) -> Union[str,None]:
    result = None

    try:
      result = config.get(section_name, entry_name)
    
    except (KeyError, NoOptionError) as e:
      if default:
        print(f'Info: found no entry {entry_name} in configuration section {section_name}. Defaulting to {default}.')
        result = default
      else:
        print(f'Warning: found no entry {entry_name} in configuration section {section_name}. No default was provided.')
        result = None

    return result
    


def main() -> None:
  if not os.path.exists('./.config'):
    sys.exit('Expected configuration file ".config" was not found. '
      + 'Please consult the documentation.')
  else:
    print('Retrieving configuration...')
  
  config = ConfigParser()
  config.read('./.config')
  sheet_id = maybe_get_config_entry(config, 'sheet', 'google_drive_sheet_id') 
  page_name = maybe_get_config_entry(config, 'sheet', 'page_name')
  keys_file = maybe_get_config_entry(config, 'account', 'keys_file')
  if not sheet_id or not page_name or not keys_file:
     sys.exit("Aborting. Missing 1 or more configuration keys: 'google_drive_sheet_id', 'page_name', or 'keys_file'. Read the manual about setting up the configuration file.")

  sheet = get_sheet(keys_file, sheet_id)
  
  if must_list_sheet_page_names():
    print('All page names in the spread sheet:')
    pages = get_page_names(sheet);
    print(pages)
    sys.exit()
  
  page = get_page(sheet, page_name)
  if not page:
    sys.exit(f'Spreadsheet has no page named {page_name}.')
  
  print(f'Found spreadsheet page named {page_name}.')
  
  if must_list_sheet_column_names():
    print('All column names in page:')
    page_column_names_row = maybe_get_config_entry(config, 'sheet', 'page_column_names_row', '0')
    columns = get_page_column_names(page, int(page_column_names_row));
    print(columns)
    sys.exit()
  
  if must_list_column_values():
    column_index = list_values_for_which_column()
    if not column_index:
      sys.exit('Specify the column index of which to list the values. First column has index 1.')
    elif 1 > column_index:
      sys.exit('Column index must be larger than 0. First column has index 1.')
    print('All column values in column ' + str(column_index) + ' of page:')
    cells = get_column_values(page, column_index);
    print(cells)
    sys.exit()
  
  
  case_id = read_case_id_from_command_line()
  if not case_id:
      message = """Error: missing case identifier.
  Specify the identity of the case/profile to print.    
  Place it as the first argument of the application
  run invocation, like so:
  $ python3 ./lammpster.py abc1234
  To find out what case identifiers exist, use the
  command-line switch --list-column-values i,
  in which you substitute i for the column that
  holds the case identifiers, like so:
  $ python3 ./lammpster.py --list-column-values 1"""
      sys.exit(message)
  else:
      print(f'Lammpster will create posters for the profile based on row {case_id}...')
  
      case_row_index = find_row_index(page, case_id)
      if not case_row_index:
          sys.exit(f'Error: No case found with id {case_id}. Use the command-line switch --list-column-values to find existing case identifiers.')
  
      print(f'Found case with id {case_id}. Creating profile...')
      profile = create_profile(page, case_row_index)
      
      output_folder = maybe_get_config_entry(config, 'output', 'folder', '~/')
      output_file_prefix = maybe_get_config_entry(config, 'output', 'file_prefix', '')

      poster_choices = maybe_get_config_section_items(config, 'posters', {})
      if not poster_choices:
        raise Exception('Error: missing posters configuration. Check the manual.')
  
      print('Profile created.')
      print('Generating and saving posters....')
      for channel, template in poster_choices.items():
        create_poster(profile, channel, template, output_folder, output_file_prefix)
  
      print('Done. Check the folder for new posters.')
      sys.exit()


# Normally, python will execute any script statements not 
# part of a function, upon reading it. 
# That also happens when using mypy or pydoc. But it should
# be skipped in those cases.
# Thus, the following makes sure the main() function gets
# executed only when python calls this script directly.
if __name__ == '__main__':
    main()

