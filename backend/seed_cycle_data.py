"""
Seed script for Review Cycle Management data.
Populates rating scales, competencies, and templates for testing.

Run: python seed_cycle_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epms.settings')
django.setup()

from apps.cycles.models import RatingScale, Competency, CycleTemplate


def seed_rating_scales():
    """Create predefined rating scales."""
    print("Creating rating scales...")
    
    # 1-5 Numeric Scale
    scale_1_5, created = RatingScale.objects.get_or_create(
        name="1-5 Performance Scale",
        defaults={
            'description': 'Standard 5-point performance rating scale',
            'scale_type': 'numeric',
            'min_value': 1,
            'max_value': 5,
            'scale_points': {
                '1': {
                    'label': 'Below Expectations',
                    'description': 'Performance needs significant improvement',
                    'color': '#ff0000'
                },
                '2': {
                    'label': 'Needs Improvement',
                    'description': 'Performance is below target',
                    'color': '#ff9900'
                },
                '3': {
                    'label': 'Meets Expectations',
                    'description': 'Performance meets all requirements',
                    'color': '#ffff00'
                },
                '4': {
                    'label': 'Exceeds Expectations',
                    'description': 'Performance exceeds requirements',
                    'color': '#90ee90'
                },
                '5': {
                    'label': 'Outstanding',
                    'description': 'Exceptional performance',
                    'color': '#00ff00'
                }
            },
            'usage_guidance': 'Use this scale for all annual performance reviews. Aim for normal distribution.',
            'distribution_guidelines': {
                '1': 5,
                '2': 15,
                '3': 60,
                '4': 15,
                '5': 5
            },
            'is_active': True
        }
    )
    print(f"  {'Created' if created else 'Already exists'}: {scale_1_5.name}")
    
    # Exceeds/Meets/Below Scale
    scale_emb, created = RatingScale.objects.get_or_create(
        name="Exceeds/Meets/Below Scale",
        defaults={
            'description': 'Simple 3-point descriptive performance scale',
            'scale_type': 'descriptive',
            'min_value': 1,
            'max_value': 3,
            'scale_points': {
                '1': {
                    'label': 'Below Expectations',
                    'description': 'Performance needs improvement to meet job requirements',
                    'color': '#ff6b6b'
                },
                '2': {
                    'label': 'Meets Expectations',
                    'description': 'Performance consistently meets all job requirements',
                    'color': '#51cf66'
                },
                '3': {
                    'label': 'Exceeds Expectations',
                    'description': 'Performance consistently exceeds job requirements',
                    'color': '#339af0'
                }
            },
            'usage_guidance': 'Simplified scale for quarterly or probation reviews.',
            'distribution_guidelines': {
                '1': 10,
                '2': 70,
                '3': 20
            },
            'is_active': True
        }
    )
    print(f"  {'Created' if created else 'Already exists'}: {scale_emb.name}")
    
    # Percentage Scale
    scale_pct, created = RatingScale.objects.get_or_create(
        name="0-100% Achievement Scale",
        defaults={
            'description': 'Percentage-based achievement scale',
            'scale_type': 'percentage',
            'min_value': 0,
            'max_value': 100,
            'scale_points': {
                '0-59': {
                    'label': 'Below Target',
                    'description': 'Less than 60% of objectives achieved',
                    'color': '#ff6b6b'
                },
                '60-79': {
                    'label': 'Developing',
                    'description': '60-79% of objectives achieved',
                    'color': '#ffd43b'
                },
                '80-89': {
                    'label': 'Proficient',
                    'description': '80-89% of objectives achieved',
                    'color': '#51cf66'
                },
                '90-100': {
                    'label': 'Exceptional',
                    'description': '90-100% of objectives achieved',
                    'color': '#339af0'
                }
            },
            'usage_guidance': 'Use for goal-oriented performance measurement.',
            'is_active': True
        }
    )
    print(f"  {'Created' if created else 'Already exists'}: {scale_pct.name}")
    
    return scale_1_5, scale_emb, scale_pct


def seed_competencies():
    """Create standard competencies."""
    print("\nCreating competencies...")
    
    competencies_data = [
        {
            'name': 'Leadership',
            'description': 'Ability to lead, motivate, and guide teams toward achieving goals',
            'category': 'leadership',
            'proficiency_levels': [
                {'level': 1, 'name': 'Emerging', 'description': 'Beginning to show leadership qualities'},
                {'level': 2, 'name': 'Developing', 'description': 'Actively developing leadership skills'},
                {'level': 3, 'name': 'Proficient', 'description': 'Consistently demonstrates strong leadership'},
                {'level': 4, 'name': 'Advanced', 'description': 'Excels in leadership role'},
                {'level': 5, 'name': 'Expert', 'description': 'Recognized leader, mentors others'}
            ],
            'behavioral_indicators': {
                '1': ['Shows initiative', 'Supports team decisions'],
                '2': ['Takes on small leadership roles', 'Provides guidance to peers'],
                '3': ['Leads projects successfully', 'Motivates team members'],
                '4': ['Drives organizational change', 'Develops future leaders'],
                '5': ['Strategic vision', 'Transforms organization culture']
            }
        },
        {
            'name': 'Communication',
            'description': 'Ability to effectively convey information and ideas',
            'category': 'communication',
            'proficiency_levels': [
                {'level': 1, 'name': 'Basic', 'description': 'Communicates basic information'},
                {'level': 2, 'name': 'Developing', 'description': 'Communicates clearly in routine situations'},
                {'level': 3, 'name': 'Proficient', 'description': 'Communicates effectively in all situations'},
                {'level': 4, 'name': 'Advanced', 'description': 'Expert communicator across all channels'},
                {'level': 5, 'name': 'Expert', 'description': 'Influential communicator, coaches others'}
            ],
            'behavioral_indicators': {
                '1': ['Responds to emails', 'Participates in meetings'],
                '2': ['Presents information clearly', 'Listens actively'],
                '3': ['Adapts communication style', 'Resolves misunderstandings'],
                '4': ['Influences stakeholders', 'Facilitates difficult conversations'],
                '5': ['Shapes organizational narrative', 'Mentors others in communication']
            }
        },
        {
            'name': 'Problem Solving',
            'description': 'Ability to analyze situations and develop effective solutions',
            'category': 'problem_solving',
            'proficiency_levels': [
                {'level': 1, 'name': 'Basic', 'description': 'Solves straightforward problems'},
                {'level': 2, 'name': 'Developing', 'description': 'Tackles moderately complex problems'},
                {'level': 3, 'name': 'Proficient', 'description': 'Resolves complex problems independently'},
                {'level': 4, 'name': 'Advanced', 'description': 'Solves highly complex, ambiguous problems'},
                {'level': 5, 'name': 'Expert', 'description': 'Develops innovative problem-solving approaches'}
            ],
            'behavioral_indicators': {
                '1': ['Identifies obvious issues', 'Seeks help when stuck'],
                '2': ['Analyzes problems systematically', 'Proposes solutions'],
                '3': ['Thinks critically', 'Implements effective solutions'],
                '4': ['Anticipates problems', 'Creates innovative solutions'],
                '5': ['Strategic problem solver', 'Transforms challenges into opportunities']
            }
        },
        {
            'name': 'Technical Skills',
            'description': 'Job-specific technical knowledge and proficiency',
            'category': 'technical',
            'proficiency_levels': [
                {'level': 1, 'name': 'Novice', 'description': 'Learning core technical skills'},
                {'level': 2, 'name': 'Competent', 'description': 'Capable in core technical areas'},
                {'level': 3, 'name': 'Proficient', 'description': 'Strong technical expertise'},
                {'level': 4, 'name': 'Expert', 'description': 'Technical authority in field'},
                {'level': 5, 'name': 'Master', 'description': 'Industry-recognized technical expert'}
            ],
            'behavioral_indicators': {
                '1': ['Learns new tools', 'Completes basic tasks'],
                '2': ['Works independently on routine tasks', 'Applies best practices'],
                '3': ['Handles complex technical challenges', 'Shares knowledge'],
                '4': ['Innovates technical solutions', 'Mentors others'],
                '5': ['Sets technical direction', 'Industry thought leader']
            }
        },
        {
            'name': 'Teamwork & Collaboration',
            'description': 'Ability to work effectively with others toward common goals',
            'category': 'teamwork',
            'proficiency_levels': [
                {'level': 1, 'name': 'Basic', 'description': 'Participates in team activities'},
                {'level': 2, 'name': 'Developing', 'description': 'Contributes actively to team'},
                {'level': 3, 'name': 'Proficient', 'description': 'Strong team player'},
                {'level': 4, 'name': 'Advanced', 'description': 'Enhances team performance'},
                {'level': 5, 'name': 'Expert', 'description': 'Builds high-performing teams'}
            ],
            'behavioral_indicators': {
                '1': ['Attends team meetings', 'Respects others'],
                '2': ['Shares information', 'Supports team goals'],
                '3': ['Builds relationships', 'Facilitates collaboration'],
                '4': ['Resolves team conflicts', 'Improves team dynamics'],
                '5': ['Creates collaborative culture', 'Develops team capabilities']
            }
        },
        {
            'name': 'Customer Focus',
            'description': 'Commitment to meeting and exceeding customer expectations',
            'category': 'customer_focus',
            'proficiency_levels': [
                {'level': 1, 'name': 'Basic', 'description': 'Responsive to customer needs'},
                {'level': 2, 'name': 'Developing', 'description': 'Understands customer requirements'},
                {'level': 3, 'name': 'Proficient', 'description': 'Anticipates customer needs'},
                {'level': 4, 'name': 'Advanced', 'description': 'Exceeds customer expectations'},
                {'level': 5, 'name': 'Expert', 'description': 'Shapes customer experience strategy'}
            ],
            'behavioral_indicators': {
                '1': ['Responds to customer requests', 'Maintains professional demeanor'],
                '2': ['Understands customer needs', 'Provides quality service'],
                '3': ['Proactively addresses issues', 'Builds customer relationships'],
                '4': ['Drives customer satisfaction', 'Implements improvements'],
                '5': ['Customer experience thought leader', 'Transforms service delivery']
            }
        }
    ]
    
    created_competencies = []
    for comp_data in competencies_data:
        comp, created = Competency.objects.get_or_create(
            name=comp_data['name'],
            defaults={
                'description': comp_data['description'],
                'category': comp_data['category'],
                'proficiency_levels': comp_data['proficiency_levels'],
                'behavioral_indicators': comp_data['behavioral_indicators'],
                'is_active': True
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {comp.name}")
        created_competencies.append(comp)
    
    return created_competencies


def seed_templates(rating_scale, competencies):
    """Create cycle templates."""
    print("\nCreating cycle templates...")
    
    # Annual Review Template
    annual_template, created = CycleTemplate.objects.get_or_create(
        name="Annual Performance Review Template",
        defaults={
            'description': 'Standard template for annual performance reviews',
            'cycle_type': 'annual',
            'default_duration_days': 365,
            'goal_setting_days': 30,
            'self_review_days': 14,
            'manager_review_days': 14,
            'calibration_days': 7,
            'requires_goals': True,
            'requires_self_review': True,
            'requires_manager_review': True,
            'requires_peer_feedback': True,
            'max_peer_feedback': 3,
            'goal_weight_percentage': 70,
            'competency_weight_percentage': 30,
            'default_rating_scale': rating_scale,
            'is_active': True
        }
    )
    print(f"  {'Created' if created else 'Already exists'}: {annual_template.name}")
    
    # Quarterly Review Template
    quarterly_template, created = CycleTemplate.objects.get_or_create(
        name="Quarterly Performance Check-in Template",
        defaults={
            'description': 'Lightweight template for quarterly reviews',
            'cycle_type': 'quarterly',
            'default_duration_days': 90,
            'goal_setting_days': 7,
            'self_review_days': 3,
            'manager_review_days': 3,
            'requires_goals': True,
            'requires_self_review': True,
            'requires_manager_review': True,
            'requires_peer_feedback': False,
            'max_peer_feedback': 0,
            'goal_weight_percentage': 80,
            'competency_weight_percentage': 20,
            'default_rating_scale': rating_scale,
            'is_active': True
        }
    )
    print(f"  {'Created' if created else 'Already exists'}: {quarterly_template.name}")
    
    # Probation Review Template
    probation_template, created = CycleTemplate.objects.get_or_create(
        name="Probation Review Template",
        defaults={
            'description': 'Template for new employee probation reviews',
            'cycle_type': 'probation',
            'default_duration_days': 90,
            'goal_setting_days': 7,
            'self_review_days': 3,
            'manager_review_days': 3,
            'requires_goals': True,
            'requires_self_review': True,
            'requires_manager_review': True,
            'requires_peer_feedback': False,
            'max_peer_feedback': 0,
            'goal_weight_percentage': 60,
            'competency_weight_percentage': 40,
            'default_rating_scale': rating_scale,
            'is_active': True
        }
    )
    print(f"  {'Created' if created else 'Already exists'}: {probation_template.name}")
    
    return [annual_template, quarterly_template, probation_template]


def main():
    """Main seeding function."""
    print("=" * 60)
    print("SEEDING REVIEW CYCLE MANAGEMENT DATA")
    print("=" * 60)
    
    try:
        # Seed rating scales
        rating_scale_1_5, rating_scale_emb, rating_scale_pct = seed_rating_scales()
        
        # Seed competencies
        competencies = seed_competencies()
        
        # Seed templates
        templates = seed_templates(rating_scale_1_5, competencies)
        
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print(f"\nCreated/Verified:")
        print(f"  - {RatingScale.objects.count()} Rating Scales")
        print(f"  - {Competency.objects.count()} Competencies")
        print(f"  - {CycleTemplate.objects.count()} Cycle Templates")
        
        print("\n✅ System is ready for review cycle creation!")
        print("\nNext Steps:")
        print("1. Access admin: http://localhost:8000/admin/")
        print("2. Or use API: http://localhost:8000/docs/")
        print("3. Create cycles from templates or manually")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

