#PRODUCTION INSTALLATION PROCESS

# 1) Download project from github:
git clone https://github.com/ShellyShelly/report_maker.git

# 2) Install virtualenv
sudo apt-get install python-virtualenv

# 3) Create virtualenv in report_maker dir
cd /var/www/<user-name>/report_maker_venv  # or something like this
mkdir report_maker_venv
virtualenv --no-site-packages report_maker_venv/
or
virtualenv --python=python3.6 report_maker_venv/

# 4) Activate virtual environment
source report_maker_venv/bin/activate

# 5) Install all requirements:

pip install -r requirements.txt

# 6) Install the dependencies to use PostgreSQL with Python/Django::
sudo apt-get -y install build-essential libpq-dev python-dev

# 7) Install the PostgreSQL Server:
sudo apt-get -y install postgresql postgresql-contrib

# 7*) Install MySQL Server:
sudo apt-get install mysql-server mysql-client
sudo apt-get install python3-dev libmysqlclient-dev build-essential

# 8) Enter in psql

# 8*) Enter in mysql
mysql -u root -p

# 9) Create user and db in psql:

create user report_maker_user with password 'jeferson97';

alter role report_maker_user set client_encoding to 'utf8';
alter role report_maker_user set default_transaction_isolation to 'read committed';
alter role report_maker_user set timezone to 'UTC';

create database report_maker_db owner report_maker_user;

# 9*) Create DB in mysql, create user and change owner of DB:
CREATE DATABASE 'someapp' DEFAULT CHARACTER SET utf8 DEFAULT COLLATE

mysql> CREATE USER 'django'@'localhost' IDENTIFIED BY 'password';
mysql> GRANT ALL PRIVILEGES ON 'someapp'.* TO 'django'@'localhost';
mysql> FLUSH PRIVILEGES;

# 10) Create my.cnf file in BASE_DIR with .
"my.cnf" --- filename

[client]
database = someapp
user = django
password = PASSWORD
default-character-set = utf8

# 9) Exit from psql:

\q

# 10) Create facebook_app_settings.txt in project_name dir.

Example of tree:

manage.py
facebook_app_settings.txt
...
# 11) Write in facebook_app_settings.txt SOCIAL_AUTH_FACEBOOK_KEY and SOCIAL_AUTH_FACEBOOK_SECRET:

12345678910 qwerty

# 12) Create twitter_app_settings.txt in project_name dir.

Example of tree:

manage.py
facebook_app_settings.txt
twitter_app_settings.txt
...
# 13) Write in twitter_app_settings.txt SOCIAL_AUTH_TWITTER_KEY and SOCIAL_AUTH_TWITTER_SECRET:

123qwe456rty qwerty

# 14) Collect static files
./manage.py collectstatic

# 15) Sync DB and Migrate
./manage.py syncdb
./manage.py migrate

# 16) Create Super User
./manage.py createsuperuser

# 17) Install WSGI packages
sudo apt-get install uwsgi uwsgi-plugin-python

# 18) Configure wsgi file
Example:
'''
import os
import sys

path = '/home/<your-username>/report_maker'  # use your own username and name of project here
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = '<mysite>.settings'  # use name of project

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
application = DjangoWhiteNoise(get_wsgi_application())
'''
