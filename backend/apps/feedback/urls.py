from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.FeedbackRequestListView.as_view(), name='request_list'),
    path('<int:pk>/', views.FeedbackRequestDetailView.as_view(), name='request_detail'),
    path('templates/', views.FeedbackTemplateListView.as_view(), name='template_list'),
]