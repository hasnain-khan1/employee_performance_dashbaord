#!/usr/bin/env python
"""
Script to create test users for all roles in the EPMS system.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epms.settings')
django.setup()

from apps.accounts.models import User

def create_test_users():
    """Create test users for all roles."""
    
    users_data = [
        {
            'username': 'employee1',
            'email': 'employee1@example.com',
            'password': 'Employee123!',
            'employee_id': 'EMP000100',
            'role': 'employee',
            'first_name': 'John',
            'last_name': 'Employee',
            'job_title': 'Software Engineer',
            'manager_username': 'manager1'  # Will be set after manager is created
        },
        {
            'username': 'employee2',
            'email': 'employee2@example.com',
            'password': 'Employee123!',
            'employee_id': 'EMP000101',
            'role': 'employee',
            'first_name': 'Jane',
            'last_name': 'Developer',
            'job_title': 'Senior Software Engineer',
            'manager_username': 'manager1'  # Will be set after manager is created
        },
        {
            'username': 'manager1',
            'email': 'manager1@example.com',
            'password': 'Manager123!',
            'employee_id': 'EMP000200',
            'role': 'manager',
            'first_name': 'Sarah',
            'last_name': 'Manager',
            'job_title': 'Engineering Manager'
        },
        {
            'username': 'hr1',
            'email': 'hr1@example.com',
            'password': 'HR123!',
            'employee_id': 'EMP000300',
            'role': 'hr',
            'first_name': 'Mike',
            'last_name': 'HR',
            'job_title': 'HR Manager'
        },
        {
            'username': 'admin1',
            'email': 'admin1@example.com',
            'password': 'Admin123!',
            'employee_id': 'EMP000400',
            'role': 'admin',
            'first_name': 'Jane',
            'last_name': 'Admin',
            'job_title': 'System Administrator',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    print("Creating test users...\n")
    
    # First pass: Create all users without manager relationships
    created_users = {}
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"❌ User '{username}' already exists. Skipping.")
            created_users[username] = User.objects.get(username=username)
            continue
        
        # Check if employee_id already exists
        if User.objects.filter(employee_id=user_data['employee_id']).exists():
            print(f"❌ Employee ID '{user_data['employee_id']}' already exists. Skipping.")
            continue
        
        # Create user
        password = user_data.pop('password')
        manager_username = user_data.pop('manager_username', None)
        is_staff = user_data.pop('is_staff', False)
        is_superuser = user_data.pop('is_superuser', False)
        
        user = User.objects.create_user(
            password=password,
            **user_data
        )
        
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        
        created_users[username] = user
        
        print(f"✅ Created {user_data['role'].upper()} user:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Employee ID: {user_data['employee_id']}")
        print(f"   Email: {user_data['email']}")
        print()
    
    # Second pass: Set up manager relationships
    print("Setting up manager relationships...\n")
    
    for user_data in users_data:
        username = user_data['username']
        manager_username = user_data.get('manager_username')
        
        if manager_username and username in created_users and manager_username in created_users:
            user = created_users[username]
            manager = created_users[manager_username]
            user.manager = manager
            user.save()
            print(f"✅ Set {username} as direct report of {manager_username}")
    
    print()
    
    print("\n" + "="*60)
    print("Test users created successfully!")
    print("="*60)
    print("\nYou can now log in with these credentials:")
    print("\nEmployee: username=employee1, password=Employee123!")
    print("Manager:  username=manager1,  password=Manager123!")
    print("HR:       username=hr1,       password=HR123!")
    print("Admin:    username=admin1,    password=Admin123!")
    print("\n" + "="*60)

if __name__ == '__main__':
    create_test_users()

