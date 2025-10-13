from rest_framework import serializers
from .models import Goal, GoalCategory, GoalUpdate


class GoalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalUpdate
        fields = '__all__'


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'


class GoalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCategory
        fields = '__all__'