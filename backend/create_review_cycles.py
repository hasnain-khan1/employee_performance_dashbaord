#!/usr/bin/env python
"""
Script to create review cycles for testing.
"""
import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epms.settings')
django.setup()

from apps.cycles.models import ReviewCycle, CycleTemplate, CycleParticipant
from apps.accounts.models import User

def create_review_cycles():
    """Create sample review cycles."""
    print("Creating review cycles...")
    
    # Get the first template (should exist from seed data)
    template = CycleTemplate.objects.first()
    if not template:
        print("❌ No cycle templates found. Please run seed_cycle_data.py first.")
        return
    
    # Create an active annual review cycle
    current_date = date.today()
    
    # Get the first user as creator
    creator = User.objects.first()
    if not creator:
        print("❌ No users found. Please run create_test_users.py first.")
        return
    
    annual_cycle, created = ReviewCycle.objects.get_or_create(
        name="2025 Annual Performance Review",
        defaults={
            'description': 'Annual performance review cycle for 2025',
            'cycle_type': 'annual',
            'start_date': current_date,
            'end_date': current_date + timedelta(days=90),
            'goal_setting_start': current_date,
            'goal_setting_end': current_date + timedelta(days=7),
            'self_review_start': current_date + timedelta(days=7),
            'self_review_end': current_date + timedelta(days=30),
            'manager_review_start': current_date + timedelta(days=30),
            'manager_review_end': current_date + timedelta(days=45),
            'calibration_start': current_date + timedelta(days=45),
            'calibration_end': current_date + timedelta(days=60),
            'is_active': True,
            'status': 'active',
            'created_by': creator,
            'requires_goals': True,
            'requires_self_review': True,
            'requires_manager_review': True,
            'requires_peer_feedback': True
        }
    )
    
    if created:
        print(f"✅ Created: {annual_cycle.name}")
    else:
        print(f"📋 Already exists: {annual_cycle.name}")
    
    # Create a quarterly cycle
    quarterly_cycle, created = ReviewCycle.objects.get_or_create(
        name="Q1 2025 Quarterly Review",
        defaults={
            'description': 'Q1 2025 quarterly performance review',
            'cycle_type': 'quarterly',
            'start_date': current_date,
            'end_date': current_date + timedelta(days=30),
            'goal_setting_start': current_date,
            'goal_setting_end': current_date + timedelta(days=3),
            'self_review_start': current_date + timedelta(days=3),
            'self_review_end': current_date + timedelta(days=15),
            'manager_review_start': current_date + timedelta(days=15),
            'manager_review_end': current_date + timedelta(days=20),
            'calibration_start': current_date + timedelta(days=20),
            'calibration_end': current_date + timedelta(days=25),
            'is_active': False,  # Not active, just for testing
            'status': 'planning',
            'created_by': creator,
            'requires_goals': True,
            'requires_self_review': True,
            'requires_manager_review': True,
            'requires_peer_feedback': False
        }
    )
    
    if created:
        print(f"✅ Created: {quarterly_cycle.name}")
    else:
        print(f"📋 Already exists: {quarterly_cycle.name}")
    
    # Assign all users to the active cycle
    users = User.objects.all()
    for user in users:
        CycleParticipant.objects.get_or_create(
            cycle=annual_cycle,
            employee=user,
            defaults={
                'is_active': True,
                'self_review_completed': False,
                'manager_review_completed': False,
                'goals_set': False
            }
        )
    
    print(f"✅ Assigned {users.count()} users to the active cycle")
    
    print("\n" + "="*60)
    print("REVIEW CYCLES CREATED!")
    print("="*60)
    print(f"Active cycles: {ReviewCycle.objects.filter(is_active=True).count()}")
    print(f"Total cycles: {ReviewCycle.objects.count()}")
    print("\n✅ Self-review endpoint should now work!")

if __name__ == '__main__':
    create_review_cycles()
