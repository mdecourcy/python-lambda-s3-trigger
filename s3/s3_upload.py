import os

import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from dotenv import load_dotenv
from pathlib import Path
import argparse
import sys

def upload_to_aws(local_file, bucket, s3_file, access, secret):
    s3 = boto3.client('s3', aws_access_key_id=access,
                      aws_secret_access_key=secret)

    file_name=s3_file
    extn=file_name.split(".", 1)
    print(extn)


    try:
        # s3.upload_file(local_file, bucket, s3_file)
        if "json" in extn:
            s3.upload_file(local_file, bucket, s3_file, ExtraArgs = {'ContentType':'json'})
        elif "xml" in extn:
            s3.upload_file(local_file, bucket, s3_file, ExtraArgs = {'ContentType':'text/xml'})



        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def get_env():
    dotenv_path = Path('../app.env')
    load_dotenv(dotenv_path=dotenv_path)
    s3_bucket = os.getenv('S3_BUCKET')
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')

    return s3_bucket, access_key, secret_key


def get_args():
    parser = argparse.ArgumentParser(description='s3 upload')
    parser.add_argument('--filepath', help="path to file to update eg ../assets/TestFiles/site1.xml")
    parser.add_argument('--filename', help="what your file will be named in s3")
    args = parser.parse_args(sys.argv[1:])
    file_path = args.filepath
    file_name = args.filename
    return file_path, file_name


def main():
    s3_bucket, access_key, secret_key = get_env()
    file_path, file_name = get_args()
    print("uploading {} to {}. The file will be named {}.".format(file_path, s3_bucket, file_name))
    upload_to_aws(file_path, s3_bucket, file_name, access_key, secret_key)


main()
