# Lincoln Community School Print Request System - Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL or MySQL (for production)
- Web server (Nginx/Apache)
- SSL Certificate

### Environment Setup

1. **Create Production Environment File**
```bash
cp .env.example .env
```

2. **Configure Production Settings**
```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/printrequest_db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@school.edu
MAIL_PASSWORD=your-app-password
```

### Database Migration

```bash
# Initialize database
flask init-db

# Run migrations
flask migrate-notifications

# Create admin user
flask seed-db
```

### Production Server (Gunicorn)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name printrequest.school.edu;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/app/static;
        expires 30d;
    }
}
```

### Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Enable HTTPS with SSL certificate
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring

### Backup Strategy

```bash
# Database backup
pg_dump printrequest_db > backup_$(date +%Y%m%d).sql

# File uploads backup
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### Monitoring

- Set up application logging
- Monitor server resources
- Track error rates
- Monitor database performance
- Set up alerts for critical issues

## 📱 Mobile Optimization

The system is fully responsive and optimized for:
- iOS Safari
- Android Chrome
- Mobile browsers
- Tablet devices

## 🔧 Maintenance

### Regular Tasks
- Weekly database backups
- Monthly security updates
- Quarterly performance reviews
- Annual SSL certificate renewal

### Support Contact
For technical support, contact: it@school.edu
