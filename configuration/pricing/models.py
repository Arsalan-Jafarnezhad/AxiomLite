from django.db import models

class PricingPlan(models.Model):
    """
    Represents a pricing plan with various features and pricing details.
    """
    
    PLAN_TYPES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise')
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable name for the pricing plan (e.g., Basic, Pro)"
    )
    
    type = models.CharField(
        max_length=20,
        choices=PLAN_TYPES,
        default='basic',
        help_text="Type of plan (Basic, Pro, Enterprise)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the plan's features and benefits"
    )
    
    price_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Monthly subscription price in currency (e.g., 9.99)"
    )
    
    price_per_year = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Annual subscription price with discount (e.g., 99.99)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this plan is currently available for sale"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the plan was first created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update to this plan"
    )
    
    class Meta:
        ordering = ['type', 'name']
        verbose_name_plural = "Pricing Plans"


class Feature(models.Model):
    """
    Represents a feature available in specific pricing plans.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name of the feature (e.g., Unlimited Storage)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed explanation of what this feature provides"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this feature is currently available to users"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the feature was first added"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update to this feature"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Features"


class PlanFeature(models.Model):
    """
    Links a pricing plan with its available features.
    """
    
    plan = models.ForeignKey(
        PricingPlan,
        on_delete=models.CASCADE,
        related_name='features',
        help_text="The pricing plan that includes this feature"
    )
    
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name='plans',
        help_text="The specific feature available in the plan"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this feature is enabled for the specified plan"
    )
    
    class Meta:
        unique_together = ('plan', 'feature')
        ordering = ['plan__type', 'feature__name']
        verbose_name_plural = "Plan-Feature Relationships"
