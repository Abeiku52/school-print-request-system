import os
from app import create_app, db
from app.models import User, PrintRequest, Notification

# create the app
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """makes db and models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'PrintRequest': PrintRequest,
        'Notification': Notification
    }


@app.cli.command()
def init_db():
    """initialize database tables"""
    db.create_all()
    print('✓ Database initialized')


@app.cli.command()
def migrate_notifications():
    """add notifications table to existing database"""
    try:
        # Create all tables (will only create missing ones)
        db.create_all()
        
        # Verify notifications table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'notifications' in inspector.get_table_names():
            print('✓ Notifications table created successfully')
            
            # Show indexes
            indexes = inspector.get_indexes('notifications')
            print(f'✓ Created {len(indexes)} indexes')
            for idx in indexes:
                print(f"  - Index on: {', '.join(idx['column_names'])}")
        else:
            print('✗ Failed to create notifications table')
    except Exception as e:
        print(f'✗ Error: {str(e)}')


@app.cli.command()
def seed_db():
    """add some sample data for testing"""
    print('Adding sample data...')
    
    # check if admin exists
    admin = User.query.filter_by(email='admin@school.edu').first()
    if not admin:
        admin = User(
            card_id='ADMIN001',
            name='Admin User',
            email='admin@school.edu',
            faculty_department='IT Department',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print('  ✓ Created admin user')
    
    # add some teachers
    teachers = [
        ('ELEM001', 'Sarah Johnson', 'sarah.johnson@school.edu', 'Elementary School'),
        ('MIDDLE001', 'Michael Chen', 'michael.chen@school.edu', 'Middle School'),
        ('HIGH001', 'Emily Rodriguez', 'emily.rodriguez@school.edu', 'High School'),
    ]
    
    for card_id, name, email, dept in teachers:
        if not User.query.filter_by(email=email).first():
            teacher = User(
                card_id=card_id,
                name=name,
                email=email,
                faculty_department=dept,
                is_admin=False
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            print(f'  ✓ Created teacher: {name}')
    
    db.session.commit()
    print('\n✓ Done!')
    print('\nLogin credentials:')
    print('  Admin: admin@school.edu / admin123')
    print('  Teachers: [email] / teacher123')


if __name__ == '__main__':
    app.run(debug=True)
