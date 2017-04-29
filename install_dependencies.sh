#!/usr/bin/env bash

if [ $(uname) != "Linux" ]; then
    echo "This install script is only meant for linux"
    exit 1
fi

if [ ! -f .env ]; then
    echo "See the README for instructions on creating the .env file"
    exit 1
fi

print_step () {
    printf "\n\n>>> $1\n\n"
}

print_step "Updating/upgrading apt packages"
sudo apt-get remove docker docker-engine
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove -y

print_step "Installing apt packages"
sudo apt-get install -y \
    python3-pip \
    python-pip \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git \
    vim

print_step "Fetching nodejs"
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -

print_step "Fetching Docker PPA"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

print_step "Updating apt cache"
sudo apt-get update

print_step "Installing nodejs"
sudo apt-get install -y nodejs

print_step "Installing Docker and Docker compose"
sudo apt-get install -y docker-ce
sudo groupadd docker ; sudo usermod -aG docker $USER
sudo pip3 install -U pip
sudo pip3 install docker-compose

print_step "Rebooting so Docker works, after reboot run bash install_project.sh"
sleep 3
sudo reboot
