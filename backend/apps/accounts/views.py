"""
Views for the accounts app.

This module contains API views for user authentication,
registration, and profile management.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserListSerializer, UserRegistrationSerializer,
    UserProfileSerializer, LoginSerializer, ChangePasswordSerializer,
    PasswordResetSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with additional user data.
    
    Extends the default JWT view to include user information
    in the response.
    """
    
    @extend_schema(
        summary="Login User",
        description="Authenticate user and return JWT tokens with user data.",
        responses={
            200: "Login successful",
            401: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        """Handle user login and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    Allows new users to register with the system.
    """
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register New User",
        description="Create a new user account in the system.",
        responses={
            201: "User created successfully",
            400: "Validation error"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new user account."""
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile management endpoint.
    
    Allows users to view and update their profile information.
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the current user's profile."""
        return self.request.user
    
    @extend_schema(
        summary="Get User Profile",
        description="Retrieve current user's profile information.",
        responses={
            200: UserSerializer,
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get current user's profile."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User Profile",
        description="Update current user's profile information.",
        responses={
            200: UserSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update current user's profile."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User Profile",
        description="Update current user's profile information.",
        responses={
            200: UserSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def put(self, request, *args, **kwargs):
        """Update current user's profile."""
        return super().put(request, *args, **kwargs)


class UserProfileExtendedView(generics.RetrieveUpdateAPIView):
    """
    Extended user profile management endpoint.
    
    Handles the UserProfile model for additional profile information.
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create the user's extended profile."""
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    @extend_schema(
        summary="Get Extended Profile",
        description="Retrieve user's extended profile information.",
        responses={
            200: UserProfileSerializer,
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get user's extended profile."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Extended Profile",
        description="Update user's extended profile information.",
        responses={
            200: UserProfileSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update user's extended profile."""
        return super().patch(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    """
    User list endpoint.
    
    Provides a list of users with filtering and search capabilities.
    """
    
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset of users."""
        queryset = User.objects.all()
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search by name or employee ID
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('employee_id')
    
    @extend_schema(
        summary="List Users",
        description="Get a list of users with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='role',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by user role'
            ),
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by department ID'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by user status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by name or employee ID'
            ),
        ],
        responses={
            200: UserListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of users."""
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    User detail endpoint.
    
    Provides detailed information about a specific user and allows updates.
    """
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Get queryset of users."""
        return User.objects.all()
    
    @extend_schema(
        summary="Get User Details",
        description="Retrieve detailed information about a specific user.",
        responses={
            200: UserSerializer,
            404: "User not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get user details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User",
        description="Update a specific user's information.",
        responses={
            200: UserSerializer,
            400: "Validation error",
            404: "User not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update user details."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User",
        description="Update a specific user's information.",
        responses={
            200: UserSerializer,
            400: "Validation error",
            404: "User not found",
            401: "Authentication required"
        }
    )
    def put(self, request, *args, **kwargs):
        """Update user details."""
        return super().put(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
    Change password endpoint.
    
    Allows authenticated users to change their password.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change Password",
        description="Change the current user's password.",
        request=ChangePasswordSerializer,
        responses={
            200: "Password changed successfully",
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Password reset request endpoint.
    
    Sends password reset email to the user.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Request Password Reset",
        description="Send password reset email to the user.",
        request=PasswordResetSerializer,
        responses={
            200: "Password reset email sent",
            400: "Validation error"
        }
    )
    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate reset token
            reset_token = get_random_string(32)
            user.reset_token = reset_token
            user.reset_token_expires = timezone.now() + timedelta(hours=1)
            user.save()
            
            # Send email (in production, use proper email templates)
            send_mail(
                'Password Reset Request',
                f'Your password reset token is: {reset_token}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email sent successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow logout even with invalid token
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