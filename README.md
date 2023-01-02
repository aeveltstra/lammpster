To create posters from data stored in the LAMMP database.

Copyright: OmegaJunior Consultancy
Since: 2021-10-11.
Version: 2022-12-29

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
