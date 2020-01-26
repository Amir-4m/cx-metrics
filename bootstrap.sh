#!/usr/bin/env bash

# Functions
function append_to_file() {
    if [[ -f "$2" ]]
    then
        grep -Fxq "$1" "$2" || echo "$1" >> "$2"
    else
        echo "$1" > "$2"
    fi
}

function setup_virtualenv() {
    deactivate
    source `which virtualenvwrapper.sh` && mkvirtualenv $1  --python=$2
    workon $1

    cd /vagrant
    pip install -r "requirements/development.txt"
    pip install -r "requirements/$3.txt"
}

# Enable soft tabs in Vim
append_to_file "set tabstop=4" ~/.vimrc
append_to_file "set softtabstop=4" ~/.vimrc
append_to_file "set shiftwidth=4" ~/.vimrc
append_to_file "set expandtab" ~/.vimrc

cd /vagrant
sudo apt-get update
sudo apt-get install -y dos2unix
dos2unix provision.sh
chmod a+x provision.sh
sh provision.sh

# Installing and setup required basic python packages
sudo apt-get install -y python3
sudo -H python3 -m pip install --upgrade pip
sudo -H pip install --upgrade setuptools wheel virtualenv virtualenvwrapper

ssh-keyscan -t rsa bitbucket.org >> ~/.ssh/known_hosts
ssh-keyscan -t rsa 45.82.137.3 >> ~/.ssh/known_hosts
append_to_file "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" $HOME/.bashrc
append_to_file "export WORKON_HOME=$HOME/.virtualenvs" $HOME/.bashrc
append_to_file "export PROJECT_HOME=/vagrant" $HOME/.bashrc
append_to_file "source /usr/local/bin/virtualenvwrapper.sh" $HOME/.bashrc
source $HOME/.bashrc

# Setup virtual environments
setup_virtualenv "cx_metrics_dj21" "python3" "django-2.1"
setup_virtualenv "cx_metrics" "python3" "django-2.2"
append_to_file "workon cx_metrics" ~/.bashrc

# Create project folder
mkdir -p /home/vagrant/projects

cp /vagrant/id_rsa /home/vagrant/.ssh/id_rsa
chmod 600 /home/vagrant/.ssh/id_rsa

append_to_file "cd /vagrant" ~/.bashrc
cd /vagrant