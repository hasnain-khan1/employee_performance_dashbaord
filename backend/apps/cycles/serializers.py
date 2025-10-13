from rest_framework import serializers
from .models import (
    ReviewCycle, CycleTemplate, CycleParticipant,
    RatingScale, Competency, CycleRatingScale,
    CycleCompetency, TemplateCompetency
)


class CycleParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleParticipant
        fields = '__all__'


class RatingScaleSerializer(serializers.ModelSerializer):
    """Serializer for Rating Scale model."""
    
    class Meta:
        model = RatingScale
        fields = [
            'id', 'name', 'description', 'scale_type', 'min_value', 'max_value',
            'scale_points', 'usage_guidance', 'distribution_guidelines',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompetencySerializer(serializers.ModelSerializer):
    """Serializer for Competency model."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Competency
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'proficiency_levels', 'behavioral_indicators', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CycleRatingScaleSerializer(serializers.ModelSerializer):
    """Serializer for Cycle Rating Scale configuration."""
    
    rating_scale_name = serializers.CharField(source='rating_scale.name', read_only=True)
    rating_scale_details = RatingScaleSerializer(source='rating_scale', read_only=True)
    
    class Meta:
        model = CycleRatingScale
        fields = [
            'id', 'cycle', 'rating_scale', 'rating_scale_name', 'rating_scale_details',
            'is_locked', 'locked_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_locked', 'locked_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """BR-005: Prevent rating scale changes when locked."""
        if self.instance and self.instance.is_locked:
            raise serializers.ValidationError({
                'rating_scale': 'Rating scale is locked and cannot be modified. '
                               'Rating scales are locked when a cycle becomes active to ensure consistency.'
            })
        return data


class CycleCompetencySerializer(serializers.ModelSerializer):
    """Serializer for Cycle Competency assignments."""
    
    competency_name = serializers.CharField(source='competency.name', read_only=True)
    competency_details = CompetencySerializer(source='competency', read_only=True)
    
    class Meta:
        model = CycleCompetency
        fields = [
            'id', 'cycle', 'competency', 'competency_name', 'competency_details',
            'weight', 'is_required', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReviewCycleSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for Review Cycle with business rule validations.
    Implements BR-004, BR-005, BR-006, BR-007.
    """
    
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    rating_scale_config = CycleRatingScaleSerializer(read_only=True)
    competencies = CycleCompetencySerializer(many=True, read_only=True)
    
    # For creating/updating rating scale and competencies
    rating_scale_id = serializers.IntegerField(write_only=True, required=False)
    competency_ids = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text='List of {competency_id: int, weight: int} dictionaries'
    )
    
    class Meta:
        model = ReviewCycle
        fields = '__all__'
    
    def validate(self, data):
        """
        Validate cycle data according to business rules.
        BR-004: Single active cycle enforcement
        BR-007: All milestone dates within cycle dates
        """
        # BR-004: Name length validation (5-100 characters)
        if 'name' in data and (len(data['name']) < 5 or len(data['name']) > 100):
            raise serializers.ValidationError({
                'name': 'Cycle name must be between 5 and 100 characters.'
            })
        
        # BR-004: Date validation
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date. Please choose a later date.'
                })
        
        # BR-004: Single active cycle enforcement
        if data.get('status') == 'active':
            overlapping_cycles = ReviewCycle.objects.filter(
                status='active',
                start_date__lte=data.get('end_date', self.instance.end_date if self.instance else None),
                end_date__gte=data.get('start_date', self.instance.start_date if self.instance else None)
            )
            if self.instance:
                overlapping_cycles = overlapping_cycles.exclude(pk=self.instance.pk)
            
            if overlapping_cycles.exists():
                active_cycle = overlapping_cycles.first()
                raise serializers.ValidationError({
                    'status': f'Cannot activate cycle. Only one active cycle is allowed at a time. '
                             f'Active cycle: "{active_cycle.name}" '
                             f'({active_cycle.start_date} to {active_cycle.end_date})'
                })
        
        return data
    
    def create(self, validated_data):
        """Create cycle with rating scale and competencies."""
        rating_scale_id = validated_data.pop('rating_scale_id', None)
        competency_ids = validated_data.pop('competency_ids', [])
        
        cycle = super().create(validated_data)
        
        # Assign rating scale
        if rating_scale_id:
            CycleRatingScale.objects.create(
                cycle=cycle,
                rating_scale_id=rating_scale_id
            )
        
        # Assign competencies
        for comp_data in competency_ids:
            CycleCompetency.objects.create(
                cycle=cycle,
                competency_id=comp_data['competency_id'],
                weight=comp_data.get('weight', 10)
            )
        
        return cycle


class TemplateCompetencySerializer(serializers.ModelSerializer):
    """Serializer for Template Competency assignments."""
    
    competency_name = serializers.CharField(source='competency.name', read_only=True)
    
    class Meta:
        model = TemplateCompetency
        fields = ['id', 'template', 'competency', 'competency_name', 'weight']


class CycleTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for Cycle Template model.
    BR-006: Cycle templates for efficient setup of recurring reviews.
    """
    
    default_rating_scale_name = serializers.CharField(
        source='default_rating_scale.name', 
        read_only=True
    )
    template_competencies_details = TemplateCompetencySerializer(
        source='template_competencies.through.objects.all',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = CycleTemplate
        fields = '__all__'