To create posters from data stored in the LAMMP database.

Copyright: OmegaJunior Consultancy
Since: 2021-10-11.
Version: 2023-01-01

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
- pipenv,
- libcairo-2

To install libcairo-2 on an older Mac, read this document:
https://cairographics.org/download/

In our test environment we used the fink package manager
for MacOsX:
https://www.finkproject.org/download/index.php?phpLang=en

and then we installed cairosvg with pipenv. Running Lammpster
however failed because cairoffi was unable to locate the 
libcairo libraries we had installed. That's because cairo
does not look for libraries that exist in Fink's libraries
path. So we have to tell it. For instance, if you used Fink,
libcairo.2.dylib will exist in /sw/lib. To tell cairoffi to 
look there, we can do this:
$ export LD_LIBRARY_PATH=/sw/lib:$LD_LIBRARY_PATH

To build this application you need to have python3 installed,
with pip3 as its package manager, to install pipenv as the
tool that creates a virtual environment in which to run the 
app. Clone the source files from the git source at Source 
Hut. Have pipenv install the dependencies. Then run the 
pipenv shell. Once inside the pipenv shell, use the following
command to run the application: 

$ python3 lammpster.py 12345

in which you replace the number 12345 with the identifier of
the record in your LAMMP database.

It is likely to fail because the configuration available in
the source files is customized to my specific environment. 
You probably need to adjust it to fit your needs. That file 
is called lammpster.ini.

First and foremost, understand that this software expects that 
the database is a Google Spread Sheet. The owner of that sheet
must give its identifier to the Lammpster operator, to be set 
as the sheet identity in the [sheet] section of lammpster.ini. 
  
Next, the owner of the spread sheet must share the sheet with 
a Google Workspace Service Account, that is set up and provided
by the operator of the Lammpster software, and specified in the
[account] section of lammpster.ini. The operator must provide 
the email address of the service account to the sheet owner. 
The service account requires read access, only. 
  
That requires that the operator of the Lammpster software has
a Google Workspace developer account, and has created a 
Workspace Project in which the Service Account lives, and has
enabled API access of that Project. The operator then has 
Google create a credential key file for the Service Account, 
using the tools that Google provides, saves that file in a 
location where the Lammpster software can read it, and tells
the Lammpster software where to find that file, in the [account]
section of lammpster.ini.
  
The owner of the spread sheet must tell the Lammpster operator
in which of the sheet's pages to look for data. Lammpster can 
read only 1 page of 1 spread sheet, using 1 service account. 
To read multiple pages of multiple sheets, possible using other 
service accounts, set up multiple copies of the software and 
adjust the lammpster.ini file for each copy.
  
The software is highly customized, and reads known columns from 
the spread sheet. If other columns need to be read, the owner 
must inform the operator, who can adjust the software. 
  
In cases where the operator and the owner are the same person, 
it is possible to have a software developer set up and customize
everything so that the owner can work the software at need. 
  
For added support and feedback, contact OmegaJunior Consultancy 
at: omegajunior@protonmail.com. 

