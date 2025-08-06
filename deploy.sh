#!/bin/bash

set -e

echo "Starting Ubuntu server deployment..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "Installing essential packages..."
sudo apt install -y curl wget git build-essential software-properties-common

# Install Node.js (if needed)
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt install -y nodejs
fi

# Install Docker (if needed)
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose (if needed)
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Nginx (if needed)
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo apt install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
fi

# Setup firewall
echo "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create application directory
APP_DIR="/var/www/meet"
echo "Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Clone or update application (customize this section)
if [ -d "$APP_DIR/.git" ]; then
    echo "Updating existing application..."
    cd $APP_DIR
    git pull origin main
else
    echo "Cloning application..."
    # Replace with your repository URL
    # git clone https://github.com/your-repo/your-app.git $APP_DIR
    echo "Please update the git clone command with your repository URL"
fi

# Install application dependencies (customize based on your stack)
cd $APP_DIR
if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install --production
fi

if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Build application (customize as needed)
if [ -f "package.json" ] && grep -q "build" package.json; then
    echo "Building application..."
    npm run build
fi

# Setup systemd service (customize as needed)
SERVICE_NAME="meet-onebitebitcoin"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Creating systemd service..."
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Your Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
fi

# Start/restart the service
echo "Starting application service..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl status $SERVICE_NAME --no-pager

# Setup Nginx configuration (basic example)
NGINX_CONFIG="/etc/nginx/sites-available/meet.onebitebitcoin.com"
if ! grep -q "proxy_pass" $NGINX_CONFIG; then
    echo "Configuring Nginx reverse proxy..."
    sudo tee $NGINX_CONFIG > /dev/null <<EOF
server {
    listen 80 ;
    server_name meet.onebitebitcoin.com;

    location ~ /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
        allow all;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name meet.onebitebitcoin.com;

    access_log /var/log/nginx/meet.onebitebitcoin.com.access.log;
    error_log /var/log/nginx/meet.onebitebitcoin.com.error.log;
    ssl_certificate /etc/letsencrypt/live/onebitebitcoin.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/onebitebitcoin.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    root /var/www/meet;

    location / {
        try_files $uri $uri/ /index.html;
    }


    location ~ /media/ {
        # for media upload 
        allow all;
        root /var/www/meet.onebitebitcoin.com/;
        try_files $uri =404;
        charset utf-8;  # Add UTF-8 Support
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }


    # Serve JavaScript, CSS, images, fonts, etc.
    location ~* \.(?:js|css|ico|json|xml|jpg|jpeg|png|gif|woff|woff2|ttf|svg|map)$ {
        root /var/www/meet.onebitebitcoin.com/html;
        access_log off;
        #expires max;
        #add_header Cache-Control "public, max-age=31536000";

        expires -1;
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate";
        add_header Pragma "no-cache";
        add_header Expires 0;
    }
}
EOF

    sudo nginx -t
    sudo systemctl reload nginx
fi

echo "Deployment completed successfully!"
echo "Please customize the following sections for your specific application:"
echo "1. Repository URL for git clone"
echo "2. Service configuration in systemd"
echo "3. Application build and start commands"
echo "4. Nginx configuration for your specific needs"
