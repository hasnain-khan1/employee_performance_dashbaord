"""
Seed script for SMART Goal Templates and Business Objectives.
Populates goal templates with inline guidance for employees.

Run: python seed_goal_templates.py
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epms.settings')
django.setup()

from apps.goals.models import GoalTemplate, GoalCategory, BusinessObjective
from apps.org.models import Department


def seed_goal_categories():
    """Create goal categories."""
    print("Creating goal categories...")
    
    categories_data = [
        {
            'name': 'Revenue & Growth',
            'description': 'Goals related to revenue generation, sales, and business growth',
            'color': '#28a745'
        },
        {
            'name': 'Customer Success',
            'description': 'Goals focused on customer satisfaction, retention, and support',
            'color': '#17a2b8'
        },
        {
            'name': 'Operational Excellence',
            'description': 'Goals related to process improvement, efficiency, and cost reduction',
            'color': '#ffc107'
        },
        {
            'name': 'Product Development',
            'description': 'Goals for product features, quality, and innovation',
            'color': '#6f42c1'
        },
        {
            'name': 'Team Development',
            'description': 'Goals for team building, training, and professional growth',
            'color': '#fd7e14'
        },
        {
            'name': 'Technical Excellence',
            'description': 'Goals related to technical skills, code quality, and architecture',
            'color': '#20c997'
        },
    ]
    
    created_categories = []
    for cat_data in categories_data:
        cat, created = GoalCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'color': cat_data['color'],
                'is_active': True
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {cat.name}")
        created_categories.append(cat)
    
    return created_categories


def seed_goal_templates(categories):
    """Create SMART goal templates."""
    print("\nCreating SMART goal templates...")
    
    # Map categories by name for easy lookup
    cat_map = {cat.name: cat for cat in categories}
    
    templates_data = [
        {
            'name': 'Increase Sales Revenue',
            'description': 'Template for setting revenue growth goals',
            'goal_type': 'performance',
            'category': cat_map['Revenue & Growth'],
            'specific_template': 'Increase sales revenue in [target market/product line] by focusing on [specific strategy]',
            'measurable_template': 'Achieve ${target_amount} in revenue, representing a {percentage}% increase from current ${current_amount}',
            'achievable_template': 'This goal is achievable through [specific actions: new customer acquisition, upselling, market expansion]',
            'relevant_template': 'This goal aligns with the company objective to [business objective] and contributes to [team/department goal]',
            'time_bound_template': 'Complete by {target_date}, with quarterly milestones of ${Q1}, ${Q2}, ${Q3}, ${Q4}',
            'guidance': 'When setting revenue goals, consider historical performance, market conditions, and available resources. Break down annual targets into quarterly milestones for better tracking.',
            'example': 'Increase sales revenue in the enterprise segment by 25% ($500K to $625K) through targeted outreach to Fortune 500 companies, completing by December 31, 2025.'
        },
        {
            'name': 'Improve Customer Satisfaction',
            'description': 'Template for customer satisfaction and NPS goals',
            'goal_type': 'performance',
            'category': cat_map['Customer Success'],
            'specific_template': 'Improve customer satisfaction for [customer segment] by implementing [specific improvements]',
            'measurable_template': 'Increase NPS score from {current_score} to {target_score} and reduce churn rate to below {target_percentage}%',
            'achievable_template': 'This goal is achievable by [specific initiatives: faster response times, proactive support, feature improvements]',
            'relevant_template': 'This goal supports our company mission of [mission] and directly impacts customer retention and lifetime value',
            'time_bound_template': 'Achieve by {target_date}, with monthly NPS surveys and quarterly reviews',
            'guidance': 'Focus on measurable metrics like NPS, CSAT, or churn rate. Identify specific pain points and create actionable improvement plans.',
            'example': 'Increase NPS score from 45 to 65 by implementing a new customer onboarding program and reducing average response time to under 2 hours, completing by Q4 2025.'
        },
        {
            'name': 'Launch New Product Feature',
            'description': 'Template for product development and launch goals',
            'goal_type': 'project',
            'category': cat_map['Product Development'],
            'specific_template': 'Successfully launch [feature name] that provides [specific value] to [target users]',
            'measurable_template': 'Complete development of {number} features, achieve {percentage}% test coverage, and reach {number} active users within {timeframe} of launch',
            'achievable_template': 'This goal is achievable with the current team of {number} developers and {timeline} development cycle',
            'relevant_template': 'This feature addresses customer feedback requesting [need] and supports our product roadmap goal of [objective]',
            'time_bound_template': 'Complete beta by {date1}, launch to production by {date2}, and achieve adoption targets by {date3}',
            'guidance': 'Define clear success criteria including technical metrics (test coverage, performance) and user adoption metrics. Include buffer time for testing and iterations.',
            'example': 'Launch advanced reporting dashboard with 10 customizable widgets, achieve 95% test coverage, and reach 500 active users within 30 days, completing by September 30, 2025.'
        },
        {
            'name': 'Reduce Operational Costs',
            'description': 'Template for cost reduction and efficiency goals',
            'goal_type': 'performance',
            'category': cat_map['Operational Excellence'],
            'specific_template': 'Reduce operational costs in [specific area] by optimizing [specific processes/resources]',
            'measurable_template': 'Decrease costs from ${current_amount} to ${target_amount}, achieving {percentage}% reduction',
            'achievable_template': 'This goal is achievable through [specific strategies: automation, vendor negotiation, process optimization]',
            'relevant_template': 'This goal contributes to the company profitability objective and allows reallocation of resources to [priority area]',
            'time_bound_template': 'Implement changes by {date1}, measure impact by {date2}, and achieve full savings by {target_date}',
            'guidance': 'Identify specific cost centers and quantify current spending. Ensure cost reductions don\'t negatively impact quality or customer experience.',
            'example': 'Reduce cloud infrastructure costs from $50K to $35K monthly (30% reduction) by implementing auto-scaling and optimizing resource allocation, completing by August 31, 2025.'
        },
        {
            'name': 'Improve Team Productivity',
            'description': 'Template for productivity and efficiency improvement goals',
            'goal_type': 'performance',
            'category': cat_map['Operational Excellence'],
            'specific_template': 'Improve team productivity in [specific area] by implementing [specific tools/processes]',
            'measurable_template': 'Increase output from {current_metric} to {target_metric}, or reduce time spent on {activity} by {percentage}%',
            'achievable_template': 'This goal is achievable through [specific actions: automation, training, process improvement, tool adoption]',
            'relevant_template': 'This goal aligns with the efficiency initiative and enables the team to [additional capability]',
            'time_bound_template': 'Pilot solution by {date1}, roll out to full team by {date2}, and measure results by {target_date}',
            'guidance': 'Define clear productivity metrics (tasks completed, cycle time, output quality). Consider both quantitative metrics and team satisfaction.',
            'example': 'Reduce code review cycle time from 48 hours to 24 hours by implementing automated checks and clear review guidelines, completing by July 15, 2025.'
        },
        {
            'name': 'Develop Technical Skills',
            'description': 'Template for professional development and learning goals',
            'goal_type': 'development',
            'category': cat_map['Technical Excellence'],
            'specific_template': 'Master [specific skill/technology] to [level of proficiency] by completing [specific learning activities]',
            'measurable_template': 'Complete {number} courses/certifications, build {number} projects, and achieve [certification/assessment score]',
            'achievable_template': 'This goal is achievable with {hours_per_week} hours per week of dedicated learning time over {number_of_months} months',
            'relevant_template': 'This skill development supports [current role requirements] and prepares me for [career goal]',
            'time_bound_template': 'Complete coursework by {date1}, build projects by {date2}, and obtain certification by {target_date}',
            'guidance': 'Choose skills aligned with career goals and company needs. Include hands-on projects to apply learning. Track progress with certificates, projects, or assessments.',
            'example': 'Master AWS cloud architecture by completing AWS Solutions Architect certification, building 3 production-ready projects, and migrating 2 services to cloud, completing by December 2025.'
        },
        {
            'name': 'Build Team Capability',
            'description': 'Template for team development and mentoring goals',
            'goal_type': 'development',
            'category': cat_map['Team Development'],
            'specific_template': 'Develop team capabilities in [specific area] by providing [specific development activities]',
            'measurable_template': 'Train {number} team members, conduct {number} workshops, and achieve {metric} improvement in team performance',
            'achievable_template': 'This goal is achievable with {time_commitment} hours per month for mentoring and {budget} for training resources',
            'relevant_template': 'This goal supports team growth objectives and builds capacity for [future initiatives]',
            'time_bound_template': 'Conduct training sessions monthly, complete skill assessments quarterly, and achieve proficiency targets by {target_date}',
            'guidance': 'Define specific skills to develop and how you\'ll measure improvement. Balance formal training with hands-on mentoring.',
            'example': 'Train 5 junior developers in advanced React patterns through weekly workshops and code reviews, achieving 80% proficiency score on assessment, completing by October 2025.'
        },
        {
            'name': 'Improve Code Quality',
            'description': 'Template for technical excellence and code quality goals',
            'goal_type': 'performance',
            'category': cat_map['Technical Excellence'],
            'specific_template': 'Improve code quality in [codebase/module] by implementing [specific practices/standards]',
            'measurable_template': 'Increase test coverage from {current}% to {target}%, reduce bug count by {percentage}%, and achieve code quality score of {score}',
            'achievable_template': 'This goal is achievable by dedicating {percentage}% of sprint capacity to quality improvements and adopting [specific tools]',
            'relevant_template': 'This goal reduces technical debt and supports long-term maintainability of our [product/platform]',
            'time_bound_template': 'Implement standards by {date1}, reach coverage targets by {date2}, and achieve quality score by {target_date}',
            'guidance': 'Use objective metrics like test coverage, code complexity, bug density. Combine automated tools with code review practices.',
            'example': 'Increase test coverage from 60% to 85%, reduce production bugs by 40%, and achieve SonarQube score of A, completing by November 2025.'
        },
        {
            'name': 'Complete Project Milestone',
            'description': 'Template for project-based goals with clear deliverables',
            'goal_type': 'project',
            'category': cat_map['Product Development'],
            'specific_template': 'Complete [project name] delivering [specific deliverables] for [stakeholders]',
            'measurable_template': 'Deliver {number} features, meet {number} acceptance criteria, and achieve {percentage}% stakeholder satisfaction',
            'achievable_template': 'This project is achievable with current team resources and {timeline} project duration, assuming [key dependencies] are met',
            'relevant_template': 'This project supports [strategic initiative] and enables [business capability]',
            'time_bound_template': 'Complete Phase 1 by {date1}, Phase 2 by {date2}, and final delivery by {target_date}',
            'guidance': 'Break large projects into clear phases with concrete deliverables. Identify dependencies and risks. Include stakeholder approval criteria.',
            'example': 'Complete mobile app redesign delivering 5 new features, meeting all UX requirements, and achieving 90% user satisfaction score, completing by August 2025.'
        },
        {
            'name': 'Expand Market Presence',
            'description': 'Template for market expansion and growth goals',
            'goal_type': 'stretch',
            'category': cat_map['Revenue & Growth'],
            'specific_template': 'Expand into [new market/segment] by establishing [specific market presence]',
            'measurable_template': 'Acquire {number} new customers, achieve ${revenue_target} in new market revenue, and reach {market_share}% market share',
            'achievable_template': 'This goal is achievable through [specific strategies: partnerships, marketing campaigns, sales team expansion]',
            'relevant_template': 'This expansion aligns with our growth strategy and diversifies revenue streams',
            'time_bound_template': 'Launch in new market by {date1}, achieve first customers by {date2}, and reach revenue targets by {target_date}',
            'guidance': 'Conduct market research to set realistic targets. Consider cultural differences, regulations, and competitive landscape.',
            'example': 'Expand into European market by partnering with 3 regional distributors, acquiring 50 new customers, and achieving €200K in revenue, completing by Q4 2025.'
        }
    ]
    
    created_templates = []
    for template_data in templates_data:
        template, created = GoalTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults={
                'description': template_data['description'],
                'goal_type': template_data['goal_type'],
                'category': template_data['category'],
                'specific_template': template_data['specific_template'],
                'measurable_template': template_data['measurable_template'],
                'achievable_template': template_data['achievable_template'],
                'relevant_template': template_data['relevant_template'],
                'time_bound_template': template_data['time_bound_template'],
                'guidance': template_data['guidance'],
                'example': template_data['example'],
                'is_active': True
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {template.name}")
        created_templates.append(template)
    
    return created_templates


def seed_business_objectives():
    """Create sample business objectives for alignment."""
    print("\nCreating business objectives...")
    
    objectives_data = [
        {
            'name': 'Achieve 50% Revenue Growth',
            'description': 'Grow company revenue from $2M to $3M annually',
            'priority': 'critical',
            'target_date': date.today() + timedelta(days=365),
            'status': 'active'
        },
        {
            'name': 'Launch New Product Line',
            'description': 'Successfully launch enterprise product tier with advanced features',
            'priority': 'high',
            'target_date': date.today() + timedelta(days=180),
            'status': 'active'
        },
        {
            'name': 'Improve Customer Retention',
            'description': 'Reduce churn rate from 15% to below 8%',
            'priority': 'high',
            'target_date': date.today() + timedelta(days=270),
            'status': 'active'
        },
        {
            'name': 'Build Engineering Excellence',
            'description': 'Establish world-class engineering practices and culture',
            'priority': 'medium',
            'target_date': date.today() + timedelta(days=365),
            'status': 'active'
        },
        {
            'name': 'Expand to International Markets',
            'description': 'Launch in 3 new international markets',
            'priority': 'medium',
            'target_date': date.today() + timedelta(days=300),
            'status': 'planning'
        }
    ]
    
    created_objectives = []
    for obj_data in objectives_data:
        obj, created = BusinessObjective.objects.get_or_create(
            name=obj_data['name'],
            defaults={
                'description': obj_data['description'],
                'priority': obj_data['priority'],
                'target_date': obj_data['target_date'],
                'status': obj_data['status'],
                'is_active': True
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {obj.name}")
        created_objectives.append(obj)
    
    return created_objectives


def main():
    """Main seeding function."""
    print("=" * 60)
    print("SEEDING SMART GOAL TEMPLATES AND BUSINESS OBJECTIVES")
    print("=" * 60)
    
    try:
        # Seed goal categories
        categories = seed_goal_categories()
        
        # Seed goal templates
        templates = seed_goal_templates(categories)
        
        # Seed business objectives
        objectives = seed_business_objectives()
        
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print(f"\nCreated/Verified:")
        print(f"  - {GoalCategory.objects.count()} Goal Categories")
        print(f"  - {GoalTemplate.objects.count()} SMART Goal Templates")
        print(f"  - {BusinessObjective.objects.count()} Business Objectives")
        
        print("\n✅ System is ready for SMART goal creation!")
        print("\nNext Steps:")
        print("1. Employees can create goals using templates")
        print("2. Templates provide inline guidance for SMART criteria")
        print("3. Goals can be aligned to business objectives")
        print("4. Access API: http://localhost:8000/docs/")
        
        print("\n📚 Goal Templates Available:")
        for template in templates:
            print(f"  - {template.name} ({template.goal_type})")
        
        print("\n🎯 Business Objectives Available:")
        for objective in objectives:
            print(f"  - {objective.name} ({objective.priority} priority)")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

