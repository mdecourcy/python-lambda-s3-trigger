import json
import urllib.parse
import boto3
import logging
import sys
import rds_config
from xmltodict3 import XmlTextToDict

import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('loading function')
print('Loading function')

s3 = boto3.client('s3')
rds_host = "postgres-cdc.c4kfm0baalsi.us-west-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response, content_type = s3_event_handler(bucket, key)

        file_data = response['Body'].read().decode()

        json_string = deserialize_response(file_data, content_type)

        date, site, first_shot, second_shot = objectify_json(json_string)

        conn = connect(rds_host)

        execute_queries(date, site, str(first_shot), str(second_shot), conn)

        return response['ContentType']
    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e


def s3_event_handler(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content_type = response['ContentType']
    logger.info('Reading {} from {}. Content type: '.format(key, bucket, content_type))
    print("CONTENT TYPE: " + content_type)
    return response, content_type


def deserialize_response(file, content_type):
    try:
        if 'json' in content_type:
            obj = json.loads(file)
        if 'xml' in content_type:
            text = file
            obj = XmlTextToDict(text, ignore_namespace=True).get_dict()
            print(json.dumps(obj))
        else:
            logger.error("Filetype not recognized. Please upload a file that is proper XML or JSON.")

    except Exception as e:
        print(e)
        raise e

    return obj


def objectify_json(json_string):
    js = False
    if 'date' in json_string:
        date = str(json_string["date"]["year"]) + str(json_string["date"]["month"]) + str(json_string["date"]["day"])
        js = True
    else:
        date = json_string['data']["@year"] + json_string['data']["@month"] + json_string['data']["@day"]

    if js:
        site = json_string["site"]
        vaccines = json_string["vaccines"]
    else:
        site = json_string['data']['site']
        site["id"] = site["@id"]
        vaccines = json_string['data']["vaccines"]["brand"]


    first_shot = 0
    second_shot = 0
    if not isinstance(vaccines, list):
        print("we made it to is instance")
        first_shot = int(vaccines["firstShot"])
        second_shot = int(vaccines["secondShot"])
    else:
        for x in vaccines:
            print(x)
            first_shot += int(x["firstShot"])
            second_shot += int(x["secondShot"])


    return date, site, first_shot, second_shot


def execute_queries(date_str, site, first_shot, second_shot, conn):
    site_query = """INSERT INTO sites VALUES ('{}', '{}', '{}') ON CONFLICT DO NOTHING""".format(site["id"],
                                                                                                 site["name"],
                                                                                                 site["zipCode"])
    print("SITE QUERY:", site_query)
    data_query = """INSERT INTO data VALUES ('{}', '{}', '{}', '{}') ON CONFLICT (site_id, date) DO UPDATE SET firstshot = EXCLUDED.firstshot, secondshot = EXCLUDED.secondshot""".format(
        site["id"], date_str, first_shot, second_shot)
    print("DATA QUERY: ", data_query)

    with conn.cursor() as cur:
        cur.execute(site_query)
        cur.execute(data_query)
        conn.commit()


def connect(rds_host):
    try:
        conn = psycopg2.connect(host=rds_host, user=name, password=password, database=db_name)

        conn.autocommit = True

    except Exception as e:
        logger.error("ERROR: Could not connect to Postgres instance.")
        raise e

    logger.info("SUCCESS: Connection to RDS Postgres instance succeeded")

    return conn
