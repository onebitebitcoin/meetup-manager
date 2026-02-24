#!/bin/bash

set -e

echo "Starting Ubuntu server deployment..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "Installing essential packages..."
sudo apt install -y curl wget git build-essential software-properties-common python3 python3-pip python3-venv psmisc net-tools

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

# Setup directories
FRONTEND_DEPLOY_DIR="/var/www/meet"
MEDIA_DEPLOY_DIR="/var/www/meet/media"
CURRENT_DIR=$(pwd)

echo "Current directory: $CURRENT_DIR"
echo "Creating frontend deployment directory: $FRONTEND_DEPLOY_DIR"
sudo mkdir -p $FRONTEND_DEPLOY_DIR
sudo chown -R $USER:$USER $FRONTEND_DEPLOY_DIR

# Deploy Django Backend
echo "=== Deploying Django Backend ==="
if [ -f "backend/requirements.txt" ]; then
    echo "Setting up Python virtual environment..."
    cd backend
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

    echo "Copying static files to frontend deployment directory..."
    sudo mkdir -p $FRONTEND_DEPLOY_DIR/staticfiles
    sudo cp -r staticfiles/* $FRONTEND_DEPLOY_DIR/staticfiles/ 2>/dev/null || true
    sudo mkdir -p $FRONTEND_DEPLOY_DIR/media
    sudo cp -r media/* $FRONTEND_DEPLOY_DIR/media/ 2>/dev/null || true

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
    cd $CURRENT_DIR
fi

# Deploy Vue Frontend
echo "=== Deploying Vue Frontend ==="
FRONTEND_DIR="frontend"
if [ -d "$FRONTEND_DIR" ]; then
    echo "Building Vue frontend..."
    cd $FRONTEND_DIR
    
    if [ -f "package.json" ]; then
        echo "Installing Node.js dependencies..."
        npm install
        
        echo "Building production build..."
        npm run build
        
        echo "Deploying to $FRONTEND_DEPLOY_DIR..."
        # Preserve media directory while removing other content
        sudo mkdir -p $FRONTEND_DEPLOY_DIR/media/meetups
        if [ -d "$FRONTEND_DEPLOY_DIR/media" ]; then
            echo "Backing up existing media files..."
            sudo cp -r $FRONTEND_DEPLOY_DIR/media /tmp/meet-media-backup 2>/dev/null || true
        fi
        
        # Remove all files except media directory
        sudo find $FRONTEND_DEPLOY_DIR -mindepth 1 -maxdepth 1 ! -name 'media' -exec rm -rf {} +
        
        # Deploy new frontend files
        sudo cp -r dist/* $FRONTEND_DEPLOY_DIR/
        
        # Restore media directory if it was backed up
        if [ -d "/tmp/meet-media-backup" ]; then
            echo "Restoring media files..."
            sudo cp -r /tmp/meet-media-backup $FRONTEND_DEPLOY_DIR/media
            sudo rm -rf /tmp/meet-media-backup
        fi
        sudo chown -R www-data:www-data $FRONTEND_DEPLOY_DIR/
        sudo chmod -R 755 $FRONTEND_DEPLOY_DIR/
        
        echo "Frontend deployed successfully!"
    fi
    
    cd $CURRENT_DIR
fi

# Setup systemd service for Django backend
SERVICE_NAME="meet-django-backend"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creating/updating Django systemd service..."
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Meetup Django Backend
After=network.target

[Service]
Type=simple
User=$USER
Group=www-data
WorkingDirectory=$CURRENT_DIR/backend
Environment="PATH=$CURRENT_DIR/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$CURRENT_DIR/backend"
Environment="DJANGO_SETTINGS_MODULE=meetup_backend.settings_production"
Environment="MEDIA_ROOT=$MEDIA_DEPLOY_DIR"
ExecStart=$CURRENT_DIR/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 meetup_backend.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
TimeoutStartSec=30
PrivateTmp=true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
echo "Django service created and enabled"

# Start/restart the service
echo "=== Starting Django Backend Service ==="
echo "Stopping existing service if running..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

echo "Starting Django backend service..."
sudo systemctl start $SERVICE_NAME

# Wait for service to start
sleep 3

echo "Checking service status..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Django service is running successfully"
    sudo systemctl status $SERVICE_NAME --no-pager
else
    echo "❌ Django service failed to start. Checking logs..."
    sudo journalctl -u $SERVICE_NAME --no-pager -n 20
    
    # Try to start manually as fallback
    echo "Attempting manual start as fallback..."
    cd $CURRENT_DIR/backend
    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=meetup_backend.settings_production
    export MEDIA_ROOT=$MEDIA_DEPLOY_DIR

    # Kill any existing processes on port 8000
    sudo fuser -k 8000/tcp 2>/dev/null || true
    sleep 2

    # Start Gunicorn manually in background
    echo "Starting Gunicorn manually on port 8000..."
    nohup $CURRENT_DIR/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 meetup_backend.wsgi:application > /var/log/gunicorn.log 2>&1 &

    # Wait and check if port 8000 is responding
    sleep 5
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        echo "Django backend started manually on port 8000"
    else
        echo "Failed to start Django backend. Trying development server..."
        # Kill gunicorn and try development server
        sudo fuser -k 8000/tcp 2>/dev/null || true
        sleep 2
        nohup python manage.py runserver 0.0.0.0:8000 > /var/log/django-dev.log 2>&1 &
        sleep 3
        if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
            echo "✅ Django development server started on port 8000"
        else
            echo "❌ All startup methods failed. Check logs:"
            echo "  - systemd: sudo journalctl -u $SERVICE_NAME"
            echo "  - gunicorn: tail -f /var/log/gunicorn.log"
            echo "  - django: tail -f /var/log/django-dev.log"
        fi
    fi
    deactivate
fi

# Setup Nginx configuration (basic example)
NGINX_CONFIG="/etc/nginx/sites-available/meet.onebitebitcoin.com"
echo "Configuring Nginx reverse proxy..."
sudo bash -c "cat > $NGINX_CONFIG" <<EOF
server {
    listen 80 ;
    server_name meet.onebitebitcoin.com;

    location ~ /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
        allow all;
        try_files \$uri =404;
    }

    location / {
        return 301 https://\$host\$request_uri;
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
    root $FRONTEND_DEPLOY_DIR;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Serve Django static files
    location /static/ {
        alias $FRONTEND_DEPLOY_DIR/staticfiles/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Serve media files
    location ^~ /media/ {
        alias /var/www/meet/media/;
        try_files \$uri =404;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Serve JavaScript, CSS, images, fonts, etc. from Vue build
    location ~* \.(?:js|css|ico|json|xml|jpg|jpeg|png|gif|woff|woff2|ttf|svg|map)$ {
        root $FRONTEND_DEPLOY_DIR;
        access_log off;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
        
        # Fallback for cache busting
        try_files \$uri \$uri/ =404;
    }
}
EOF

# Enable the site
sudo ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/meet.onebitebitcoin.com

# Remove default site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl reload nginx

# Final setup and permissions
echo "=== Final Setup ==="
sudo chown -R www-data:www-data $FRONTEND_DEPLOY_DIR/
sudo chmod -R 755 $FRONTEND_DEPLOY_DIR/
sudo mkdir -p $MEDIA_DEPLOY_DIR/task_submissions
sudo chown -R www-data:www-data $MEDIA_DEPLOY_DIR
sudo find $MEDIA_DEPLOY_DIR -type d -exec chmod 755 {} +
sudo find $MEDIA_DEPLOY_DIR -type f -exec chmod 644 {} +

# Enable and start nginx site
if [ -f "/etc/nginx/sites-available/meet.onebitebitcoin.com" ]; then
    echo "Enabling Nginx site..."
    sudo ln -sf /etc/nginx/sites-available/meet.onebitebitcoin.com /etc/nginx/sites-enabled/
    sudo systemctl reload nginx
fi

echo "=== Final Verification ==="
echo "Checking if Django backend is running on port 8000..."
if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo "✅ Port 8000 is active"
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        echo "✅ Django backend health check passed"
    else
        echo "⚠️  Port 8000 active but health check failed"
    fi
else
    echo "❌ Port 8000 is not active"
    echo "Checking what's running on port 8000..."
    sudo lsof -i :8000 || echo "No process found on port 8000"
fi

echo "Checking direct media access (sample file if available)..."
SAMPLE_MEDIA_FILE=$(find $MEDIA_DEPLOY_DIR/task_submissions -type f | head -n 1 || true)
if [ -n "$SAMPLE_MEDIA_FILE" ]; then
    SAMPLE_MEDIA_URL_PATH=${SAMPLE_MEDIA_FILE#/var/www/meet}
    echo "Sample media HEAD request: https://meet.onebitebitcoin.com$SAMPLE_MEDIA_URL_PATH"
    curl --max-time 5 -I "https://meet.onebitebitcoin.com$SAMPLE_MEDIA_URL_PATH" || true
else
    echo "No sample task submission media file found; skipping media HEAD check"
fi

echo ""
echo "=== Deployment Summary ==="
BACKEND_STATUS="❌ Not Running"
if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    BACKEND_STATUS="✅ Running on http://localhost:8000"
fi

echo "🔧 Django Backend: $BACKEND_STATUS"
echo "✅ Vue Frontend: Deployed to $FRONTEND_DEPLOY_DIR/"
echo "✅ Repository: Working from $CURRENT_DIR/"
echo "✅ Nginx: Configured with SSL support"
echo "✅ Systemd Service: meet-django-backend"
echo ""
echo "🔧 Manual Configuration Needed:"
echo "1. Configure SSL certificates with Let's Encrypt"
echo "2. Update Django settings for production (DEBUG=False, ALLOWED_HOSTS)"
echo "3. Set up environment variables for database and secrets"
echo ""
echo "📋 Service Management Commands:"
echo "  sudo systemctl status meet-django-backend"
echo "  sudo systemctl restart meet-django-backend"
echo "  sudo systemctl reload nginx"
echo "  sudo journalctl -u meet-django-backend -f  # View logs"
echo ""
echo "🔍 Debugging Commands:"
echo "  netstat -tlnp | grep :8000  # Check port 8000"
echo "  curl http://localhost:8000/api/health/  # Test backend"
echo "  tail -f /var/log/gunicorn.log  # Gunicorn logs"
echo "  tail -f /var/log/django-dev.log  # Django dev server logs"
echo ""
echo "🌐 Site should be accessible at: https://meet.onebitebitcoin.com"
echo "📝 Django admin: https://meet.onebitebitcoin.com/api/admin/"
echo "🔑 Default admin credentials: admin/admin123"
