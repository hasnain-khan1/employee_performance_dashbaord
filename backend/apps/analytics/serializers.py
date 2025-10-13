"""
Serializers for the analytics app.

This module contains serializers for reports, dashboards, and metrics.
"""

from rest_framework import serializers
from .models import Report, Dashboard, Metric
from apps.accounts.serializers import UserListSerializer


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model.
    
    Provides full report information including
    configuration and file details.
    """
    
    created_by = UserListSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'status',
            'parameters', 'file_path', 'file_size', 'created_by',
            'created_by_id', 'generated_at', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'generated_at', 'file_size'
        ]


class ReportListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing reports.
    """
    
    created_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'status',
            'created_by', 'generated_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'generated_at']


class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for Dashboard model.
    
    Manages dashboard configuration and layout.
    """
    
    owner = UserListSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'owner', 'owner_id',
            'is_public', 'configuration', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing dashboards.
    """
    
    owner = UserListSerializer(read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'owner',
            'is_public', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MetricSerializer(serializers.ModelSerializer):
    """
    Serializer for Metric model.
    
    Manages performance metrics and KPIs.
    """
    
    class Meta:
        model = Metric
        fields = [
            'id', 'name', 'description', 'metric_type',
            'calculation_method', 'unit', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MetricListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing metrics.
    """
    
    class Meta:
        model = Metric
        fields = [
            'id', 'name', 'metric_type', 'unit',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

