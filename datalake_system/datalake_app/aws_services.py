import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import uuid
import json
from datetime import datetime

class AWSService:
    def __init__(self, user):
        self.user = user
        self.aws_config = getattr(user, 'aws_config', None)
        
    def is_aws_configured(self):
        """Check if AWS credentials are configured"""
        if not self.aws_config or not self.aws_config.use_real_aws:
            return False
        
        try:
            sts = self.get_sts_client()
            sts.get_caller_identity()
            return True
        except Exception:
            return False
    
    def get_aws_clients(self):
        """Get AWS service clients"""
        if not self.is_aws_configured():
            return None
        
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_config.aws_access_key_id,
                aws_secret_access_key=self.aws_config.aws_secret_access_key,
                region_name=self.aws_config.aws_region
            )
            
            return {
                's3': session.client('s3'),
                'glue': session.client('glue'),
                'athena': session.client('athena'),
                'sts': session.client('sts')
            }
        except Exception as e:
            print(f"Error creating AWS clients: {e}")
            return None
    
    # S3 Operations
    def create_s3_bucket(self, bucket_name):
        """Create a real S3 bucket"""
        if not self.is_aws_configured():
            return None
        
        try:
            clients = self.get_aws_clients()
            if clients:
                clients['s3'].create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.aws_config.aws_region
                    }
                )
                return f"s3://{bucket_name}"
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                return f"s3://{bucket_name}"
            print(f"Error creating bucket: {e}")
        return None
    
    def list_s3_buckets(self):
        """List real S3 buckets"""
        if not self.is_aws_configured():
            return []
        
        try:
            clients = self.get_aws_clients()
            if clients:
                response = clients['s3'].list_buckets()
                return [bucket['Name'] for bucket in response['Buckets']]
        except Exception as e:
            print(f"Error listing buckets: {e}")
        return []
    
    def upload_to_s3(self, bucket_name, file_name, content):
        """Upload file to S3"""
        if not self.is_aws_configured():
            return None
        
        try:
            clients = self.get_aws_clients()
            if clients:
                key = f"uploads/{self.user.username}/{file_name}"
                clients['s3'].put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=content
                )
                return key
        except Exception as e:
            print(f"Error uploading to S3: {e}")
        return None
    
    # Glue Operations
    def create_glue_crawler(self, crawler_name, bucket_name):
        """Create a real Glue crawler"""
        if not self.is_aws_configured():
            return None
        
        try:
            clients = self.get_aws_clients()
            if clients:
                crawler_name = f"{crawler_name}-{self.user.username}"
                
                # Create IAM role name for crawler (simplified - in real scenario, need proper IAM setup)
                role_name = f"GlueServiceRole-{self.user.username}"
                
                clients['glue'].create_crawler(
                    Name=crawler_name,
                    Role=role_name,
                    DatabaseName='data_lake_db',
                    Targets={
                        'S3Targets': [
                            {
                                'Path': f"s3://{bucket_name}/",
                            }
                        ]
                    },
                    SchemaChangePolicy={
                        'UpdateBehavior': 'UPDATE_IN_DATABASE',
                        'DeleteBehavior': 'LOG'
                    }
                )
                return crawler_name
        except Exception as e:
            print(f"Error creating crawler: {e}")
        return None
    
    def start_glue_crawler(self, crawler_name):
        """Start a real Glue crawler"""
        if not self.is_aws_configured():
            return False
        
        try:
            clients = self.get_aws_clients()
            if clients:
                clients['glue'].start_crawler(Name=crawler_name)
                return True
        except Exception as e:
            print(f"Error starting crawler: {e}")
        return False
    
    # Athena Operations
    def execute_athena_query(self, query, database='default'):
        """Execute real Athena query"""
        if not self.is_aws_configured():
            return None
        
        try:
            clients = self.get_aws_clients()
            if clients:
                # Create output location
                output_location = f"s3://athena-results-{self.user.username}-{uuid.uuid4()}/"
                
                response = clients['athena'].start_query_execution(
                    QueryString=query,
                    QueryExecutionContext={
                        'Database': database
                    },
                    ResultConfiguration={
                        'OutputLocation': output_location
                    }
                )
                return response['QueryExecutionId']
        except Exception as e:
            print(f"Error executing Athena query: {e}")
        return None
    
    def get_query_results(self, query_execution_id):
        """Get Athena query results"""
        if not self.is_aws_configured():
            return None
        
        try:
            clients = self.get_aws_clients()
            if clients:
                response = clients['athena'].get_query_results(
                    QueryExecutionId=query_execution_id
                )
                return response
        except Exception as e:
            print(f"Error getting query results: {e}")
        return None


class LocalSimulationService:
    """Local simulation service when AWS is not configured"""
    
    @staticmethod
    def create_s3_bucket(bucket_name):
        return f"simulated-s3://{bucket_name}"
    
    @staticmethod
    def list_s3_buckets():
        return ['simulated-bucket-1', 'simulated-bucket-2', 'simulated-bucket-3']
    
    @staticmethod
    def upload_to_s3(bucket_name, file_name, content):
        return f"simulated-s3://{bucket_name}/uploads/{file_name}"
    
    @staticmethod
    def create_glue_crawler(crawler_name, bucket_name):
        return f"simulated-crawler-{crawler_name}"
    
    @staticmethod
    def start_glue_crawler(crawler_name):
        return True
    
    @staticmethod
    def execute_athena_query(query, database='default'):
        return f"simulated-query-{uuid.uuid4()}"
    
    @staticmethod
    def get_query_results(query_execution_id):
        # Return simulated results
        return {
            'ResultSet': {
                'Rows': [
                    {'Data': [{'VarCharValue': 'id'}, {'VarCharValue': 'name'}, {'VarCharValue': 'value'}]},
                    {'Data': [{'VarCharValue': '1'}, {'VarCharValue': 'John'}, {'VarCharValue': '100'}]},
                    {'Data': [{'VarCharValue': '2'}, {'VarCharValue': 'Jane'}, {'VarCharValue': '200'}]},
                ]
            }
        }