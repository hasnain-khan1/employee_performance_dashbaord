from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Goal, GoalCategory
from .serializers import GoalSerializer, GoalCategorySerializer


class GoalListView(generics.ListCreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]


class GoalCategoryListView(generics.ListCreateAPIView):
    queryset = GoalCategory.objects.all()
    serializer_class = GoalCategorySerializer
    permission_classes = [IsAuthenticated]