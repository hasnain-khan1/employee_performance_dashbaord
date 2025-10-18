from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    # Employee Goal Management
    path('', views.GoalListView.as_view(), name='goal_list'),
    path('<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('categories/', views.GoalCategoryListView.as_view(), name='category_list'),
    
    # Goal submission for approval
    path('<int:goal_id>/submit/', views.submit_goal_for_approval, name='submit_goal'),
    
    # Manager Goal Review (BR-017, BR-018, BR-019, BR-020, BR-021)
    path('manager/team/', views.get_manager_goals, name='manager_team_goals'),
    path('<int:goal_id>/review/', views.submit_goal_review, name='submit_goal_review'),
    path('<int:goal_id>/approve/', views.approve_goal, name='approve_goal'),
    path('<int:goal_id>/history/', views.get_goal_history, name='goal_history'),
    path('bulk-feedback/', views.submit_bulk_feedback, name='bulk_feedback'),
]