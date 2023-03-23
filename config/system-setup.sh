#!/bin/bash

echo ! CONFIGURING BASE SYSTEM !

echo "FONT=Lat2-Terminus16" | sudo tee -a /etc/vconsole.conf
echo "FONT_MAP=8859-2" | sudo tee -a /etc/vconsole.conf
sudo pacman-mirrors --api --set-branch testging
sudo pacman-mirrors --fasttrack 5 
sudo pacman -Syy linux-rpi4-mainline linux-rpi4-mainline-headers --noconfirm
sudo pacman -Sy mpg123 portaudio spotifyd neofetch python-pip git base-devel

sudo mkdir /spotify-cache
sudo cp ./spotifyd-config.conf /etc/spotifyd.conf
sudo loginctl enable-linger $USER
systemctl --user enable spotifyd.service

sudo pacman -Syu
git clone https://aur.archlinux.org/yay-bin
cd yay-bin
makepkg -si --noconfirm
cd ..
rm -rf yay-bin

pip install pyaudio openai gTTS pydexcom SpeechRecognition colorama