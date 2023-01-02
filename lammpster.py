#!/usr/bin/env python3
# Easily publish LAMMP registrations as posters for publication 
# on social media and phystical printing. 
#
# Copyright OmegaJunior Consultancy
# Since 2021-10-11
# Version 2.22.1229.1230
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


def get_client(key_path):
  return gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_name(
      key_path,
      [
          'https://www.googleapis.com/auth/spreadsheets.readonly'
        , 'https://www.googleapis.com/auth/drive.readonly'
      ]
    )
  )

def list_headers():
  # we need an empty 0 header. if we don't supply one, 
  # the spreadsheet won't find the 1st column.
  return ['', 'Case ID', 'Created At', 'Created By', 'Last Modified At', 'Last Modified By', 'Case Status', 'Poster Generated At', 'Given Name', 'Chosen Name', 'Aliases', 'Birth Year', 'Birth Year Accuracy', 'Last Seen Date', 'Last Seen Date Accuracy', 'Last Seen Location', 'Last Seen Wearing', 'Last Seen Activity', 'Who to Contact If Found', 'Image Path']

def get_cell_value_for_header(page, row_index, header):
  header_index = list_headers().index(header)
  if not header_index:
     return None
  cell = page.cell(row_index, header_index)
  if not cell:
     return None
  return cell.value

def get_current_year():
  return datetime.date.today().year

def get_page(keys_file, sheet_id, page_name):
  client = get_client(keys_file)
  if not client:
     return None
  sheet = client.open_by_key(sheet_id)
  if not sheet:
     return None
  page = sheet.worksheet(page_name)
  if not page:
     return None
  return page


def create_profile(page, row_index):
  if not page or not row_index:
     return None
  g1 = partial(get_cell_value_for_header, page)
  g2 = partial(g1, row_index)
  birth_year = g2('Birth Year')
  age = None
  if birth_year:
     age = get_current_year() - int(birth_year)
  return {
    'Case ID': g2('Case ID'),
    'Chosen Name': g2('Chosen Name'),
    'Birth Year': birth_year,
    'Age': age,
    'Last Seen Location': g2('Last Seen Location'),
    'Last Seen Wearing': g2('Last Seen Wearing'),
    'Last Seen Date': g2('Last Seen Date'),
    'Who to Contact If Found': g2('Who to Contact If Found'),
    'Image Path': g2('Image Path')
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
        ,image_path=profile.get('Image Path', '')
    )

def create_poster(profile, channel, output_folder, file_prefix):
    if not profile or not channel or not output_folder:
        return None
    prefix = output_folder + file_prefix
    
    template_setting = config.get('posters', channel)
    try: 
        with open(template_setting, 'r') as template: 
            svg_poster = apply_profile_to_template(profile, template.read())
            if not svg_poster:
                print('Failed to create poster for channel ' + channel)
                return None
            output_file = open(prefix + profile.get('Case ID') + '-poster-' + channel + '.svg','w')
            output_file.write(svg_poster)
            svg2png(bytestring=svg_poster, write_to=prefix + profile.get('Case ID') + '-poster-' + channel + '.png')
            svg2pdf(bytestring=svg_poster, write_to=prefix + profile.get('Case ID') + '-poster-' + channel + '.pdf')

    except FileNotFoundError:
        print('For channel ' + channel + ' no template was found named ' + template_setting)
        return None


row_id = read_row_id_from_command_line()
if not row_id:
   sys.exit('Provide a row identifier for the profile to print. '
        + 'Place it as the first argument of the application '
        + 'run invocation, like so: $ python3 lammpster.py 1234')

print('Lammpster will create a poster for the profile based on row ' 
      + row_id + '. Retrieving configuration...')

config = ConfigParser()
if not os.path.exists('./lammpster.ini'):
   sys.exit('Expected configuration file lammpster.ini was not found. '
        + 'Please consult the documentation.')

config.read('./lammpster.ini')
sheet_id = config.get('sheet', 'google_drive_sheet_id') 
page_name = config.get('sheet', 'page_name')
keys_file = config.get('account', 'keys_file')
output_folder = config.get('output', 'folder')
output_file_prefix = config.get('output', 'file_prefix')

page = get_page(keys_file, sheet_id, page_name)
if not page:
   sys.exit('Spreadsheet has no page named ' + page_name)

print('Found spreadsheet page named ' + page_name + '. Finding row.')

found_row = find_row_index(page, row_id)
if not found_row:
   sys.exit('No row found with ID ' + row_id)

profile = create_profile(page, found_row)
print('Found row with ID ' + row_id + '. Creating profile.')

channels = ['facebook', 'twitter_header', 'twitter_post', 'discord', 'print']
for channel in channels:
    print('Creating poster for channel ' + channel)
    create_poster(profile, channel, output_folder, output_file_prefix)

print('Done. Check the folder for new posters.')
