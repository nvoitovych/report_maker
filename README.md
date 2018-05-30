## DEVELOPMENT INSTALLATION PROCESS

# 1) create virtualenv
# 2) activate venv
# 3) install all requirements:

pip install -r requirements_dev.txt

# 4*) Install MySQL
sudo apt-get install mysql-server mysql-client

# 5*) Enter in mysql
mysql -u root -p

# 6*) Create db
CREATE DATABASE report_maker_db DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

# 7*) Create user for DB and exit from mysql
CREATE USER 'report_maker_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON report_maker_db.* TO 'report_maker_user'@'localhost';
FLUSH PRIVILEGES;

# 4) install postgresql:
sudo apt-get install postgresql

# 5) enter in psql
# 6) create user and db in psql:

 create user report_maker_user with password 'jeferson97';

 alter role report_maker_user set client_encoding to 'utf8';
 alter role report_maker_user set default_transaction_isolation to 'read committed';
 alter role report_maker_user set timezone to 'UTC';

 create database report_maker_db owner report_maker_user;


# 7) exit from psql:
 \q

# 8) create facebook_app_settings.txt in project_name dir.
Example of tree:
- manage.py
- facebook_app_settings.txt
- ...

# 9) write in facebook_app_settings.txt SOCIAL_AUTH_FACEBOOK_KEY and SOCIAL_AUTH_FACEBOOK_SECRET:

12345678910
qwerty

# 10) create twitter_app_settings.txt in project_name dir.
Example of tree:
- manage.py
- facebook_app_settings.txt
- twitter_app_settings.txt
- ...

# 11) write in twitter_app_settings.txt SOCIAL_AUTH_TWITTER_KEY and SOCIAL_AUTH_TWITTER_SECRET:

123qwe456rty
qwerty

# 12) ./manage.py migrate
# 13) ./manage.py createsuperuser
