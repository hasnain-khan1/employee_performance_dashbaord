from django.urls import path
from . import views

app_name = 'cycles'

urlpatterns = [
    path('', views.ReviewCycleListView.as_view(), name='cycle_list'),
    path('<int:pk>/', views.ReviewCycleDetailView.as_view(), name='cycle_detail'),
    path('templates/', views.CycleTemplateListView.as_view(), name='template_list'),
]