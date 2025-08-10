# Production Deployment Guide

## Image Upload - Production Readiness ✅

The image upload functionality is now **production-ready** with the following improvements:

### ✅ Fixed Issues

1. **Removed hardcoded URLs** - Now uses dynamic URL generation
2. **Added file validation** - File size limits, extension validation
3. **Improved security** - Secure file naming, path generation
4. **Added production settings** - Separate configuration for production

### 🚀 Production Deployment Steps

#### 1. Settings Configuration
The settings are already configured for your domain `https://meet.onebitebitcoin.com`

#### 2. Install Production Dependencies
```bash
pip install -r requirements.txt
# This includes gunicorn and whitenoise
```

#### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 4. Collect Static Files
```bash
python manage.py collectstatic
```

#### 5. Run with Production Settings
```bash
# Development
python manage.py runserver --settings=meetup_backend.settings

# Production
gunicorn meetup_backend.wsgi:application --settings=meetup_backend.settings_production
```

### 🔧 Environment Variables for Production

Create a `.env` file or set these environment variables:

```bash
# Required
DJANGO_SETTINGS_MODULE=meetup_backend.settings_production
SECRET_KEY=your-super-secret-key-here
SITE_URL=https://meet.onebitebitcoin.com

# Database (optional - defaults to SQLite)
DB_NAME=meetup_db
DB_USER=meetup_user  
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# AWS S3 (optional - for cloud storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

### 📁 File Storage Options

#### Option 1: Local File Storage (Current)
- Files stored in `media/` directory
- ✅ Simple setup
- ❌ Not scalable for multiple servers

#### Option 2: Cloud Storage (Recommended for Production)
Uncomment the AWS S3 settings in `settings_production.py` and install:
```bash
pip install django-storages boto3
```

### 🛡️ Security Features Added

1. **File Size Validation**: Max 5MB per image
2. **File Type Validation**: Only jpg, jpeg, png, gif, webp allowed
3. **Secure File Naming**: Auto-generated names with timestamps
4. **Path Security**: Files stored in organized directory structure

### 🔍 Testing Production Setup

1. **Test Image Upload**:
   ```bash
   curl -X POST https://meet.onebitebitcoin.com/api/meetups/ \
     -F "name=Test Meetup" \
     -F "description=Test" \
     -F "date_time=2024-08-15T15:00:00Z" \
     -F "location=Test Location" \
     -F "max_participants=10" \
     -F "image=@test_image.jpg"
   ```

2. **Check Image URLs**: Verify they return full absolute URLs like:
   ```json
   {
     "image_display_url": "https://meet.onebitebitcoin.com/media/meetups/Test_Meetup_1723291234.jpg"
   }
   ```

### 🚨 Production Considerations

1. **Reverse Proxy**: Use nginx to serve static/media files
2. **CDN**: Use CloudFlare or AWS CloudFront for better performance
3. **Backup**: Regular backups of media files
4. **Monitoring**: Monitor disk space for uploaded files
5. **Cleanup**: Implement cleanup of unused images

### 📝 Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name meet.onebitebitcoin.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name meet.onebitebitcoin.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    
    location /media/ {
        alias /path/to/your/project/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

The image upload functionality is now **fully production-ready**! 🎉