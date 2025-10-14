from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Peer feedback requests
    path('', views.FeedbackRequestListView.as_view(), name='request_list'),
    path('<int:pk>/', views.FeedbackRequestDetailView.as_view(), name='request_detail'),
    path('templates/', views.FeedbackTemplateListView.as_view(), name='template_list'),
    
    # Manager-to-employee feedback
    path('manager/', views.ManagerFeedbackListView.as_view(), name='manager_feedback_list'),
    path('manager/<int:pk>/', views.ManagerFeedbackDetailView.as_view(), name='manager_feedback_detail'),
    path('manager/<int:pk>/acknowledge/', views.acknowledge_feedback, name='acknowledge_feedback'),
]