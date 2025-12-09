# Lincoln Community School Print Request System

A modern, user-friendly web application for managing print requests at Lincoln Community School. Built with Flask and designed for both staff and administrators.

## Features

### For Staff Members
- **Submit Print Requests**: Upload documents and specify printing requirements
- **Track Requests**: Monitor the status of all print requests in real-time
- **Print Credit Management**: View and manage print credit balance
- **Notifications**: Receive instant notifications when request status changes
- **Request History**: Search and filter through past print requests
- **Mobile Friendly**: Full functionality on smartphones and tablets

### For Administrators
- **Request Management**: Review, approve, and process print requests
- **User Management**: Manage staff accounts and credit allocations
- **Dashboard Analytics**: View system statistics and usage reports
- **Status Updates**: Update request status with automatic user notifications
- **Reporting**: Generate comprehensive reports on print usage

### Technical Features
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Notifications**: Bell icon notifications for status updates
- **Search & Filter**: Quickly find requests by number, file name, or status
- **Pagination**: Efficient browsing of large request lists
- **Secure Authentication**: Role-based access control (Staff/Admin)
- **File Management**: Secure document upload and storage
- **Email Notifications**: Automated email alerts for status changes
- **REST API**: Full API access with JWT authentication

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Authentication**: Flask-Login, JWT
- **Email**: Flask-Mail
- **File Handling**: Pillow (image processing)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/print-request-system.git
cd print-request-system
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
flask init-db
flask seed-db  # Creates admin and sample users
```

6. **Run the application**
```bash
flask run
```

Visit `http://localhost:5000` in your browser.

## Default Credentials

After running `flask seed-db`:

**Admin Account:**
- Email: admin@school.edu
- Password: admin123

**Sample Staff Accounts:**
- Email: [teacher-email] / Password: teacher123

**⚠️ Important**: Change these passwords immediately in production!

## Configuration

Key configuration options in `.env`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///dev_print_requests.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@school.edu
MAIL_PASSWORD=your-app-password
```

## Project Structure

```
print-request-system/
├── app/
│   ├── api/              # REST API endpoints
│   ├── routes/           # Web routes
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   ├── utils/            # Helper functions
│   ├── forms.py          # WTForms
│   └── models.py         # Database models
├── uploads/              # User uploaded files
├── config.py             # Configuration
├── run.py                # Application entry point
└── requirements.txt      # Python dependencies
```

## API Documentation

The system includes a REST API for programmatic access. See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for details.

## Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For technical support or questions:
- Email: it@lincolnschool.edu
- Create an issue in the GitHub repository

## Acknowledgments

- Lincoln Community School IT Department
- All staff members who provided feedback during development
- Flask and Python communities

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Developed for**: Lincoln Community School
