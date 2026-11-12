from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
import uuid
import json
from datetime import datetime

import os
import mimetypes

# Add these imports at the top
import csv
import json as json_lib

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """Dashboard view"""
    user_buckets = S3Bucket.objects.filter(created_by=request.user).count()
    user_queries = AthenaQuery.objects.filter(executed_by=request.user).count()
    user_files = DataFile.objects.filter(created_by=request.user).count()
    user_crawlers = GlueCrawler.objects.filter(created_by=request.user).count()
    
    # Get recent files
    recent_files = DataFile.objects.filter(created_by=request.user).order_by('-upload_date')[:5]
    
    # Get recent queries
    recent_queries = AthenaQuery.objects.filter(executed_by=request.user).order_by('-executed_at')[:5]
    
    context = {
        'buckets_count': user_buckets,
        'queries_count': user_queries,
        'files_count': user_files,
        'crawlers_count': user_crawlers,
        'recent_files': recent_files,
        'recent_queries': recent_queries,
    }
    return render(request, 'datalake/dashboard.html', context)

@login_required
def create_bucket(request):
    if request.method == 'POST':
        form = S3BucketForm(request.POST)
        if form.is_valid():
            bucket = form.save(commit=False)
            bucket.created_by = request.user
            bucket.save()
            messages.success(request, f'S3 Bucket "{bucket.name}" created successfully!')
            return redirect('list_buckets')
    else:
        form = S3BucketForm()
    return render(request, 'datalake/create_bucket.html', {'form': form})

@login_required
def list_buckets(request):
    buckets = S3Bucket.objects.filter(created_by=request.user)
    return render(request, 'datalake/list_buckets.html', {'buckets': buckets})

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = DataFileForm(request.POST)
        if form.is_valid():
            file = form.save()
            
            # Simulate metadata extraction
            metadata = {
                'columns': ['id', 'name', 'value', 'timestamp'],
                'row_count': 1000,
                'compression': 'none',
                'uploaded_by': request.user.username
            }
            file.set_metadata(metadata)
            file.save()
            
            messages.success(request, f'File "{file.name}" uploaded to S3 bucket!')
            return redirect('list_files')
    else:
        form = DataFileForm()
        form.fields['bucket'].queryset = S3Bucket.objects.filter(created_by=request.user)
    
    return render(request, 'datalake/upload_file.html', {'form': form})

@login_required
def execute_athena_query(request):
    if request.method == 'POST':
        form = AthenaQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.query_id = str(uuid.uuid4())[:8]
            query.executed_by = request.user
            query.output_location = f"s3://{request.user.username}-query-results/"
            
            # Simulate query execution
            import random
            query.execution_time_ms = random.randint(100, 5000)
            query.rows_returned = random.randint(10, 1000)
            query.status = 'SUCCEEDED'
            
            # Generate sample result data
            sample_data = {
                'columns': ['id', 'customer_name', 'purchase_amount', 'date'],
                'rows': [
                    [1, 'John Doe', 150.50, '2024-01-15'],
                    [2, 'Jane Smith', 89.99, '2024-01-16'],
                    [3, 'Bob Johnson', 245.00, '2024-01-17'],
                ]
            }
            query.result_data = json.dumps(sample_data)
            
            query.save()
            
            messages.success(request, f'Query executed successfully! Query ID: {query.query_id}')
            return redirect('query_results', query_id=query.query_id)
    else:
        form = AthenaQueryForm()
    
    return render(request, 'datalake/execute_query.html', {'form': form})

@login_required
def query_results(request, query_id):
    query = get_object_or_404(AthenaQuery, query_id=query_id, executed_by=request.user)
    
    # Parse result data
    result_data = json.loads(query.result_data) if query.result_data else None
    
    context = {
        'query': query,
        'result_data': result_data,
        'execution_time_seconds': query.execution_time_ms / 1000 if query.execution_time_ms else 0
    }
    
    return render(request, 'datalake/query_results.html', context)

@login_required
def glue_crawler(request):
    if request.method == 'POST':
        crawler_name = request.POST.get('crawler_name')
        bucket_id = request.POST.get('bucket')
        
        if crawler_name and bucket_id:
            bucket = S3Bucket.objects.get(id=bucket_id, created_by=request.user)
            crawler = GlueCrawler.objects.create(
                name=crawler_name,
                bucket=bucket,
                created_by=request.user,
                status='RUNNING'
            )
            
            # Simulate crawler execution
            import time
            time.sleep(2)  # Simulate processing time
            
            crawler.last_run = datetime.now()
            crawler.status = 'COMPLETED'
            crawler.save()
            
            messages.success(request, f'Glue Crawler "{crawler_name}" completed successfully!')
            return redirect('crawler_results', crawler_id=crawler.id)
    
    buckets = S3Bucket.objects.filter(created_by=request.user)
    crawlers = GlueCrawler.objects.filter(created_by=request.user).order_by('-last_run')
    
    return render(request, 'datalake/glue_crawler.html', {
        'buckets': buckets,
        'crawlers': crawlers
    })

@login_required
def crawler_results(request, crawler_id):
    crawler = get_object_or_404(GlueCrawler, id=crawler_id, created_by=request.user)
    
    # Simulate discovered tables
    discovered_tables = [
        {'name': 'sales_data', 'record_count': 10000, 'file_format': 'parquet'},
        {'name': 'customer_data', 'record_count': 5000, 'file_format': 'csv'},
        {'name': 'product_catalog', 'record_count': 2000, 'file_format': 'json'},
    ]
    
    return render(request, 'datalake/crawler_results.html', {
        'crawler': crawler,
        'tables': discovered_tables
    })
    
    
    
from .forms import AWSConfigForm
from .models import AWSConfig
from .aws_services import AWSService, LocalSimulationService

# Add this function to get service based on configuration
def get_data_lake_service(user):
    """Get appropriate service (AWS or Local) based on user configuration"""
    if hasattr(user, 'aws_config') and user.aws_config.use_real_aws:
        aws_service = AWSService(user)
        if aws_service.is_aws_configured():
            return aws_service
    return LocalSimulationService()

# Add AWS configuration view
from .aws_helper import AWSConnection

@login_required
def aws_config(request):
    """AWS configuration view with automatic connection testing"""
    try:
        aws_config_instance = request.user.aws_config
    except AWSConfig.DoesNotExist:
        aws_config_instance = AWSConfig.objects.create(user=request.user)
    
    connection_status = None
    test_results = None
    
    if request.method == 'POST':
        form = AWSConfigForm(request.POST, instance=aws_config_instance)
        
        if form.is_valid():
            config = form.save(commit=False)
            
            # Only validate if real AWS is enabled
            if config.use_real_aws and config.aws_access_key_id and config.aws_secret_access_key:
                # Test the connection
                is_valid, message, account_id = AWSConnection.validate_credentials(
                    config.aws_access_key_id,
                    config.aws_secret_access_key,
                    config.aws_region
                )
                
                connection_status = {
                    'is_valid': is_valid,
                    'message': message,
                    'account_id': account_id
                }
                
                if is_valid:
                    # Test full access
                    full_access, full_message, bucket_count = AWSConnection.create_test_resources(
                        config.aws_access_key_id,
                        config.aws_secret_access_key,
                        config.aws_region
                    )
                    
                    test_results = {
                        'full_access': full_access,
                        'message': full_message,
                        'bucket_count': bucket_count
                    }
                    
                    if full_access:
                        config.is_active = True
                        messages.success(request, f'AWS connection successful! Account: {account_id}')
                    else:
                        config.is_active = False
                        messages.warning(request, f'Connected but limited permissions: {full_message}')
                else:
                    config.is_active = False
                    messages.error(request, f'Connection failed: {message}')
            else:
                # Local simulation mode
                config.is_active = False
                messages.success(request, 'Local simulation mode enabled')
            
            config.save()
            
            # Don't redirect if there are connection issues
            if connection_status and connection_status.get('is_valid') and test_results and test_results.get('full_access'):
                return redirect('dashboard')
    else:
        form = AWSConfigForm(instance=aws_config_instance)
    
    # Get IAM policy for students
    iam_policy = AWSConnection.get_required_permissions()
    
    context = {
        'form': form,
        'connection_status': connection_status,
        'test_results': test_results,
        'iam_policy': iam_policy,
        'current_config': aws_config_instance
    }
    
    return render(request, 'datalake/aws_config.html', context)

# Update existing views to use appropriate service
@login_required
def create_bucket(request):
    if request.method == 'POST':
        form = S3BucketForm(request.POST)
        if form.is_valid():
            bucket = form.save(commit=False)
            bucket.created_by = request.user
            
            # Get appropriate service
            service = get_data_lake_service(request.user)
            
            # Create bucket using appropriate service
            if isinstance(service, AWSService):
                bucket_arn = service.create_s3_bucket(bucket.name)
                if bucket_arn:
                    bucket.is_real_aws = True
                    bucket.aws_bucket_arn = bucket_arn
                    bucket.save()
                    messages.success(request, f'Real AWS S3 Bucket "{bucket.name}" created successfully!')
                else:
                    messages.error(request, 'Failed to create AWS S3 bucket. Check your configuration.')
                    return redirect('create_bucket')
            else:
                bucket_arn = service.create_s3_bucket(bucket.name)
                bucket.is_real_aws = False
                bucket.save()
                messages.success(request, f'Simulated S3 Bucket "{bucket.name}" created successfully!')
            
            return redirect('list_buckets')
    else:
        form = S3BucketForm()
    return render(request, 'datalake/create_bucket.html', {'form': form})

import re
from django.db.models import Q

@login_required
def execute_athena_query(request):
    """Execute Athena query view - DYNAMIC VERSION"""
    # Get pre-filled query from URL if available
    initial_query = request.GET.get('query', 'SELECT * FROM sales_data LIMIT 10;')
    
    if request.method == 'POST':
        # Get form data
        sql_statement = request.POST.get('sql_statement', '').strip()
        database = request.POST.get('database', 'data_lake_db')
        
        if not sql_statement:
            messages.error(request, 'Please enter a SQL query')
            return redirect('execute_query')
        
        # Create query record first
        query = AthenaQuery.objects.create(
            query_id=str(uuid.uuid4())[:8],
            sql_statement=sql_statement,
            database=database,
            output_location=f"s3://{request.user.username}-query-results/",
            executed_by=request.user,
            status='RUNNING'
        )
        
        try:
            # Parse the SQL query
            parsed_query = parse_sql_query(sql_statement)
            
            # Execute the query based on actual files
            result_data = execute_query_on_files(request.user, parsed_query)
            
            # Update query with results
            query.status = 'SUCCEEDED'
            query.execution_time_ms = 100 + len(result_data['rows']) * 10  # Simulate execution time
            query.rows_returned = len(result_data['rows'])
            query.result_data = json.dumps(result_data)
            
            messages.success(request, f'Query executed successfully! Returned {query.rows_returned} rows.')
            
        except Exception as e:
            # If query execution fails
            query.status = 'FAILED'
            query.result_data = json.dumps({
                'columns': ['error'],
                'rows': [[str(e)]]
            })
            messages.error(request, f'Query execution failed: {str(e)}')
        
        query.save()
        return redirect('query_results', query_id=query.query_id)
    
    # GET request - show query form with initial query
    context = {
        'initial_query': initial_query
    }
    
    return render(request, 'datalake/execute_query.html', context)

def parse_sql_query(sql):
    """Parse SQL query to extract components"""
    sql = sql.upper().strip()
    
    # Extract table name (simplified)
    table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
    table_name = table_match.group(1).lower() if table_match else None
    
    # Extract columns
    select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
    columns_text = select_match.group(1) if select_match else '*'
    
    # Parse columns
    if columns_text.strip() == '*':
        columns = ['*']  # All columns
    else:
        columns = [col.strip().split(' AS ')[-1].strip() for col in columns_text.split(',')]
    
    # Extract LIMIT
    limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
    limit = int(limit_match.group(1)) if limit_match else 100
    
    # Extract WHERE clause
    where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
    where_clause = where_match.group(1).strip() if where_match else None
    
    # Extract ORDER BY
    order_match = re.search(r'ORDER\s+BY\s+(.+?)(?:\s+LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
    order_by = order_match.group(1).strip() if order_match else None
    
    # Extract GROUP BY
    group_match = re.search(r'GROUP\s+BY\s+(.+?)(?:\s+ORDER\s+BY|\s+LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
    group_by = group_match.group(1).strip() if group_match else None
    
    return {
        'table_name': table_name,
        'columns': columns,
        'limit': limit,
        'where': where_clause,
        'order_by': order_by,
        'group_by': group_by,
        'original_sql': sql
    }

def execute_query_on_files(user, parsed_query):
    """Execute query on actual uploaded files"""
    table_name = parsed_query['table_name']
    
    if not table_name:
        raise ValueError("No table specified in query")
    
    # Find files that match the table name
    # Convert table_name to possible file names (e.g., "sales_data" -> "sales_data.csv", "sales_data.json")
    possible_files = [
        f"{table_name}.csv",
        f"{table_name}.json",
        f"{table_name}.txt",
        table_name  # Just the name itself
    ]
    
    # Find matching files
    matching_files = DataFile.objects.filter(
        Q(created_by=user) &
        (Q(name__icontains=table_name) | 
         Q(name__in=possible_files))
    )
    
    if not matching_files.exists():
        # If no exact match, try to find any file
        all_files = DataFile.objects.filter(created_by=user)
        if all_files.exists():
            # Use the first file
            data_file = all_files.first()
        else:
            # No files uploaded yet - return sample data
            return get_sample_data_for_table(table_name)
    else:
        data_file = matching_files.first()
    
    # Get file metadata
    metadata = data_file.get_metadata()
    columns = metadata.get('columns', [])
    sample_data = metadata.get('sample_data', [])
    row_count = metadata.get('row_count', 0)
    
    # If no columns in metadata, create generic ones
    if not columns:
        columns = [f'col_{i}' for i in range(1, 11)]
    
    # Generate dynamic data based on query
    results = generate_dynamic_results(
        parsed_query, columns, row_count, sample_data, data_file.file_type
    )
    
    return results

def get_sample_data_for_table(table_name):
    """Generate sample data for common table names"""
    if 'sales' in table_name.lower():
        return {
            'columns': ['sale_id', 'customer_id', 'product', 'amount', 'date', 'region'],
            'rows': [
                [1, 101, 'Laptop', 1200.50, '2024-01-15', 'North'],
                [2, 102, 'Mouse', 25.99, '2024-01-16', 'South'],
                [3, 101, 'Keyboard', 89.99, '2024-01-17', 'East'],
                [4, 103, 'Monitor', 299.99, '2024-01-18', 'West'],
                [5, 104, 'Tablet', 499.99, '2024-01-19', 'North'],
                [6, 102, 'Headphones', 79.99, '2024-01-20', 'South'],
                [7, 105, 'Laptop', 1100.00, '2024-01-21', 'East'],
                [8, 103, 'Mouse', 22.50, '2024-01-22', 'West'],
                [9, 101, 'Monitor', 350.00, '2024-01-23', 'North'],
                [10, 104, 'Keyboard', 75.00, '2024-01-24', 'South']
            ]
        }
    elif 'customer' in table_name.lower():
        return {
            'columns': ['customer_id', 'name', 'email', 'city', 'join_date', 'membership'],
            'rows': [
                [101, 'John Doe', 'john@example.com', 'New York', '2023-12-01', 'Gold'],
                [102, 'Jane Smith', 'jane@example.com', 'Los Angeles', '2024-01-05', 'Silver'],
                [103, 'Bob Johnson', 'bob@example.com', 'Chicago', '2024-01-10', 'Platinum'],
                [104, 'Alice Brown', 'alice@example.com', 'Houston', '2024-01-15', 'Basic'],
                [105, 'Charlie Wilson', 'charlie@example.com', 'Phoenix', '2024-01-20', 'Gold']
            ]
        }
    elif 'product' in table_name.lower():
        return {
            'columns': ['product_id', 'name', 'category', 'price', 'stock', 'rating'],
            'rows': [
                ['P001', 'Laptop', 'Electronics', 1200.50, 50, 4.5],
                ['P002', 'Mouse', 'Electronics', 25.99, 200, 4.2],
                ['P003', 'Keyboard', 'Electronics', 89.99, 150, 4.3],
                ['P004', 'Monitor', 'Electronics', 299.99, 75, 4.6],
                ['P005', 'Tablet', 'Electronics', 499.99, 100, 4.4],
                ['P006', 'T-Shirt', 'Clothing', 19.99, 300, 4.1],
                ['P007', 'Jeans', 'Clothing', 49.99, 200, 4.3],
                ['P008', 'Book', 'Books', 14.99, 500, 4.7],
                ['P009', 'Headphones', 'Electronics', 79.99, 180, 4.4],
                ['P010', 'Smartphone', 'Electronics', 799.99, 60, 4.6]
            ]
        }
    else:
        # Generic sample data
        return {
            'columns': ['id', 'name', 'value', 'date'],
            'rows': [
                [1, 'Item 1', 100.50, '2024-01-15'],
                [2, 'Item 2', 200.75, '2024-01-16'],
                [3, 'Item 3', 150.25, '2024-01-17'],
                [4, 'Item 4', 300.00, '2024-01-18'],
                [5, 'Item 5', 250.50, '2024-01-19']
            ]
        }

def generate_dynamic_results(parsed_query, columns, row_count, sample_data, file_type):
    """Generate dynamic results based on query parameters"""
    limit = parsed_query['limit']
    requested_columns = parsed_query['columns']
    where_clause = parsed_query['where']
    order_by = parsed_query['order_by']
    group_by = parsed_query['group_by']
    
    # If SELECT *, use all columns
    if requested_columns == ['*']:
        requested_columns = columns
    
    # Filter columns to only requested ones
    column_indices = []
    final_columns = []
    
    for col in requested_columns:
        # Try to find the column in the actual columns
        found = False
        for i, actual_col in enumerate(columns):
            if col.lower() == actual_col.lower() or col == f'col_{i+1}':
                column_indices.append(i)
                final_columns.append(actual_col)
                found = True
                break
        
        # If column not found, add it as a new column
        if not found:
            column_indices.append(len(columns))  # Will generate data for this
            final_columns.append(col)
    
    # Generate data based on sample data or create new
    if sample_data and len(sample_data) > 0:
        # Use sample data as base
        base_rows = sample_data[:min(limit * 2, len(sample_data))]
    else:
        # Generate synthetic data
        base_rows = []
        for i in range(1, min(limit * 2, 50) + 1):
            row = []
            for col in columns:
                if 'id' in col.lower():
                    row.append(i)
                elif 'name' in col.lower():
                    row.append(f'Item {i}')
                elif 'date' in col.lower():
                    row.append(f'2024-01-{15 + (i % 15)}')
                elif 'amount' in col.lower() or 'price' in col.lower() or 'value' in col.lower():
                    row.append(round(50 + i * 25.5, 2))
                elif 'quantity' in col.lower():
                    row.append(i % 10 + 1)
                else:
                    row.append(f'Data {i}')
            base_rows.append(row)
    
    # Apply WHERE filtering (simplified)
    filtered_rows = []
    if where_clause:
        # Simple WHERE clause parsing
        for row in base_rows:
            include_row = evaluate_where_clause(row, columns, where_clause)
            if include_row:
                filtered_rows.append(row)
    else:
        filtered_rows = base_rows
    
    # Apply GROUP BY (simplified)
    if group_by:
        # Simple GROUP BY simulation
        grouped_data = {}
        group_col = group_by.split(',')[0].strip().lower()
        
        # Find group column index
        group_idx = -1
        for i, col in enumerate(columns):
            if col.lower() == group_col:
                group_idx = i
                break
        
        if group_idx >= 0:
            for row in filtered_rows:
                if group_idx < len(row):
                    key = row[group_idx]
                    if key not in grouped_data:
                        grouped_data[key] = []
                    grouped_data[key].append(row)
            
            # Create aggregated rows
            aggregated_rows = []
            for key, rows in list(grouped_data.items())[:limit]:
                # Simple aggregation - count
                agg_row = [key, len(rows)]
                for i in range(2, len(requested_columns)):
                    if i == 2:
                        agg_row.append(round(sum(float(r[i]) for r in rows if i < len(r) and str(r[i]).replace('.', '').isdigit()), 2))
                    else:
                        agg_row.append('-')
                aggregated_rows.append(agg_row)
            
            filtered_rows = aggregated_rows
            final_columns = [group_col, 'count'] + final_columns[2:]
    
    # Apply ORDER BY (simplified)
    if order_by:
        order_col = order_by.replace(' DESC', '').replace(' ASC', '').strip().lower()
        descending = 'DESC' in order_by.upper()
        
        # Find order column index
        order_idx = -1
        for i, col in enumerate(columns):
            if col.lower() == order_col:
                order_idx = i
                break
        
        if order_idx >= 0:
            try:
                filtered_rows.sort(
                    key=lambda x: float(x[order_idx]) if order_idx < len(x) and str(x[order_idx]).replace('.', '').isdigit() else str(x[order_idx]) if order_idx < len(x) else '',
                    reverse=descending
                )
            except:
                # If sorting fails, keep original order
                pass
    
    # Apply LIMIT
    final_rows = filtered_rows[:limit]
    
    # Select only requested columns
    final_data = []
    for row in final_rows:
        new_row = []
        for idx in column_indices:
            if idx < len(row):
                new_row.append(row[idx])
            else:
                # Generate data for missing columns
                if 'id' in final_columns[len(new_row)].lower():
                    new_row.append(len(final_data) + 1)
                elif 'name' in final_columns[len(new_row)].lower():
                    new_row.append(f'Generated {len(final_data) + 1}')
                elif 'date' in final_columns[len(new_row)].lower():
                    new_row.append('2024-01-15')
                elif 'amount' in final_columns[len(new_row)].lower():
                    new_row.append(round(100 + len(final_data) * 25.5, 2))
                else:
                    new_row.append('N/A')
        final_data.append(new_row)
    
    return {
        'columns': final_columns,
        'rows': final_data,
        'query_info': {
            'table_used': parsed_query['table_name'],
            'row_count': row_count,
            'file_type': file_type
        }
    }

def evaluate_where_clause(row, columns, where_clause):
    """Simple WHERE clause evaluation"""
    where_clause = where_clause.upper()
    
    # Check for simple conditions
    if '>' in where_clause:
        parts = where_clause.split('>')
        if len(parts) == 2:
            col_name = parts[0].strip()
            value = parts[1].strip()
            
            # Find column index
            col_idx = -1
            for i, col in enumerate(columns):
                if col.upper() == col_name:
                    col_idx = i
                    break
            
            if col_idx >= 0 and col_idx < len(row):
                try:
                    row_value = float(row[col_idx])
                    compare_value = float(value)
                    return row_value > compare_value
                except:
                    return True  # If can't compare, include row
    
    elif '<' in where_clause:
        parts = where_clause.split('<')
        if len(parts) == 2:
            col_name = parts[0].strip()
            value = parts[1].strip()
            
            # Find column index
            col_idx = -1
            for i, col in enumerate(columns):
                if col.upper() == col_name:
                    col_idx = i
                    break
            
            if col_idx >= 0 and col_idx < len(row):
                try:
                    row_value = float(row[col_idx])
                    compare_value = float(value)
                    return row_value < compare_value
                except:
                    return True
    
    elif 'LIKE' in where_clause:
        parts = where_clause.split('LIKE')
        if len(parts) == 2:
            col_name = parts[0].strip()
            pattern = parts[1].strip().strip("'%")
            
            # Find column index
            col_idx = -1
            for i, col in enumerate(columns):
                if col.upper() == col_name:
                    col_idx = i
                    break
            
            if col_idx >= 0 and col_idx < len(row):
                row_value = str(row[col_idx]).upper()
                return pattern.upper() in row_value
    
    # Default: include row if we can't evaluate
    return True


def _process_athena_results(self, results):
    """Process Athena results into displayable format"""
    if not results or 'ResultSet' not in results:
        return {'columns': [], 'rows': []}
    
    result_set = results['ResultSet']
    rows = result_set.get('Rows', [])
    
    if not rows:
        return {'columns': [], 'rows': []}
    
    # Extract headers from first row
    headers = [col.get('VarCharValue', '') for col in rows[0]['Data']]
    
    # Extract data from remaining rows
    data_rows = []
    for row in rows[1:]:
        data_rows.append([col.get('VarCharValue', '') for col in row['Data']])
    
    return {
        'columns': headers,
        'rows': data_rows[:100]  # Limit to 100 rows for display
    }
    
    
@login_required
def upload_file(request):
    """Handle actual file uploads"""
    if request.method == 'POST':
        form = FileUploadForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            bucket = form.cleaned_data['bucket']
            description = form.cleaned_data.get('description', '')
            
            # Get file information
            file_name = uploaded_file.name
            file_size_mb = uploaded_file.size / (1024 * 1024)  # Convert to MB
            
            # Determine file type from extension
            file_ext = os.path.splitext(file_name)[1].lower()
            file_type_map = {
                '.csv': 'csv',
                '.json': 'json',
                '.txt': 'text',
                '.parquet': 'parquet',
                '.avro': 'avro'
            }
            file_type = file_type_map.get(file_ext, 'unknown')
            
            # Read and analyze file content
            file_content = uploaded_file.read().decode('utf-8', errors='ignore')
            
            # Analyze file based on type
            metadata = analyze_file_content(file_content, file_type, file_name)
            metadata['description'] = description
            metadata['original_filename'] = file_name
            metadata['uploaded_by'] = request.user.username
            
            # Save file to local storage (simulating S3)
            local_file_path = save_file_locally(uploaded_file, request.user.username, bucket.name)
            
            # Create DataFile record
            data_file = DataFile.objects.create(
                name=file_name,
                bucket=bucket,
                file_type=file_type,
                size_mb=round(file_size_mb, 2),
                created_by=request.user,
                metadata=json.dumps(metadata),
                local_file_path=local_file_path,
                is_real_aws=False  # For now, we're simulating
            )
            
            messages.success(request, f'File "{file_name}" uploaded successfully!')
            return redirect('list_files')
    else:
        form = FileUploadForm(request.user)
    
    # Get user's buckets
    buckets = S3Bucket.objects.filter(created_by=request.user)
    
    return render(request, 'datalake/upload_file.html', {
        'form': form,
        'buckets': buckets
    })

def analyze_file_content(content, file_type, file_name):
    """Analyze file content and extract metadata"""
    metadata = {
        'analyzed_at': datetime.now().isoformat(),
        'file_type': file_type,
        'columns': [],
        'row_count': 0,
        'sample_data': []
    }
    
    try:
        if file_type == 'csv':
            # Parse CSV
            csv_reader = csv.reader(content.splitlines())
            rows = list(csv_reader)
            if rows:
                metadata['columns'] = rows[0]
                metadata['row_count'] = len(rows) - 1
                metadata['sample_data'] = rows[1:6]  # First 5 data rows
                
        elif file_type == 'json':
            # Parse JSON
            try:
                data = json_lib.loads(content)
                if isinstance(data, list):
                    metadata['row_count'] = len(data)
                    if data:
                        # Get keys from first object as columns
                        if isinstance(data[0], dict):
                            metadata['columns'] = list(data[0].keys())
                            metadata['sample_data'] = data[:3]  # First 3 items
                elif isinstance(data, dict):
                    metadata['columns'] = list(data.keys())
                    metadata['row_count'] = 1
            except:
                metadata['columns'] = ['json_data']
                
        elif file_type == 'text':
            lines = content.split('\n')
            metadata['row_count'] = len(lines)
            metadata['sample_data'] = lines[:5]
            
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata

def save_file_locally(uploaded_file, username, bucket_name):
    """Save uploaded file to local storage (simulating S3)"""
    # Create user directory structure
    user_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', username, bucket_name)
    os.makedirs(user_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(user_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    return file_path

@login_required
def list_files(request):
    """List all uploaded files"""
    files = DataFile.objects.filter(bucket__created_by=request.user).order_by('-upload_date')
    
    return render(request, 'datalake/list_files.html', {
        'files': files
    })

@login_required
def view_file(request, file_id):
    """View file details and content"""
    data_file = get_object_or_404(DataFile, id=file_id, bucket__created_by=request.user)
    
    # Parse metadata
    metadata = json.loads(data_file.metadata) if data_file.metadata else {}
    
    # Try to read file content if it exists locally
    file_content = None
    if data_file.local_file_path and os.path.exists(data_file.local_file_path):
        try:
            with open(data_file.local_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read(5000)  # Read first 5000 chars
        except:
            file_content = "[Binary file - content not displayable]"
    
    return render(request, 'datalake/view_file.html', {
        'file': data_file,
        'metadata': metadata,
        'file_content': file_content
    })

def _get_sample_columns(self, sample_type, file_format):
    """Get column names for sample data"""
    if sample_type == 'sales':
        return ['id', 'customer_id', 'product', 'amount', 'date', 'region']
    elif sample_type == 'logs':
        return ['timestamp', 'level', 'message', 'user_id', 'ip_address']
    elif sample_type == 'users':
        return ['user_id', 'name', 'email', 'registration_date', 'status']
    return ['column1', 'column2', 'column3']

def _generate_sample_content(self, sample_type, file_format):
    """Generate sample content based on type and format"""
    # This is simplified - in real app, generate proper content
    return f"Sample {sample_type} data in {file_format} format"

