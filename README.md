# School Print Request System

A web app for managing print requests at schools. Teachers submit print jobs, admins approve them.

## Features

- Submit print requests with file upload
- Admin dashboard for approvals
- Email notifications
- User profiles
- Request tracking

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
flask init-db
flask seed-db

# Run
python run.py
```

Visit http://localhost:5000

## Login

**Admin:**
- Email: admin@school.edu
- Password: admin123

**Teacher:**
- Email: sarah.johnson@school.edu
- Password: teacher123

## Tech Stack

- Flask
- SQLite
- Bootstrap

## License

MIT
