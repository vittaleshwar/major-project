from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # S3 Operations
    path('bucket/create/', views.create_bucket, name='create_bucket'),
    path('buckets/', views.list_buckets, name='list_buckets'),
    
    # File Operations
    path('file/upload/', views.upload_file, name='upload_file'),
    path('files/', views.list_files, name='list_files'),
    path('file/<int:file_id>/', views.view_file, name='view_file'),
    
    # Athena Operations
    path('athena/execute/', views.execute_athena_query, name='execute_query'),
    path('athena/results/<str:query_id>/', views.query_results, name='query_results'),
    
    # Glue Operations
    path('glue/crawler/', views.glue_crawler, name='glue_crawler'),
    path('glue/results/<int:crawler_id>/', views.crawler_results, name='crawler_results'),
    
    # Configuration
    path('aws-config/', views.aws_config, name='aws_config'),
]