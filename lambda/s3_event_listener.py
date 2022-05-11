import json
import urllib.parse
import boto3
import logging
import xml.etree.ElementTree as et
import sys
import rds_config

import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('loading function')
print('Loading function')

s3 = boto3.client('s3')
rds_host  = "postgres-cdc.c4kfm0baalsi.us-west-2.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response, content_type = s3_event_handler(bucket, key)
        file_data = response['Body'].read().decode()
        json_string = deserialize_response(file_data, content_type)
        objectify_json(json_string)

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
    print("DEBUG DEBUG CONTENT TYPE: ", content_type)
    if content_type is "binary/octet-stream":
        print("we made it here")
        obj = json.loads(file)
    elif content_type is "text/xml":
        parsed_xml = et.fromstring(file)
        # objectify_xml(parsed_xml)

    obj = json.loads(file)
    print(obj)

    return obj

def objectify_json(json_string):
    date = json_string["date"]
    site = json_string["site"]
    vaccines = json_string["vaccines"]

    first_shot = 0
    second_shot = 0
    for x in vaccines:
        first_shot += x["firstShot"]
        second_shot += x["secondShot"]

    conn = connect('postgres-cdc.c4kfm0baalsi.us-west-2.rds.amazonaws.com', 'postgres', 'Buzz2-Ample-Dwindling', 'documentstore')
    execute_queries(date, site, first_shot, second_shot, conn)

    return date, site, first_shot, second_shot


def execute_queries(date, site, first_shot, second_shot, conn):

    date_str = str(date["year"]) + str(date["month"]) + str(date["day"])
    site_query = """INSERT INTO sites VALUES ('{}', '{}', '{}') ON CONFLICT DO NOTHING""".format( site["id"], site["name"], site["zipCode"])
    print(site_query)
    data_query = """INSERT INTO data VALUES ('{}', '{}', '{}', '{}') ON CONFLICT (siteid) DO UPDATE SET firstshot = EXCLUDED.firstshot, secondshot = EXCLUDED.secondshot""".format(site["id"], date_str, first_shot, second_shot)
    print(data_query)

    with conn.cursor() as cur:
        cur.execute(site_query)
        cur.execute(data_query)
        for i in cur.fetchall():
            print(i)
        conn.commit()



def connect(rds_host, rds_username, rds_user_pwd, rds_db_name):
    try:
        # conn_string = "host=%s user=%s password=%s dbname=%s" % \
        #              (rds_host, rds_username, rds_user_pwd, rds_db_name)

        # print(conn_string)
        # conn = psycopg2.connect(dbname=rds_db_name, user=rds_username, host=rds_host, password=rds_user_pwd, port=5432)
        # conn_string = "host=%s database=%s user=postgres password=%s port=5432" % (rds_db_name, rds_user_pwd, rds_host)
        # print(conn_string)
        print("we're in connect")
        conn = psycopg2.connect(host=rds_host, user=name, password=password, database=db_name)

        conn.autocommit = True

    except Exception as e:
        logger.error("ERROR: Could not connect to Postgres instance.")
        raise e
        sys.exit()

    logger.info("SUCCESS: Connection to RDS Postgres instance succeeded")

    return conn