#!/usr/bin/env python3
# Easily publish LAMMP registrations as posters for publication 
# on social media and phystical printing. 
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.23.102.0020
#

import datetime
import gspread
import os
from functools import partial
from oauth2client.service_account import ServiceAccountCredentials
from configparser import ConfigParser
import sys
from string import Template
import json
from cairosvg import svg2png, svg2pdf


def list_headers() -> [str]:
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
) -> str:
  header_index = list_headers().index(header)
  if not header_index:
     return None
  cell = page.cell(row_index, header_index)
  if not cell:
     return None
  return cell.value


def get_current_year() -> int:
  return datetime.date.today().year


def get_sheet(
  keys_file: str, 
  sheet_id: str
):
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


def get_page_names(sheet) -> [str]:
  pages = sheet.worksheets()
  titles = [page.title for page in pages]
  return titles


def get_page(
  sheet, 
  page_name: str
):
  return sheet.worksheet(page_name)


def get_page_column_names(
  page, 
  row_index: int
) -> [str]:
  if not page: 
    return None
  cells = page.row_values(row_index)
  if not cells:
    return None
  return cells


def get_column_values(
  page, 
  column_index: int
) -> [str]:
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
  row_index: int
) -> dict:
  if not page or not row_index:
    return None
  g1 = partial(get_cell_value_for_header, page)
  g2 = partial(g1, row_index)
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


def find_row_index(page, row_identifier):
  if not page or not row_identifier:
    return None
  cells = page.findall(row_identifier)
  if not cells:
    return None
  cell = find_first(is_first_column, cells)
  if not cell:
    return None
  return cell.row


def read_row_id_from_command_line():
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
  return Template(template_contents).substitute(
     name=profile.get('Chosen Name', 'unknown')
    ,age=profile.get('Age', 'unknown')
    ,last_seen_on=profile.get('Last Seen Date', 'unknown')
    ,last_seen_where=profile.get('Last Seen Location', 'unknown')
    ,last_seen_wearing=profile.get('Last Seen Wearing', 'unknown')
    ,contact_if_found=profile.get('Who to Contact If Found', 'unknown')
    ,image_path=profile.get('Image 1 Path', '')
  )


def create_poster(profile, channel, template_path, output_folder, file_prefix):
  if not profile or not channel or not template_path or not output_folder:
    return None
  prefix = output_folder + file_prefix
    
  try: 
    with open(template_path, 'r') as template: 
      svg_poster = apply_profile_to_template(profile, template.read())
      if not svg_poster:
        print('Failed to create poster for channel ' + channel)
        return None
      output_file = open(prefix + profile.get('Case ID') + '-poster-' + channel + '.svg','w')
      output_file.write(svg_poster)
      svg2png(bytestring=svg_poster, write_to=prefix + profile.get('Case ID') + '-poster-' + channel + '.png')
      svg2pdf(bytestring=svg_poster, write_to=prefix + profile.get('Case ID') + '-poster-' + channel + '.pdf')

  except FileNotFoundError:
    print('For channel ' + channel + ' no template was found named ' + template_path)
    return None


config = ConfigParser()
if not os.path.exists('./.config'):
  sys.exit('Expected configuration file ".config" was not found. '
    + 'Please consult the documentation.')
else:
  print('Retrieving configuration...')

config.read('./config')
sheet_id = config.get('sheet', 'google_drive_sheet_id') 
page_name = config.get('sheet', 'page_name')
keys_file = config.get('account', 'keys_file')
sheet = get_sheet(keys_file, sheet_id)

if must_list_sheet_page_names():
  print('All page names in the spread sheet:')
  pages = get_page_names(sheet);
  sys.exit(pages)

page = get_page(sheet, page_name)
if not page:
  sys.exit('Spreadsheet has no page named ' + page_name + '.')

print('Found spreadsheet page named ' + page_name + '.')

if must_list_sheet_column_names():
  print('All column names in page:')
  page_column_names_row = config.get('sheet', 'page_column_names_row')
  columns = get_page_column_names(page, page_column_names_row);
  sys.exit(columns)

if must_list_column_values():
  column_index = list_values_for_which_column()
  if not column_index:
    sys.exit('Specify the column index of which to list the values. First column has index 1.')
  elif 1 > column_index:
    sys.exit('Column index must be larger than 0. First column has index 1.')
  print('All column values in column ' + str(column_index) + ' of page:')
  cells = get_column_values(page, column_index);
  sys.exit(cells)


row_id = read_row_id_from_command_line()
if not row_id:
    sys.exit('Provide a row identifier for the profile to print. '
        + 'Place it as the first argument of the application '
        + 'run invocation, like so: $ python3 lammpster.py 1234')
else:
    print('Lammpster will create a poster for the profile based on row ' 
      + row_id + '.')

    found_row = find_row_index(page, row_id)
    if not found_row:
      sys.exit('No row found with ID ' + row_id)

    print('Found row with ID ' + row_id + '. Creating profile.')
    profile = create_profile(page, found_row)

    output_folder = config.get('output', 'folder')
    output_file_prefix = config.get('output', 'file_prefix')
    poster_choices = dict(config.items('posters'))

    print('Profile created. Generating and saving posters.')
    for channel, template in poster_choices.items():
      create_poster(profile, channel, template, output_folder, output_file_prefix)

    print('Done. Check the folder for new posters.')
