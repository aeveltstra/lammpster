To create posters from data stored in the LAMMP database.

Copyright: OmegaJunior Consultancy
Since: 2021-10-11.
Version: 2023-05-30

The LAMMP database stores and publishes information about
missing and murdered people who are part of marginalized 
communities. Looking for missing people can be eased by 
publishing posters with basic identifying information and
who to contact. 

The Lammpster software aims to automate the poster creation
process so that the operator only needs to provide a case 
identifier to have a poster generated in formats suited for 
various social media and physical printing.

LAMMP is a project by Redgrave Research and the Trans Doe
Task Force. 

OmegaJunior Consultancy recognizes that others can benefit
from the Lammpster software. But it is not released as a 
general purpose software. Instead, it is custom made for the 
LAMMP database. 

If you think your organization can be helped by a similar 
product, you are free to fork the available source code and 
change it to fit your needs. If you lack the time or the 
expertise to do so, you are free to reach out and contact 
OmegaJunior Consultancy and talk business.

Dependencies you need to install before attempting to run 
the application: 
- python3,
- pip3,
- pipenv

To build this application you need to have python3 installed,
with pip3 as its package manager, to install pipenv as the
tool that creates a virtual environment in which to run the 
app. Clone the source files from the git source at GitHub
or Source Hut. Have pipenv install the dependencies. Then 
run the pipenv shell. Once inside the pipenv shell, use this
command to run the application: 
  
$ python3 -m lammpster 12345  

or, simpler:

$ ./lammpster.py 12345
  
in which you replace the number 12345 with the identifier of
the record in your LAMMP database.  
  
It is likely to fail because the configuration available in
the source files is but an example. You need to adjust it to
fit your needs. That file is called:
/maps/lammpster.ini
  
First and foremost, understand that this software expects 
that the database is a Google Spread Sheet. The owner of 
that sheet must give its identifier to the Lammpster oper-
ator, to be set as the sheet identity in the [sheet] section
of the configuration. 
  
Next, the owner of the spread sheet must share the sheet with 
a Google Workspace Service Account, set up and provided by 
the operator of the Lammpster software, and specified in the
[account] section of the configuration. The operator must 
provide the email address of the service account to the sheet
owner. The service account requires read access, only. 
  
That requires that the operator of the Lammpster software has
a Google Workspace developer account, and has created a 
Workspace Project in which the Service Account lives, and has
enabled API access of that Project. The operator then has 
Google create a credential key file for the Service Account, 
using the tools that Google provides, saves that file in a 
location where the Lammpster software can read it, and tells
the Lammpster software where to find that file, in the 
[account] section of the configuration.
  
The owner of the spread sheet must tell the Lammpster 
operator in which of the sheet's pages to look for data. 
Lammpster can read only 1 page of 1 spread sheet, using 1 
service account. To read multiple pages of multiple sheets, 
possible using other service accounts, set up multiple 
copies of the software and adjust the config file for each.

The software is highly customized, and reads known columns 
from the spread sheet. Which columns, is specified in the 
configuration file, in the section 'profile', under the 
heading 'fields'. If you change that, make sure to also 
change the 'profile_map' section, wich maps the placeholder
names in the poster templates to the field names from the 
database.
  
It is possible to specify fewer and more poster templates. 
Templates must be created in SVG format. Programs that can 
create these include Draw.io and Inkscape. Each template 
creates posters in the formats pdf, png, and svg. Specify 
templates in the configuration file, in the section 
'posters'. 

Additional options:  
- --list-column-names will list the column names of the 
  specified page in the spread sheet. This is used to 
  configure the mapping of the spread sheet columns to the 
  posters. It looks at the [sheet] section in the configur-
  ation file to determine which row contains the sheet 
  column names. Invoke this without providing other switches
  or options, like so: 
  $ python3 -m lammpster --list-column-names  

- --list-sheet-pages will list the page names in the spread 
  sheet. Use this to explore a spread sheet of which the 
  owner forgot to specify which page to query. By default, 
  the page of interest is named sheet1, but owners have the 
  option of renaming sheets. Invoke this without providing 
  other switches or options, like so: 
  $ python3 -m lammpster --list-sheet-pages  

- --list-column-values x will list all values in column x in
  the specified page in the spread sheet. Use this to find a
  record identifier, for instance. Provide the index of the
  column to list. Usually that is column 1. Invoke this with-
  out providing other switches or options, like so: 
  $ python3 -m lammpster --list-column-values 1

- --unit-test will perform unit tests. A python script named
  'unit_tester.py' is available, that gets called. You can 
  call it by itself as well, like so: 
  $ python3 -m unit_tester
  
For added support and feedback, contact OmegaJunior Consultancy 
at: omegajunior@protonmail.com. 

