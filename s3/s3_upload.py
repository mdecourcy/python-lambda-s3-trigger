import os

import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from pathlib import Path

def upload_to_aws(local_file, bucket, s3_file, access, secret):
    s3 = boto3.client('s3', aws_access_key_id=access,
                      aws_secret_access_key=secret)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def main():
    dotenv_path = Path('../app.env')
    load_dotenv(dotenv_path=dotenv_path)
    s3_bucket = os.getenv('S3_BUCKET')
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    print(s3_bucket)
    uploaded = upload_to_aws('../assets/TestFiles/site1.xml', s3_bucket, 'site1.xml', access_key, secret_key)
    print(uploaded)

main()