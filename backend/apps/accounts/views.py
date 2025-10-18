"""
Views for the accounts app.

This module contains views for user authentication, registration,
profile management, and employee dashboard functionality.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiTypes
from drf_spectacular.types import OpenApiTypes

from .models import User
from .serializers import UserSerializer, UserListSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain pair view with additional user data."""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Get the user from the token payload instead of request.user
            # The token contains the user ID, so we can fetch the user
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = response.data.get('access')
                if access_token:
                    token = AccessToken(access_token)
                    user_id = token.get('user_id')
                    if user_id:
                        user = User.objects.get(id=user_id)
                        response.data['user'] = {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'full_name': user.get_full_name(),
                            'role': user.role,
                            'is_hr': user.is_hr,
                            'is_manager': user.is_manager,
                            'is_admin': user.is_admin
                        }
            except (User.DoesNotExist, Exception) as e:
                # If we can't get user data, just return the tokens without user data
                print(f"Error getting user data: {e}")
                pass
        return response


class UserRegistrationView(generics.CreateAPIView):
    """User registration view."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create a new user with error handling."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle specific database errors
            if 'UNIQUE constraint failed' in str(e):
                if 'employee_id' in str(e):
                    return Response({
                        'error': 'Employee ID already exists. Please try again.',
                        'detail': 'A user with this employee ID already exists in the system.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif 'username' in str(e):
                    return Response({
                        'error': 'Username already exists.',
                        'detail': 'Please choose a different username.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif 'email' in str(e):
                    return Response({
                        'error': 'Email already exists.',
                        'detail': 'An account with this email already exists.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generic error handling
            return Response({
                'error': 'Registration failed.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileExtendedView(generics.RetrieveUpdateAPIView):
    """Extended user profile view with additional fields."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password view."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'})


class PasswordResetView(APIView):
    """Password reset view."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # In a real application, you would send an email here
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserListView(generics.ListAPIView):
    """List users. HR and Admin see all users, Managers see their direct reports."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_hr or user.is_admin:
            return User.objects.all()
        elif user.is_manager:
            # Managers can see their direct reports
            return User.objects.filter(manager=user)
        return User.objects.none()


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update user profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        # Get the user ID from the URL
        user_id = self.kwargs.get('id')
        if user_id:
            return get_object_or_404(User, id=user_id)
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@extend_schema(
    summary="Register User",
    description="Register a new user account.",
    request=UserRegistrationSerializer,
    responses={
        201: UserSerializer,
        400: "Validation error"
    }
)
def register_view(request):
    """Register a new user."""
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Handle specific database errors
        if 'UNIQUE constraint failed' in str(e):
            if 'employee_id' in str(e):
                return Response({
                    'error': 'Employee ID already exists. Please try again.',
                    'detail': 'A user with this employee ID already exists in the system.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif 'username' in str(e):
                return Response({
                    'error': 'Username already exists.',
                    'detail': 'Please choose a different username.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in str(e):
                return Response({
                    'error': 'Email already exists.',
                    'detail': 'An account with this email already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generic error handling
        return Response({
            'error': 'Registration failed.',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Logout User",
    description="Logout the current user by blacklisting the refresh token.",
        responses={
        200: "Logout successful",
        400: "Bad request"
    }
)
def logout_view(request):
    """
    Logout user by blacklisting the refresh token.
    
    This endpoint accepts a refresh token and adds it to the blacklist,
    preventing it from being used to generate new access tokens.
    """
    try:
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        
        # Try to blacklist the token
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            # Token might be invalid or already blacklisted, but that's ok for logout
            # We still want to return success so the frontend can clear local storage
            print(f"Token blacklist error: {e}")
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Even if there's an error, we still want to allow logout on the frontend
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Employee Dashboard Data",
    description="Get comprehensive dashboard data for the current employee including progress, deadlines, and action items.",
        responses={
        200: OpenApiTypes.OBJECT,
            401: "Authentication required"
        }
    )
def get_employee_dashboard_data(request):
    """
    Get comprehensive dashboard data for the current employee.
    Includes progress tracking, deadlines, action items, and recent activity.
    """
    try:
        user = request.user
        
        # Initialize dashboard data
        dashboard_data = {
            'employee': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'position': user.job_title,
                'department': user.department.name if user.department else None,
                'avatar': user.avatar.url if user.avatar else None
            },
            'progress': {
                'goals_completion': 0,
                'self_review_completion': 0,
                'peer_feedback_completion': 0,
                'overall_completion': 0
            },
            'deadlines': [],
            'action_items': [],
            'recent_activity': [],
            'statistics': {
                'completed_items': 0,
                'in_progress_items': 0,
                'overdue_items': 0,
                'upcoming_items': 0
            }
        }
        
        # Get goals progress
        from apps.goals.models import Goal
        goals = Goal.objects.filter(employee=user)
        if goals.exists():
            completed_goals = goals.filter(status='completed').count()
            dashboard_data['progress']['goals_completion'] = round((completed_goals / goals.count()) * 100)
        
        # Get self-review progress
        from apps.reviews.models import SelfReview
        try:
            self_review = SelfReview.objects.filter(employee=user).latest('created_at')
            dashboard_data['progress']['self_review_completion'] = self_review.completion_percentage or 0
        except SelfReview.DoesNotExist:
            pass
        
        # Get peer feedback progress
        from apps.feedback.models import FeedbackRequest
        feedback_requests = FeedbackRequest.objects.filter(requester=user)
        if feedback_requests.exists():
            completed_requests = feedback_requests.filter(status='completed').count()
            dashboard_data['progress']['peer_feedback_completion'] = round((completed_requests / feedback_requests.count()) * 100)
        
        # Calculate overall completion
        progress_values = [
            dashboard_data['progress']['goals_completion'],
            dashboard_data['progress']['self_review_completion'],
            dashboard_data['progress']['peer_feedback_completion']
        ]
        dashboard_data['progress']['overall_completion'] = round(sum(progress_values) / len(progress_values))
        
        # Get deadlines and action items
        action_items = []
        urgent_deadlines = []
        
        # Goals action items
        incomplete_goals = goals.filter(status__in=['draft', 'in_progress'])
        for goal in incomplete_goals:
            days_until_deadline = (goal.target_date - timezone.now().date()).days
            priority = 'high' if days_until_deadline <= 2 else 'medium' if days_until_deadline <= 7 else 'low'
            
            action_item = {
                'id': f'goal-{goal.id}',
                'title': f'Complete Goal: {goal.title}',
                'description': goal.description,
                'due_date': goal.target_date.isoformat(),
                'priority': priority,
                'status': 'overdue' if days_until_deadline < 0 else 'in_progress' if goal.status == 'in_progress' else 'pending',
                'type': 'goal',
                'action_url': '/employee/goals',
                'estimated_time': 30
            }
            action_items.append(action_item)
            
            if days_until_deadline <= 2:
                urgent_deadlines.append({
                    'id': f'goal-{goal.id}',
                    'title': f'Goal: {goal.title}',
                    'due_date': goal.target_date.isoformat(),
                    'action_text': 'Continue' if goal.status == 'in_progress' else 'Start'
                })
        
        # Self-review action items
        try:
            self_review = SelfReview.objects.filter(employee=user).latest('created_at')
            if self_review.completion_percentage < 100:
                days_until_deadline = 7  # Default 7 days for self-review
                priority = 'high' if days_until_deadline <= 2 else 'medium'
                
                action_item = {
                    'id': 'self-review',
                    'title': 'Complete Self Review',
                    'description': 'Finish your self-assessment',
                    'due_date': (timezone.now().date() + timezone.timedelta(days=days_until_deadline)).isoformat(),
                    'priority': priority,
                    'status': 'in_progress' if self_review.completion_percentage > 0 else 'pending',
                    'type': 'self_review',
                    'action_url': '/employee/self-review',
                    'estimated_time': 60
                }
                action_items.append(action_item)
        except SelfReview.DoesNotExist:
            # Create self-review action item if none exists
            action_item = {
                'id': 'self-review',
                'title': 'Start Self Review',
                'description': 'Begin your self-assessment',
                'due_date': (timezone.now().date() + timezone.timedelta(days=7)).isoformat(),
                'priority': 'high',
                'status': 'pending',
                'type': 'self_review',
                'action_url': '/employee/self-review',
                'estimated_time': 60
            }
            action_items.append(action_item)
        
        # Peer feedback action items
        from apps.feedback.models import PeerReviewer
        pending_feedback = PeerReviewer.objects.filter(reviewer=user, status='pending')
        if pending_feedback.exists():
            days_until_deadline = 3  # Default 3 days for peer feedback
            priority = 'medium' if days_until_deadline <= 2 else 'low'
            
            action_item = {
                'id': 'peer-feedback',
                'title': f'Provide Peer Feedback ({pending_feedback.count()} requests)',
                'description': f'{pending_feedback.count()} feedback requests pending',
                'due_date': (timezone.now().date() + timezone.timedelta(days=days_until_deadline)).isoformat(),
                'priority': priority,
                'status': 'pending',
                'type': 'peer_feedback',
                'action_url': '/employee/peer-feedback',
                'estimated_time': 20
            }
            action_items.append(action_item)
        
        # Sort action items by priority and due date
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        action_items.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['due_date']))
        
        dashboard_data['action_items'] = action_items
        dashboard_data['deadlines'] = urgent_deadlines
        
        # Calculate statistics
        dashboard_data['statistics'] = {
            'completed_items': len([item for item in action_items if item['status'] == 'completed']),
            'in_progress_items': len([item for item in action_items if item['status'] == 'in_progress']),
            'overdue_items': len([item for item in action_items if item['status'] == 'overdue']),
            'upcoming_items': len([item for item in action_items if item['status'] == 'pending'])
        }
        
        # Get recent activity (mock data for now)
        recent_activity = [
            {
                'id': 1,
                'title': 'Goal Updated',
                'description': 'Updated progress on a goal',
                'type': 'goal_update',
                'timestamp': (timezone.now() - timezone.timedelta(hours=2)).isoformat()
            },
            {
                'id': 2,
                'title': 'Self Review Started',
                'description': 'Began working on your self-assessment',
                'type': 'self_review_start',
                'timestamp': (timezone.now() - timezone.timedelta(days=1)).isoformat()
            }
        ]
        dashboard_data['recent_activity'] = recent_activity
        
        return Response(dashboard_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to load dashboard data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Employee Progress Summary",
    description="Get a summary of the employee's progress across all review components.",
    responses={
        200: OpenApiTypes.OBJECT,
        401: "Authentication required"
    }
)
def get_employee_progress_summary(request):
    """
    Get a summary of the employee's progress across all review components.
    """
    try:
        user = request.user
        
        # Get goals progress
        from apps.goals.models import Goal
        goals = Goal.objects.filter(employee=user)
        goals_completion = 0
        if goals.exists():
            completed_goals = goals.filter(status='completed').count()
            goals_completion = round((completed_goals / goals.count()) * 100)
        
        # Get self-review progress
        from apps.reviews.models import SelfReview
        self_review_completion = 0
        try:
            self_review = SelfReview.objects.filter(employee=user).latest('created_at')
            self_review_completion = self_review.completion_percentage or 0
        except SelfReview.DoesNotExist:
            pass
        
        # Get peer feedback progress
        from apps.feedback.models import FeedbackRequest
        feedback_requests = FeedbackRequest.objects.filter(requester=user)
        peer_feedback_completion = 0
        if feedback_requests.exists():
            completed_requests = feedback_requests.filter(status='completed').count()
            peer_feedback_completion = round((completed_requests / feedback_requests.count()) * 100)
        
        # Calculate overall completion
        progress_values = [goals_completion, self_review_completion, peer_feedback_completion]
        overall_completion = round(sum(progress_values) / len(progress_values))
            
        return Response({
            'goals_completion': goals_completion,
            'self_review_completion': self_review_completion,
            'peer_feedback_completion': peer_feedback_completion,
            'overall_completion': overall_completion,
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to load progress summary: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Employee Action Items",
    description="Get action items for the current employee with priorities and deadlines.",
    responses={
        200: OpenApiTypes.OBJECT,
            401: "Authentication required"
    }
)
def get_employee_action_items(request):
    """
    Get action items for the current employee with priorities and deadlines.
    """
    try:
        user = request.user
        action_items = []
        
        # Get goals action items
        from apps.goals.models import Goal
        goals = Goal.objects.filter(employee=user, status__in=['draft', 'in_progress'])
        for goal in goals:
            days_until_deadline = (goal.target_date - timezone.now().date()).days
            priority = 'high' if days_until_deadline <= 2 else 'medium' if days_until_deadline <= 7 else 'low'
            
            action_items.append({
                'id': f'goal-{goal.id}',
                'title': f'Complete Goal: {goal.title}',
                'description': goal.description,
                'due_date': goal.target_date.isoformat(),
                'priority': priority,
                'status': 'overdue' if days_until_deadline < 0 else 'in_progress' if goal.status == 'in_progress' else 'pending',
                'type': 'goal',
                'action_url': '/employee/goals',
                'estimated_time': 30
            })
        
        # Get self-review action items
        from apps.reviews.models import SelfReview
        try:
            self_review = SelfReview.objects.filter(employee=user).latest('created_at')
            if self_review.completion_percentage < 100:
                action_items.append({
                    'id': 'self-review',
                    'title': 'Complete Self Review',
                    'description': 'Finish your self-assessment',
                    'due_date': (timezone.now().date() + timezone.timedelta(days=7)).isoformat(),
                    'priority': 'high',
                    'status': 'in_progress' if self_review.completion_percentage > 0 else 'pending',
                    'type': 'self_review',
                    'action_url': '/employee/self-review',
                    'estimated_time': 60
                })
        except SelfReview.DoesNotExist:
            action_items.append({
                'id': 'self-review',
                'title': 'Start Self Review',
                'description': 'Begin your self-assessment',
                'due_date': (timezone.now().date() + timezone.timedelta(days=7)).isoformat(),
                'priority': 'high',
                'status': 'pending',
                'type': 'self_review',
                'action_url': '/employee/self-review',
                'estimated_time': 60
            })
        
        # Get peer feedback action items
        from apps.feedback.models import PeerReviewer
        pending_feedback = PeerReviewer.objects.filter(reviewer=user, status='pending')
        if pending_feedback.exists():
            action_items.append({
                'id': 'peer-feedback',
                'title': f'Provide Peer Feedback ({pending_feedback.count()} requests)',
                'description': f'{pending_feedback.count()} feedback requests pending',
                'due_date': (timezone.now().date() + timezone.timedelta(days=3)).isoformat(),
                'priority': 'medium',
                'status': 'pending',
                'type': 'peer_feedback',
                'action_url': '/employee/peer-feedback',
                'estimated_time': 20
            })
        
        # Sort by priority and due date
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        action_items.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['due_date']))
        
        return Response({
            'action_items': action_items,
            'total_count': len(action_items),
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to load action items: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )