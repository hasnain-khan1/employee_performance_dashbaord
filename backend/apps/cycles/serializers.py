from rest_framework import serializers
from .models import ReviewCycle, CycleTemplate, CycleParticipant


class CycleParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleParticipant
        fields = '__all__'


class ReviewCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewCycle
        fields = '__all__'


class CycleTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleTemplate
        fields = '__all__'