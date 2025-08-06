#!/bin/bash

set -e

echo "Starting Ubuntu server deployment..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "Installing essential packages..."
sudo apt install -y curl wget git build-essential software-properties-common python3 python3-pip python3-venv

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

# Navigate to application directory
cd $APP_DIR

# Deploy Django Backend
echo "=== Deploying Django Backend ==="
if [ -f "requirements.txt" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    
    echo "Running Django migrations..."
    python manage.py migrate
    
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    
    echo "Copying static files to web directory..."
    sudo mkdir -p /var/www/meet/staticfiles
    sudo cp -r staticfiles/* /var/www/meet/staticfiles/ 2>/dev/null || true
    sudo mkdir -p /var/www/meet/media
    sudo cp -r media/* /var/www/meet/media/ 2>/dev/null || true
    
    echo "Creating Django superuser (if needed)..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    deactivate
fi

# Deploy Vue Frontend
echo "=== Deploying Vue Frontend ==="
FRONTEND_DIR="$APP_DIR/meetup-manager"
if [ -d "$FRONTEND_DIR" ]; then
    echo "Building Vue frontend..."
    cd $FRONTEND_DIR
    
    if [ -f "package.json" ]; then
        echo "Installing Node.js dependencies..."
        npm install
        
        echo "Building production build..."
        npm run build
        
        echo "Deploying to /var/www/meet/..."
        sudo rm -rf /var/www/meet/*
        sudo cp -r dist/* /var/www/meet/
        sudo chown -R www-data:www-data /var/www/meet/
        sudo chmod -R 755 /var/www/meet/
        
        echo "Frontend deployed successfully!"
    fi
    
    cd $APP_DIR
fi

# Setup systemd service for Django backend
SERVICE_NAME="meet-django-backend"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Creating Django systemd service..."
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Meetup Django Backend
After=network.target

[Service]
Type=simple
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 meetup_backend.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    echo "Django service created and enabled"
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
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Serve Django static files
    location /static/ {
        alias /var/www/meet/staticfiles/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Serve media files
    location /media/ {
        alias /var/www/meet/media/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Serve JavaScript, CSS, images, fonts, etc. from Vue build
    location ~* \.(?:js|css|ico|json|xml|jpg|jpeg|png|gif|woff|woff2|ttf|svg|map)$ {
        root /var/www/meet;
        access_log off;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
        
        # Fallback for cache busting
        try_files $uri $uri/ =404;
    }
}
EOF

    # Enable the site
    sudo ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/meet.onebitebitcoin.com
    
    # Remove default site if it exists
    sudo rm -f /etc/nginx/sites-enabled/default
    
    sudo nginx -t
    sudo systemctl reload nginx
fi

# Final setup and permissions
echo "=== Final Setup ==="
sudo chown -R www-data:www-data /var/www/meet/
sudo chmod -R 755 /var/www/meet/

# Enable and start nginx site
if [ -f "/etc/nginx/sites-available/meet.onebitebitcoin.com" ]; then
    echo "Enabling Nginx site..."
    sudo ln -sf /etc/nginx/sites-available/meet.onebitebitcoin.com /etc/nginx/sites-enabled/
    sudo systemctl reload nginx
fi

echo "=== Deployment Summary ==="
echo "✅ Django Backend: Running on http://localhost:8000"
echo "✅ Vue Frontend: Deployed to /var/www/meet/"
echo "✅ Nginx: Configured with SSL support"
echo "✅ Systemd Service: meet-django-backend"
echo ""
echo "🔧 Manual Configuration Needed:"
echo "1. Update git repository URL in the script"
echo "2. Configure SSL certificates with Let's Encrypt"
echo "3. Update Django settings for production (DEBUG=False, ALLOWED_HOSTS)"
echo "4. Set up environment variables for database and secrets"
echo ""
echo "📋 Service Management Commands:"
echo "  sudo systemctl status meet-django-backend"
echo "  sudo systemctl restart meet-django-backend"
echo "  sudo systemctl reload nginx"
echo ""
echo "🌐 Site should be accessible at: https://meet.onebitebitcoin.com"
echo "📝 Django admin: https://meet.onebitebitcoin.com/api/admin/"
echo "🔑 Default admin credentials: admin/admin123"
