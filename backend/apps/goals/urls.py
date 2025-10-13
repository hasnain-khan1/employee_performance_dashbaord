from django.urls import path
from . import views
from . import manager_views

app_name = 'goals'

urlpatterns = [
    # Employee Goal Management
    path('', views.GoalListView.as_view(), name='goal_list'),
    path('<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('categories/', views.GoalCategoryListView.as_view(), name='category_list'),
    
    # Manager Goal Review (BR-017, BR-018, BR-019, BR-020, BR-021)
    path('manager/team/', manager_views.ManagerTeamGoalsView.as_view(), name='manager_team_goals'),
    path('manager/stats/', manager_views.manager_goal_stats, name='manager_goal_stats'),
    path('<int:goal_id>/approve/', manager_views.approve_goal, name='approve_goal'),
    path('<int:goal_id>/request-changes/', manager_views.request_goal_changes, name='request_goal_changes'),
    path('<int:goal_id>/feedback/', manager_views.add_goal_feedback, name='add_goal_feedback'),
    path('<int:goal_id>/feedback/history/', manager_views.goal_feedback_history, name='goal_feedback_history'),
    path('<int:goal_id>/versions/', manager_views.goal_version_history, name='goal_version_history'),
]