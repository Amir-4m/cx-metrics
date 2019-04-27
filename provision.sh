#!/usr/bin/env bash

# Install required packages
# Enable RabbitMQ application repository
sudo bash -c 'echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list.d/rabbitmq.list'
curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -

# Enable PostgreSQL application repository
sudo bash -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
sudo curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update repository list & upgrade packages
sudo apt-get -y -q update

# Common dep.
sudo apt-get install -y build-essential ntp git
sudo apt-get install -y python-dev python-pip python3-dev python3-pip
ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Setup memcached
sudo apt-get install -y memcached
sudo service memcached start

# Setup redis
sudo apt-get install -y redis-server
sudo service redis-server restart

# Setup RabbitMQ
sudo apt-get install -y --force-yes rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management

# Setup PostgreSQL
sudo apt-get install -y postgresql-9.5 postgresql-contrib-9.5
sudo sh -c 'echo "local all postgres trust" > /etc/postgresql/9.5/main/pg_hba.conf'
sudo sh -c 'echo -n "host all all 127.0.0.1/32 trust" >> /etc/postgresql/9.5/main/pg_hba.conf'
sudo /etc/init.d/postgresql restart

sudo -u postgres psql << EOF
UPDATE pg_database SET datistemplate=false WHERE datname='template1';
drop database template1;
create database template1 with template = template0 encoding = 'UTF8';
UPDATE pg_database SET datistemplate=true WHERE datname='template1';
EOF

sudo -u postgres createdb "fake-db" --encoding='utf-8' --locale=en_US.utf8 --template=template0

# Installing psycopg2 dep.
sudo apt-get install -y libpq-dev

# Installing gnu gettext
sudo apt-get install -y gettext

# pygraphviz required packages
sudo apt-get install -y graphviz libgraphviz-dev pkg-config

# Pillow required packages
sudo apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev
sudo apt-get install -y libfreetype6-dev liblcms2-dev
sudo apt-get install -y libwebp-dev tcl8.5-dev tk8.5-dev python-tk

# python-magic required package
sudo apt-get install -y libmagic1
