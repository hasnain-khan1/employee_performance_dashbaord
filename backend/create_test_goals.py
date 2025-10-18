#!/usr/bin/env python
"""
Script to create test goals for employees.
"""
import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epms.settings')
django.setup()

from apps.accounts.models import User
from apps.goals.models import Goal, GoalCategory
from apps.cycles.models import ReviewCycle

def create_test_goals():
    """Create test goals for employees."""
    
    print("Creating test goals...\n")
    
    # Get users
    try:
        employee1 = User.objects.get(username='employee1')
        employee2 = User.objects.get(username='employee2')
        manager1 = User.objects.get(username='manager1')
    except User.DoesNotExist as e:
        print(f"❌ User not found: {e}")
        return
    
    # Create or get a review cycle
    cycle, created = ReviewCycle.objects.get_or_create(
        name="Q4 2024 Performance Cycle",
        defaults={
            'start_date': datetime.now().date() - timedelta(days=30),
            'end_date': datetime.now().date() + timedelta(days=30),
            'goal_setting_start': datetime.now().date() - timedelta(days=30),
            'goal_setting_end': datetime.now().date() + timedelta(days=15),
            'self_review_start': datetime.now().date() + timedelta(days=15),
            'self_review_end': datetime.now().date() + timedelta(days=25),
            'manager_review_start': datetime.now().date() + timedelta(days=25),
            'manager_review_end': datetime.now().date() + timedelta(days=30),
            'created_by': manager1
        }
    )
    
    if created:
        print(f"✅ Created review cycle: {cycle.name}")
    else:
        print(f"✅ Using existing review cycle: {cycle.name}")
    
    # Create goal categories if they don't exist
    categories_data = [
        {'name': 'Technical Skills', 'description': 'Goals related to technical development'},
        {'name': 'Project Delivery', 'description': 'Goals related to project completion'},
        {'name': 'Team Collaboration', 'description': 'Goals related to teamwork and communication'},
    ]
    
    for cat_data in categories_data:
        category, created = GoalCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Created goal category: {category.name}")
    
    # Create goals for employee1
    goals_employee1 = [
        {
            'title': 'Complete React Training Course',
            'description': 'Finish the advanced React course and implement learnings in current project',
            'target_value': 100,
            'current_value': 75,
            'unit': 'percentage',
            'target_date': datetime.now().date() + timedelta(days=30),
            'priority': 'high',
            'status': 'in_progress'
        },
        {
            'title': 'Lead Q4 Feature Development',
            'description': 'Take ownership of the new user dashboard feature development',
            'target_value': 1,
            'current_value': 0,
            'unit': 'features',
            'target_date': datetime.now().date() + timedelta(days=45),
            'priority': 'high',
            'status': 'draft'
        },
        {
            'title': 'Improve Code Review Process',
            'description': 'Implement automated code quality checks and improve review turnaround time',
            'target_value': 50,
            'current_value': 20,
            'unit': 'percentage',
            'target_date': datetime.now().date() + timedelta(days=20),
            'priority': 'medium',
            'status': 'in_progress'
        }
    ]
    
    # Create goals for employee2
    goals_employee2 = [
        {
            'title': 'Mentor Junior Developers',
            'description': 'Provide guidance and support to 2 junior team members',
            'target_value': 2,
            'current_value': 1,
            'unit': 'developers',
            'target_date': datetime.now().date() + timedelta(days=60),
            'priority': 'high',
            'status': 'in_progress'
        },
        {
            'title': 'Optimize Database Performance',
            'description': 'Reduce query response time by 30% for critical database operations',
            'target_value': 30,
            'current_value': 10,
            'unit': 'percentage',
            'target_date': datetime.now().date() + timedelta(days=40),
            'priority': 'high',
            'status': 'submitted'
        },
        {
            'title': 'Complete AWS Certification',
            'description': 'Pass the AWS Solutions Architect Associate certification',
            'target_value': 1,
            'current_value': 0,
            'unit': 'certifications',
            'target_date': datetime.now().date() + timedelta(days=90),
            'priority': 'medium',
            'status': 'draft'
        }
    ]
    
    # Create goals for employee1
    for goal_data in goals_employee1:
        goal, created = Goal.objects.get_or_create(
            title=goal_data['title'],
            employee=employee1,
            defaults={
                **goal_data,
                'cycle': cycle,
                'created_by': employee1
            }
        )
        if created:
            print(f"✅ Created goal for {employee1.username}: {goal.title}")
        else:
            print(f"ℹ️  Goal already exists for {employee1.username}: {goal.title}")
    
    # Create goals for employee2
    for goal_data in goals_employee2:
        goal, created = Goal.objects.get_or_create(
            title=goal_data['title'],
            employee=employee2,
            defaults={
                **goal_data,
                'cycle': cycle,
                'created_by': employee2
            }
        )
        if created:
            print(f"✅ Created goal for {employee2.username}: {goal.title}")
        else:
            print(f"ℹ️  Goal already exists for {employee2.username}: {goal.title}")
    
    print(f"\n✅ Test goals created successfully!")
    print(f"   Employee1 ({employee1.username}): {Goal.objects.filter(employee=employee1).count()} goals")
    print(f"   Employee2 ({employee2.username}): {Goal.objects.filter(employee=employee2).count()} goals")
    print(f"   Total goals: {Goal.objects.count()}")

if __name__ == '__main__':
    create_test_goals()
