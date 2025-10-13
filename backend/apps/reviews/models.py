"""
Reviews models for the EPMS system.

This module contains models for performance reviews,
including self-reviews, manager reviews, and evaluations.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

# Import structured self-review models (BR-027 through BR-031)
from .self_review_models import SelfReview, SelfReviewVersion, SelfReviewAttachment


class Review(models.Model):
    """
    Review model for performance evaluations.
    
    Represents a performance review for an employee
    during a specific review cycle.
    """
    
    # Review type choices
    TYPE_CHOICES = [
        ('self', 'Self Review'),
        ('manager', 'Manager Review'),
        ('peer', 'Peer Review'),
        ('360', '360 Review'),
    ]
    
    # Review status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ]
    
    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Employee being reviewed'
    )
    
    reviewer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reviews_given',
        help_text='Person conducting the review'
    )
    
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Review cycle this review belongs to'
    )
    
    review_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text='Type of review'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Current status of the review'
    )
    
    # Overall ratings
    overall_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Overall performance rating (1-5)'
    )
    
    # Review content
    achievements = models.TextField(
        blank=True,
        help_text='Key achievements and accomplishments'
    )
    
    challenges = models.TextField(
        blank=True,
        help_text='Challenges faced and how they were addressed'
    )
    
    development_areas = models.TextField(
        blank=True,
        help_text='Areas for development and improvement'
    )
    
    goals_for_next_period = models.TextField(
        blank=True,
        help_text='Goals for the next review period'
    )
    
    comments = models.TextField(
        blank=True,
        help_text='Additional comments and observations'
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the review was submitted'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the review was approved'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Review model."""
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['employee', 'reviewer', 'cycle', 'review_type']
    
    def __str__(self):
        """String representation of the review."""
        return f"{self.get_review_type_display()} for {self.employee.employee_id}"


class ReviewSection(models.Model):
    """
    Review section model for structured reviews.
    
    Represents different sections within a review
    with specific questions and ratings.
    """
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='sections',
        help_text='Review this section belongs to'
    )
    
    title = models.CharField(
        max_length=200,
        help_text='Section title'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Section description'
    )
    
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating for this section (1-5)'
    )
    
    comments = models.TextField(
        blank=True,
        help_text='Comments for this section'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Order of this section in the review'
    )
    
    class Meta:
        """Meta options for ReviewSection model."""
        verbose_name = 'Review Section'
        verbose_name_plural = 'Review Sections'
        ordering = ['order', 'title']
    
    def __str__(self):
        """String representation of the review section."""
        return f"{self.title} - {self.review}"


class ReviewTemplate(models.Model):
    """
    Review template model for standardized reviews.
    
    Represents templates for creating consistent
    review structures across the organization.
    """
    
    name = models.CharField(
        max_length=200,
        help_text='Template name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Template description'
    )
    
    review_type = models.CharField(
        max_length=20,
        choices=Review.TYPE_CHOICES,
        help_text='Type of review this template is for'
    )
    
    sections = models.JSONField(
        help_text='List of sections in the template'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the template is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for ReviewTemplate model."""
        verbose_name = 'Review Template'
        verbose_name_plural = 'Review Templates'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the review template."""
        return self.name