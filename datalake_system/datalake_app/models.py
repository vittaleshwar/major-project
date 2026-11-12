from django.db import models
from django.contrib.auth.models import User
import json
from django_cryptography.fields import encrypt  # Install: pip install django-cryptography

class AWSConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aws_config')
    aws_access_key_id = models.CharField(max_length=100, blank=True)
    aws_secret_access_key = models.CharField(max_length=100, blank=True)
    aws_region = models.CharField(max_length=50, default='us-east-1')
    use_real_aws = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Add this field
    configured_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AWS Config for {self.user.username}"
    
    def get_connection_status(self):
        """Get connection status message"""
        if not self.use_real_aws:
            return "local", "Local Simulation Mode"
        elif self.is_active:
            return "active", f"AWS Connected (Region: {self.aws_region})"
        else:
            return "inactive", "AWS Configuration Required"

class S3Bucket(models.Model):
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=100, default='us-east-1')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_real_aws = models.BooleanField(default=False)
    aws_bucket_arn = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.name

class DataFile(models.Model):
    FILE_TYPES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('parquet', 'Parquet'),
        ('avro', 'Avro'),
        ('text', 'Text'),
        ('unknown', 'Unknown'),
    ]
    
    name = models.CharField(max_length=255)
    bucket = models.ForeignKey(S3Bucket, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='unknown')
    size_mb = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)  # ADD THIS FIELD
    upload_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    metadata = models.TextField(default='{}')  # JSON field for metadata
    local_file_path = models.TextField(blank=True, null=True)  # ADD THIS FIELD
    is_real_aws = models.BooleanField(default=False)
    s3_key = models.CharField(max_length=500, blank=True, null=True)
    
    def get_metadata(self):
        try:
            return json.loads(self.metadata)
        except:
            return {}
    
    def set_metadata(self, data):
        self.metadata = json.dumps(data)
    
    def __str__(self):
        return f"{self.name} ({self.file_type})"

class GlueCrawler(models.Model):
    name = models.CharField(max_length=255)
    bucket = models.ForeignKey(S3Bucket, on_delete=models.CASCADE)
    schedule = models.CharField(max_length=50, default='On demand')
    last_run = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Ready')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_real_aws = models.BooleanField(default=False)
    aws_crawler_name = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name

class AthenaQuery(models.Model):
    query_id = models.CharField(max_length=100, unique=True)
    sql_statement = models.TextField()
    database = models.CharField(max_length=100)
    output_location = models.CharField(max_length=500)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    rows_returned = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default='QUEUED')
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(auto_now_add=True)
    result_data = models.TextField(null=True, blank=True)
    is_real_aws = models.BooleanField(default=False)
    aws_query_execution_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Query {self.query_id}"