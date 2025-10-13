"""
Views for the reviews app.

This module contains API views for performance review management.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from django.utils import timezone

from .models import Review, ReviewSection, ReviewTemplate
from .serializers import (
    ReviewSerializer, ReviewListSerializer,
    ReviewSectionSerializer, ReviewTemplateSerializer,
    ReviewTemplateListSerializer
)


class ReviewListView(generics.ListCreateAPIView):
    """
    Review list and creation endpoint.
    
    Provides list of reviews with filtering,
    and allows creation of new reviews.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return ReviewListSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        """Get filtered queryset of reviews."""
        user = self.request.user
        queryset = Review.objects.select_related(
            'employee', 'reviewer', 'cycle'
        ).prefetch_related('sections')
        
        # Filter based on user role
        view_type = self.request.query_params.get('view')
        if view_type == 'employee':
            queryset = queryset.filter(employee=user)
        elif view_type == 'reviewer':
            queryset = queryset.filter(reviewer=user)
        else:
            # Default: show all reviews where user is involved
            queryset = queryset.filter(
                Q(employee=user) | Q(reviewer=user)
            )
        
        # Filter by review type
        review_type = self.request.query_params.get('type')
        if review_type:
            queryset = queryset.filter(review_type=review_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by cycle
        cycle = self.request.query_params.get('cycle')
        if cycle:
            queryset = queryset.filter(cycle_id=cycle)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set reviewer to current user if not specified."""
        if not serializer.validated_data.get('reviewer_id'):
            serializer.save(reviewer=self.request.user)
        else:
            serializer.save()
    
    @extend_schema(
        summary="List Reviews",
        description="Get a list of reviews with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='view',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by view type: "employee" or "reviewer"'
            ),
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by review type: "self", "manager", "peer", "360"'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='cycle',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by cycle ID'
            ),
        ],
        responses={
            200: ReviewListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of reviews."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Review",
        description="Create a new review.",
        responses={
            201: ReviewSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new review."""
        return super().post(request, *args, **kwargs)


class ReviewDetailView(generics.RetrieveUpdateAPIView):
    """
    Review detail endpoint.
    
    Provides detailed information about a specific review
    and allows updates to content and status.
    """
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get queryset filtered by user involvement."""
        user = self.request.user
        return Review.objects.filter(
            Q(employee=user) | Q(reviewer=user) | Q(employee__manager=user)
        )
    
    @extend_schema(
        summary="Get Review Details",
        description="Retrieve detailed information about a specific review.",
        responses={
            200: ReviewSerializer,
            404: "Review not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get review details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Review",
        description="Update a review's content or status.",
        responses={
            200: ReviewSerializer,
            400: "Validation error",
            404: "Review not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update review."""
        review = self.get_object()
        
        # Update submitted_at when status changes to submitted
        if request.data.get('status') == 'submitted' and review.status != 'submitted':
            request.data['submitted_at'] = timezone.now()
        
        # Update approved_at when status changes to approved
        if request.data.get('status') == 'approved' and review.status != 'approved':
            request.data['approved_at'] = timezone.now()
        
        return super().patch(request, *args, **kwargs)


class ReviewTemplateListView(generics.ListCreateAPIView):
    """
    Review template list and creation endpoint.
    
    Provides list of review templates and allows creation
    of new templates (HR only).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return ReviewTemplateListSerializer
        return ReviewTemplateSerializer
    
    def get_queryset(self):
        """Get queryset of active review templates."""
        queryset = ReviewTemplate.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by review type
        review_type = self.request.query_params.get('type')
        if review_type:
            queryset = queryset.filter(review_type=review_type)
        
        return queryset.order_by('name')
    
    @extend_schema(
        summary="List Review Templates",
        description="Get a list of review templates.",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by review type'
            ),
        ],
        responses={
            200: ReviewTemplateListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of review templates."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Review Template",
        description="Create a new review template (HR only).",
        responses={
            201: ReviewTemplateSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new review template."""
        # Check if user is HR or admin
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can create review templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class ReviewTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Review template detail endpoint.
    
    Provides detailed information about a specific template
    and allows updates (HR only).
    """
    
    serializer_class = ReviewTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ReviewTemplate.objects.all()
    lookup_field = 'pk'
    
    @extend_schema(
        summary="Get Review Template Details",
        description="Retrieve detailed information about a specific review template.",
        responses={
            200: ReviewTemplateSerializer,
            404: "Template not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get review template details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Review Template",
        description="Update a review template (HR only).",
        responses={
            200: ReviewTemplateSerializer,
            400: "Validation error",
            404: "Template not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update review template."""
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can update review templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Review Template",
        description="Delete a review template (HR only).",
        responses={
            204: "Template deleted",
            404: "Template not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete review template."""
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can delete review templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)

