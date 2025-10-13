from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('dashboards/', views.DashboardListView.as_view(), name='dashboard_list'),
    path('metrics/', views.MetricListView.as_view(), name='metric_list'),
    
    # Dashboard statistics endpoints
    path('dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    path('employee-stats/', views.employee_dashboard_stats, name='employee_dashboard_stats'),
    path('manager-stats/', views.manager_dashboard_stats, name='manager_dashboard_stats'),
    path('hr-stats/', views.hr_dashboard_stats, name='hr_dashboard_stats'),
]