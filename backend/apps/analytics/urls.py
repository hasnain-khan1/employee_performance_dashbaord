from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('dashboards/', views.DashboardListView.as_view(), name='dashboard_list'),
    path('metrics/', views.MetricListView.as_view(), name='metric_list'),
]