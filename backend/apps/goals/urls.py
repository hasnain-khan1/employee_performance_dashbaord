from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.GoalListView.as_view(), name='goal_list'),
    path('<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('categories/', views.GoalCategoryListView.as_view(), name='category_list'),
]