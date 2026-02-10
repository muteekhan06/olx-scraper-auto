#!/bin/bash

# OLXify AWS EC2 Setup Script
# Run this on a fresh Ubuntu 22.04/24.04 server

echo "🚀 Starting OLXify Server Setup..."

# 1. Update System
echo "🔄 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. Install Python & Basic Tools
echo "🐍 Installing Python, Pip, and Git..."
sudo apt-get install -y python3 python3-pip git wget unzip libnss3

# 3. Install Google Chrome (for Selenium)
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# 4. Install Project Dependencies
echo "📦 Installing Python libraries..."
pip3 install -r requirements.txt

# 5. Create Config Directory
mkdir -p config
mkdir -p output

echo "✅ Setup Complete! You can now configure your secrets."
