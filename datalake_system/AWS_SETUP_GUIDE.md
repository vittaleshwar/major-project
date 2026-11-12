# AWS Setup Guide for Students

## Step 1: Create AWS Account (if you don't have one)
1. Go to [https://aws.amazon.com/](https://aws.amazon.com/)
2. Click "Create an AWS Account"
3. Follow the signup process (you'll need a credit card, but most services have free tier)

## Step 2: Create IAM User
1. Login to AWS Console
2. Search for "IAM" in services
3. Click "Users" in left sidebar
4. Click "Create user"
5. Enter username: `data-lake-student`
6. Select "Provide user access to the AWS Management Console" (optional)
7. Click "Next"

## Step 3: Set Permissions
1. Click "Attach policies directly"
2. Search for and select these policies:
   - `AmazonS3FullAccess`
   - `AWSGlueConsoleFullAccess`
   - `AmazonAthenaFullAccess`
3. Click "Next"

## Step 4: Create Access Keys
1. After user is created, click on the username
2. Go to "Security credentials" tab
3. Scroll to "Access keys"
4. Click "Create access key"
5. Select "Application running outside AWS"
6. Click "Next"
7. Add description: "Data Lake Project"
8. Click "Create access key"
9. **IMPORTANT**: Copy both:
   - **Access Key** (starts with AKIA...)
   - **Secret Key** (long string)

## Step 5: Configure in Data Lake System
1. Login to Data Lake System
2. Go to Settings → AWS Configuration
3. Enable "Real AWS Connection"
4. Paste your Access Key and Secret Key
5. Select your region (usually `us-east-1`)
6. Click "Test Connection"
7. If successful, click "Save"

## Common Issues & Solutions:

### Issue: "InvalidClientTokenId"
**Solution**: Check your Access Key ID. It should start with `AKIA` followed by 16 characters.

### Issue: "SignatureDoesNotMatch"
**Solution**: Check your Secret Access Key. Make sure you copied it correctly.

### Issue: "AccessDenied"
**Solution**: Your IAM user needs these permissions:
- AmazonS3FullAccess
- AWSGlueConsoleFullAccess  
- AmazonAthenaFullAccess

### Issue: Can't find S3/Glue/Athena
**Solution**: Make sure you're in the correct AWS region. Try `us-east-1`.

## For Local Simulation (No AWS Account):
1. Leave AWS credentials blank
2. Uncheck "Enable Real AWS Connection"
3. Click "Save"
4. Use simulated AWS services (perfect for learning)

## Cost Considerations:
- S3: First 5GB free for 12 months
- Glue: First 1 million objects crawled free per month
- Athena: First 1TB of queries free per month
- **Always enable billing alerts to avoid unexpected charges!**