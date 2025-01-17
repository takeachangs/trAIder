#!/bin/bash
# Deployment script for trAIder

# Exit on error
set -e

# Configuration
APP_NAME="trAIder"
DEPLOY_DIR="/opt/trAIder"
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
SERVICE_NAME="trAIder"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with color
print_status() {
    echo -e "${GREEN}[+] $1${NC}"
}

print_error() {
    echo -e "${RED}[-] $1${NC}"
}

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Please run with sudo"
    exit 1
fi

# Create deployment directory
print_status "Creating deployment directory..."
mkdir -p $DEPLOY_DIR

# Copy application files
print_status "Copying application files..."
cp -r ../src $DEPLOY_DIR/
cp ../$REQUIREMENTS $DEPLOY_DIR/

# Set up Python virtual environment
print_status "Setting up virtual environment..."
cd $DEPLOY_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install requirements
print_status "Installing dependencies..."
pip install --upgrade pip
pip install -r $REQUIREMENTS

# Create systemd service
print_status "Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOL
[Unit]
Description=trAIder Trading Analysis Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=$DEPLOY_DIR/$VENV_DIR/bin"
ExecStart=$DEPLOY_DIR/$VENV_DIR/bin/python src/ui/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Set permissions
print_status "Setting permissions..."
chown -R www-data:www-data $DEPLOY_DIR
chmod -R 755 $DEPLOY_DIR

# Start service
print_status "Starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

print_status "Deployment complete!"
print_status "Service status:"
systemctl status $SERVICE_NAME

# Add nginx configuration if needed
# print_status "Configuring nginx..."
# cat > /etc/nginx/sites-available/$APP_NAME << EOL
# server {
#     listen 80;
#     server_name your_domain.com;
#
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         proxy_set_header Host \$host;
#         proxy_set_header X-Real-IP \$remote_addr;
#     }
# }
# EOL

# ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
# nginx -t && systemctl restart nginx