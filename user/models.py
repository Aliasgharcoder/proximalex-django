from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('lawyer', 'Lawyer'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(('email address'), unique=True)  # Add this line
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # Add these fields for lawyers only
    specialization = models.CharField(max_length=255, blank=True, null=True)  # e.g. Criminal Law, Corporate, etc.
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)  # Comma-separated for now
    bio = models.TextField(blank=True, null=True)  # Short intro about the lawyer
    is_available = models.BooleanField(default=True)

    sub_specialization = models.CharField(max_length=100, blank=True, null=True)
    cases_handled = models.PositiveIntegerField(default=0)
    area = models.CharField(max_length=100, blank=True, null=True)
    court_experience = models.CharField(max_length=255, blank=True, null=True)
    hourly_rate = models.PositiveIntegerField(blank=True, null=True)
    success_rate = models.CharField(max_length=10, blank=True, null=True)

class Case(models.Model):
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Status and Urgency
    urgency_level = models.CharField(
        max_length=50, 
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], 
        default='medium'
    )
    case_status = models.CharField(
        max_length=100,
        choices=[
            ('fir_registered', 'FIR Registered'),
            ('under_investigation', 'Under Investigation'),
            ('challan_submitted', 'Challan Submitted'),
            ('trial_started', 'Trial Started'),
            ('appeal_filed', 'Appeal Filed'),
            ('settled', 'Settled')
        ],
        blank=True,
        null=True
    )
    
    # Police and FIR Details
    police_station = models.CharField(max_length=255, blank=True, null=True)
    fir_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Court Details
    court_name = models.CharField(
        max_length=100,
        choices=[
            ('district', 'District Court'),
            ('high', 'High Court'),
            ('supreme', 'Supreme Court'),
            ('family', 'Family Court'),
            ('anti_terrorism', 'Anti-terrorism Court'),
            ('banking', 'Banking Court'),
            ('customs', 'Customs Court')
        ],
        blank=True,
        null=True
    )
    case_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Legal Details
    opposing_party = models.CharField(max_length=255, blank=True, null=True)
    applicable_laws = models.CharField(max_length=255, blank=True, null=True)
    hearing_date = models.DateField(blank=True, null=True)
    
    # Document
    document = models.FileField(upload_to='case_documents/', blank=True, null=True)
    
    # Relationships
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='client_cases', 
        on_delete=models.CASCADE
    )
    lawyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='lawyer_cases', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    # Type and Complexity
    case_type = models.CharField(max_length=100, blank=True, null=True)
    case_subtype = models.CharField(max_length=100, blank=True, null=True)
    case_complexity = models.CharField(
        max_length=50,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    # Status Tracking
    status = models.CharField(
        max_length=50, 
        choices=[
            ('open', 'Open'), 
            ('in_progress', 'In Progress'), 
            ('closed', 'Closed')
        ], 
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"