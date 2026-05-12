from django.db import models
from django.conf import settings
from django.utils import timezone

class Dataset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    file_type = models.CharField(max_length=20)
    row_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'datasets'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Dashboard(models.Model):
    DASHBOARD_TYPES = [
        ('sales', 'Sales Analytics'),
        ('hr', 'HR Analytics'),
        ('education', 'Education Analytics'),
        ('custom', 'Custom Dashboard'),
    ]
    
    THEMES = [
        ('corporate', 'Corporate'),
        ('executive', 'Executive'),
        ('modern', 'Modern'),
        ('dark', 'Dark Theme'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboards')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dashboards')
    name = models.CharField(max_length=255)
    dashboard_type = models.CharField(max_length=50, choices=DASHBOARD_TYPES, default='custom')
    theme = models.CharField(max_length=50, choices=THEMES, default='corporate')
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'dashboards'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

# ============================================================
# EMAIL AND SCHEDULED REPORTS MODELS
# ============================================================

class EmailReport(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE, related_name='email_reports')
    recipients = models.TextField(help_text="Comma-separated email addresses")
    subject = models.CharField(max_length=500)
    message = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    send_time = models.TimeField(null=True, blank=True)
    next_send = models.DateTimeField(null=True, blank=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.frequency}"

class ScheduledReport(models.Model):
    WEEKDAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE, related_name='scheduled_reports')
    name = models.CharField(max_length=255)
    recipients = models.TextField()
    format = models.CharField(max_length=10, choices=EmailReport.FORMAT_CHOICES, default='pdf')
    schedule_type = models.CharField(max_length=20, choices=EmailReport.FREQUENCY_CHOICES)
    schedule_time = models.TimeField()
    schedule_day = models.CharField(max_length=10, choices=WEEKDAYS, null=True, blank=True)
    schedule_date = models.IntegerField(null=True, blank=True, help_text="Day of month (1-31)")
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduled_reports'
    
    def __str__(self):
        return f"{self.name} - {self.schedule_type}"