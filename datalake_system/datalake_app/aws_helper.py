"""
AWS Connection Helper - Handles AWS connections without errors
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
import logging

logger = logging.getLogger(__name__)

class AWSConnection:
    """Handles AWS connections with proper error handling"""
    
    @staticmethod
    def validate_credentials(access_key, secret_key, region='us-east-1'):
        """
        Validate AWS credentials without throwing errors to users
        Returns: (is_valid, message, aws_account_id)
        """
        if not access_key or not secret_key:
            return False, "AWS Access Key ID and Secret Access Key are required", None
        
        try:
            # Create session with provided credentials
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            # Test connection with STS
            sts_client = session.client('sts')
            
            # Get caller identity
            identity = sts_client.get_caller_identity()
            aws_account_id = identity.get('Account', 'Unknown')
            user_arn = identity.get('Arn', 'Unknown')
            
            return True, f"Connected successfully to AWS Account: {aws_account_id}", aws_account_id
            
        except NoCredentialsError:
            return False, "AWS credentials not found. Please check your Access Key ID and Secret Access Key.", None
        except PartialCredentialsError:
            return False, "Incomplete AWS credentials. Both Access Key ID and Secret Access Key are required.", None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'InvalidClientTokenId':
                return False, "Invalid Access Key ID. Please check your AWS Access Key.", None
            elif error_code == 'SignatureDoesNotMatch':
                return False, "Invalid Secret Access Key. Please check your AWS Secret Key.", None
            elif error_code == 'RequestExpired':
                return False, "AWS credentials have expired. Please generate new credentials.", None
            else:
                return False, f"AWS Error: {error_message}", None
        except Exception as e:
            logger.error(f"Unexpected error validating AWS credentials: {str(e)}")
            return False, f"Connection error: {str(e)}", None
    
    @staticmethod
    def get_aws_client(service_name, access_key, secret_key, region='us-east-1'):
        """Get AWS client with error handling"""
        try:
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return session.client(service_name)
        except Exception as e:
            logger.error(f"Error creating {service_name} client: {str(e)}")
            return None
    
    @staticmethod
    def get_required_permissions():
        """Return required IAM permissions for students"""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:*",
                        "glue:*",
                        "athena:*",
                        "iam:GetUser",
                        "sts:GetCallerIdentity"
                    ],
                    "Resource": "*"
                }
            ]
        }
    
    @staticmethod
    def create_test_resources(access_key, secret_key, region):
        """Create test resources to verify full access"""
        try:
            s3 = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            ).client('s3')
            
            # Try to list buckets (requires s3:ListAllMyBuckets)
            response = s3.list_buckets()
            bucket_count = len(response.get('Buckets', []))
            
            return True, f"Successfully connected. Found {bucket_count} S3 buckets.", bucket_count
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'AccessDenied':
                return False, "Permission denied. Your IAM user needs S3, Glue, and Athena permissions.", 0
            else:
                return False, f"AWS Error: {e.response['Error']['Message']}", 0