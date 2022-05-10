import json
import urllib.parse
import boto3
import logging
from lxml import objectify

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('loading function')
print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response, content_type = s3_event_handler(bucket, key)

        if content_type is "json":
            obj = deserialize_json(response)
        elif content_type is "text/xml":
            obj = deserialize_xml(response)
        else:
            logger.info("Invalid content type")

        sql_connect()

        sql_query()

        return response['ContentType']
    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e

def sql_query():

def sql_connect():


def s3_event_handler(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content_type = response['ContentType']
    logger.info('Reading {} from {}. Content type: '.format(key, bucket, content_type))
    print("CONTENT TYPE: " + content_type)
    return response, content_type

def deserialize_json(resp):
    return json.dumps(resp)


def deserialize_xml(resp):
    return objectify.fromstring(resp)
