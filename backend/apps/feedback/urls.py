from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Peer feedback requests
    path('', views.FeedbackRequestListView.as_view(), name='request_list'),
    path('<int:pk>/', views.FeedbackRequestDetailView.as_view(), name='request_detail'),
    path('templates/', views.FeedbackTemplateListView.as_view(), name='template_list'),
    
    # Peer feedback system
    path('peers/', views.get_available_peers, name='available_peers'),
    path('peer-request/', views.create_peer_feedback_request, name='create_peer_request'),
    path('response/', views.FeedbackResponseCreateView.as_view(), name='create_response'),
    path('validate-content/', views.validate_content_policy, name='validate_content'),
    path('statistics/', views.get_feedback_statistics, name='feedback_statistics'),
    path('<int:pk>/cancel/', views.cancel_feedback_request, name='cancel_request'),
    path('<int:pk>/reminder/', views.send_reminder, name='send_reminder'),
    
    # Manager feedback endpoints
    path('manager/', views.ManagerFeedbackListView.as_view(), name='manager_feedback_list'),
    path('manager/<int:pk>/', views.ManagerFeedbackDetailView.as_view(), name='manager_feedback_detail'),
    path('manager/<int:pk>/acknowledge/', views.acknowledge_manager_feedback, name='acknowledge_manager_feedback'),
    
]