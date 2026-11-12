from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import S3Bucket, DataFile, GlueCrawler, AthenaQuery, AWSConfig

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class S3BucketForm(forms.ModelForm):
    REGION_CHOICES = [
        ('us-east-1', 'US East (N. Virginia)'),
        ('us-east-2', 'US East (Ohio)'),
        ('us-west-1', 'US West (N. California)'),
        ('us-west-2', 'US West (Oregon)'),
        ('eu-west-1', 'Europe (Ireland)'),
        ('ap-south-1', 'Asia Pacific (Mumbai)'),
        ('ap-southeast-1', 'Asia Pacific (Singapore)'),
        ('ap-northeast-1', 'Asia Pacific (Tokyo)'),
    ]
    
    region = forms.ChoiceField(choices=REGION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = S3Bucket
        fields = ['name', 'region']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'my-data-lake-bucket'
            }),
        }

class FileUploadForm(forms.Form):
    """Form for actual file upload (not just metadata)"""
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.json,.txt'
        }),
        label="Choose File"
    )
    bucket = forms.ModelChoiceField(
        queryset=S3Bucket.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="S3 Bucket"
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional description of the file contents...'
        }),
        label="Description"
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bucket'].queryset = S3Bucket.objects.filter(created_by=user)

# REMOVE or FIX the DataFileForm since it's causing the error
# Or update it to match the actual model fields:

class DataFileForm(forms.ModelForm):
    """Form for file metadata (after upload) - FIXED VERSION"""
    class Meta:
        model = DataFile
        fields = ['name', 'bucket', 'file_type', 'size_mb']  # Removed description
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bucket': forms.Select(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
            'size_mb': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AthenaQueryForm(forms.ModelForm):
    class Meta:
        model = AthenaQuery
        fields = ['sql_statement', 'database']
        widgets = {
            'sql_statement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'SELECT * FROM sales_data LIMIT 10;'
            }),
            'database': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'data_lake_db'
            }),
        }

class AWSConfigForm(forms.ModelForm):
    class Meta:
        model = AWSConfig
        fields = ['aws_access_key_id', 'aws_secret_access_key', 'aws_region', 'use_real_aws']
        widgets = {
            'aws_access_key_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AKIAIOSFODNN7EXAMPLE'
            }),
            'aws_secret_access_key': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
            }),
            'aws_region': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('us-east-1', 'US East (N. Virginia)'),
                ('us-west-2', 'US West (Oregon)'),
                ('eu-west-1', 'Europe (Ireland)'),
                ('ap-south-1', 'Asia Pacific (Mumbai)'),
            ]),
            'use_real_aws': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }