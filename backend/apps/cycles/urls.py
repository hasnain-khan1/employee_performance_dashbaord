from django.urls import path
from . import views

app_name = 'cycles'

urlpatterns = [
    # Review cycles (BR-004, BR-005, BR-007)
    path('', views.ReviewCycleListView.as_view(), name='cycle_list'),
    path('<int:pk>/', views.ReviewCycleDetailView.as_view(), name='cycle_detail'),
    path('<int:pk>/activate/', views.activate_cycle, name='cycle_activate'),
    
    # Rating Scales (BR-005)
    path('rating-scales/', views.RatingScaleListView.as_view(), name='rating_scale_list'),
    path('rating-scales/<int:pk>/', views.RatingScaleDetailView.as_view(), name='rating_scale_detail'),
    
    # Competencies
    path('competencies/', views.CompetencyListView.as_view(), name='competency_list'),
    path('competencies/<int:pk>/', views.CompetencyDetailView.as_view(), name='competency_detail'),
    
    # Cycle templates (BR-006)
    path('templates/', views.CycleTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.CycleTemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:pk>/create-cycle/', views.create_from_template, name='template_create_cycle'),
]