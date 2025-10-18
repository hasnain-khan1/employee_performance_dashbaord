"""
URL patterns for the reviews app.

This module contains URL patterns for self-review and manager review management.
"""

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Self-Review URLs
    path('self/', views.SelfReviewListView.as_view(), name='self_review_list'),
    path('self/<int:pk>/', views.SelfReviewDetailView.as_view(), name='self_review_detail'),
    path('self/<int:pk>/submit/', views.submit_self_review, name='submit_self_review'),
    path('self/<int:pk>/auto-save/', views.auto_save_self_review, name='auto_save_self_review'),
    path('self/<int:self_review_id>/sections/<int:pk>/', views.SelfReviewSectionView.as_view(), name='self_review_section'),
    path('self/<int:self_review_id>/evidence/', views.EvidenceLinkView.as_view(), name='evidence_links'),
    
    # Manager Review URLs
    path('manager/', views.ManagerReviewListView.as_view(), name='manager_review_list'),
    path('manager/<int:pk>/', views.ManagerReviewDetailView.as_view(), name='manager_review_detail'),
    path('manager/<int:pk>/submit/', views.submit_manager_review, name='submit_manager_review'),
    path('manager/<int:review_id>/attachments/', views.upload_review_attachment, name='upload_attachment'),
    path('manager/bulk-action/', views.bulk_review_action, name='bulk_review_action'),
    path('manager/statistics/', views.get_review_statistics, name='review_statistics'),
    
    # Employee Dossier URL
    path('dossier/<int:employee_id>/', views.get_employee_dossier, name='employee_dossier'),
    
    # Template URLs
    path('templates/', views.SelfReviewTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.SelfReviewTemplateDetailView.as_view(), name='template_detail'),
]