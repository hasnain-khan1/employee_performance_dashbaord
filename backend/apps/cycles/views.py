from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import ReviewCycle, CycleTemplate, RatingScale, Competency
from .serializers import (
    ReviewCycleSerializer, CycleTemplateSerializer,
    RatingScaleSerializer, CompetencySerializer
)


class ReviewCycleListView(generics.ListCreateAPIView):
    """
    List and create review cycles.
    Implements BR-004, BR-005, BR-006, BR-007.
    """
    queryset = ReviewCycle.objects.all()
    serializer_class = ReviewCycleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter cycles based on status parameter."""
        queryset = ReviewCycle.objects.all()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class ReviewCycleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a review cycle.
    BR-005: Rating scale lock enforcement during updates.
    """
    queryset = ReviewCycle.objects.all()
    serializer_class = ReviewCycleSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Activate Review Cycle",
    description="Activate a review cycle and lock its rating scale (BR-004, BR-005)",
    request=None,
    responses={200: ReviewCycleSerializer}
)
def activate_cycle(request, pk):
    """
    Activate a review cycle.
    BR-004: Enforces single active cycle policy
    BR-005: Locks the rating scale upon activation
    """
    try:
        cycle = ReviewCycle.objects.get(pk=pk)
        
        # Check permissions (only HR/Admin can activate)
        if request.user.role not in ['hr', 'admin']:
            return Response(
                {'error': 'Only HR administrators can activate cycles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Activate the cycle (this will lock the rating scale)
        try:
            cycle.activate()
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewCycleSerializer(cycle)
        return Response({
            'message': 'Cycle activated successfully. Rating scale is now locked.',
            'cycle': serializer.data
        })
    
    except ReviewCycle.DoesNotExist:
        return Response(
            {'error': 'Review cycle not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class RatingScaleListView(generics.ListCreateAPIView):
    """
    List and create rating scales.
    Available for HR to configure rating options.
    """
    queryset = RatingScale.objects.filter(is_active=True)
    serializer_class = RatingScaleSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Only HR/Admin can create rating scales."""
        if self.request.user.role not in ['hr', 'admin']:
            raise PermissionError('Only HR administrators can create rating scales')
        serializer.save()


class RatingScaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a rating scale.
    """
    queryset = RatingScale.objects.all()
    serializer_class = RatingScaleSerializer
    permission_classes = [IsAuthenticated]


class CompetencyListView(generics.ListCreateAPIView):
    """
    List and create competencies.
    Available for HR to configure competency frameworks.
    """
    queryset = Competency.objects.filter(is_active=True)
    serializer_class = CompetencySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter competencies by category if provided."""
        queryset = Competency.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    def perform_create(self, serializer):
        """Only HR/Admin can create competencies."""
        if self.request.user.role not in ['hr', 'admin']:
            raise PermissionError('Only HR administrators can create competencies')
        serializer.save()


class CompetencyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a competency.
    """
    queryset = Competency.objects.all()
    serializer_class = CompetencySerializer
    permission_classes = [IsAuthenticated]


class CycleTemplateListView(generics.ListCreateAPIView):
    """
    List and create cycle templates.
    BR-006: Cycle templates for efficient recurring review setup.
    """
    queryset = CycleTemplate.objects.filter(is_active=True)
    serializer_class = CycleTemplateSerializer
    permission_classes = [IsAuthenticated]


class CycleTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a cycle template.
    """
    queryset = CycleTemplate.objects.all()
    serializer_class = CycleTemplateSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Create Cycle from Template",
    description="Create a new review cycle from a template (BR-006)",
    request=None,
    responses={201: ReviewCycleSerializer}
)
def create_from_template(request, pk):
    """
    Create a new cycle from a template.
    BR-006: Efficient setup of recurring reviews.
    """
    try:
        template = CycleTemplate.objects.get(pk=pk)
        
        # Check permissions
        if request.user.role not in ['hr', 'admin']:
            return Response(
                {'error': 'Only HR administrators can create cycles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get required data from request
        name = request.data.get('name')
        start_date = request.data.get('start_date')
        
        if not name or not start_date:
            return Response(
                {'error': 'Name and start_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create cycle from template
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        cycle = template.create_cycle(name, start_date_obj, request.user)
        
        serializer = ReviewCycleSerializer(cycle)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except CycleTemplate.DoesNotExist:
        return Response(
            {'error': 'Template not found'},
            status=status.HTTP_404_NOT_FOUND
        )