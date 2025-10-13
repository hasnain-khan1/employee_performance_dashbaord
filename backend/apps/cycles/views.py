from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ReviewCycle, CycleTemplate
from .serializers import ReviewCycleSerializer, CycleTemplateSerializer


class ReviewCycleListView(generics.ListCreateAPIView):
    queryset = ReviewCycle.objects.all()
    serializer_class = ReviewCycleSerializer
    permission_classes = [IsAuthenticated]


class ReviewCycleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReviewCycle.objects.all()
    serializer_class = ReviewCycleSerializer
    permission_classes = [IsAuthenticated]


class CycleTemplateListView(generics.ListCreateAPIView):
    queryset = CycleTemplate.objects.all()
    serializer_class = CycleTemplateSerializer
    permission_classes = [IsAuthenticated]