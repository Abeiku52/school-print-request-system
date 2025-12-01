# 🖨️ School Print Request System

A professional web application for managing print requests in educational institutions with print credit tracking and REST API.

## ✨ Features

### Core Features
- 📝 **Print Request Management** - Submit and track print jobs
- 👨‍💼 **Admin Dashboard** - Comprehensive management interface
- 💳 **Print Credit System** - Track and manage user print credits
- 📧 **Email Notifications** - Automatic status update notifications
- 👤 **User Profiles** - Customizable profiles with avatars
- 📊 **Credit Transactions** - Complete transaction history

### REST API
- 🔌 **RESTful API** - Full API access with JWT authentication
- 📚 **API Documentation** - Complete API docs included
- 🔐 **Secure Authentication** - JWT token-based auth
- 📈 **Statistics Endpoint** - System-wide statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/Abeiku52/school-print-request-system.git
cd school-print-request-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask init-db
flask seed-db

# Run application
python run.py
```

Visit http://localhost:5000

## 🔑 Default Credentials

**Administrator:**
- Email: `admin@school.edu`
- Password: `admin123`
- Starting Credit: 100.0

**Teacher:**
- Email: `sarah.johnson@school.edu`
- Password: `teacher123`
- Starting Credit: 100.0

⚠️ Change these in production!

## 💳 Print Credit System

- Each user has a print credit balance
- Credits are deducted when print jobs are processed
- Admins can add/deduct credits
- Complete transaction history tracking
- Low credit warnings

## 🔌 REST API

Full REST API with JWT authentication. See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details.

**Quick Example:**
```bash
# Login
curl -X POST http://localhost:5000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@school.edu","password":"admin123"}'

# Get users (use token from login)
curl -X GET http://localhost:5000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**API Endpoints:**
- `POST /api/v1/login` - Get auth token
- `GET /api/v1/users` - List users
- `POST /api/v1/users/<id>/credit` - Manage credits
- `GET /api/v1/users/<id>/transactions` - Credit history
- `GET /api/v1/requests` - List print requests
- `GET /api/v1/stats` - System statistics

## 📁 Project Structure

```
school-print-request-system/
├── app/
│   ├── api/                # REST API
│   │   ├── auth.py        # JWT authentication
│   │   ├── routes.py      # API endpoints
│   │   └── errors.py      # Error handlers
│   ├── routes/            # Web routes
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, images
│   ├── utils/             # Helper functions
│   ├── models.py          # Database models
│   └── forms.py           # Form definitions
├── uploads/               # User files
├── config.py             # Configuration
├── run.py                # Entry point
└── requirements.txt      # Dependencies
```

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (upgradable to PostgreSQL)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login + JWT
- **Email:** Flask-Mail
- **API:** RESTful with JWT tokens
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5

## 📧 Email Setup (Optional)

Create a `.env` file:

```bash
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourschool.edu
```

For Gmail, generate an [App Password](https://support.google.com/accounts/answer/185833).

## 🌐 Deployment

### Heroku

```bash
heroku create your-app-name
git push heroku main
heroku run flask init-db
heroku run flask seed-db
```

### Environment Variables

Set these in production:
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `MAIL_USERNAME` - Email username
- `MAIL_PASSWORD` - Email password

## 📊 Database Models

- **User** - User accounts with credit balance
- **PrintRequest** - Print job requests
- **CreditTransaction** - Credit transaction history

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file

## 🐛 Issues

Found a bug? [Open an issue](https://github.com/Abeiku52/school-print-request-system/issues)

## 📞 Support

For questions or support, open an issue on GitHub.

---

**Built with ❤️ for educational institutions**
