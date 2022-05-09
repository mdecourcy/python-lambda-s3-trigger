import sys
import logging
import psycopg2
import json
import os

import dotenv
from dotenv import load_dotenv

logger = logging.getLogger()
logger.setLevel(logging.INFO)



def connect(rds_host, rds_username, rds_user_pwd, rds_db_name):
    try:
        conn_string = "host=%s user=%s password=%s dbname=%s" % \
                      (rds_host, rds_username, rds_user_pwd, rds_db_name)
        conn = psycopg2.connect(conn_string)
    except:
        logger.error("ERROR: Could not connect to Postgres instance.")
        sys.exit()

    logger.info("SUCCESS: Connection to RDS Postgres instance succeeded")

    return conn

def handler(conn):

    query = """select id, name, job_title
            from employee
            order by 1"""

    with conn.cursor() as cur:
        rows = []
        cur.execute(query)
        for row in cur:
            rows.append(row)

    return { 'statusCode': 200, 'body': rows }

def get_env():
    dotenv_path = Path('../app.env')
    load_dotenv(dotenv_path=dotenv_path)
    rds_host = os.getenv('RDS_HOST')
    rds_username = os.getenv('RDS_USERNAME')
    rds_user_pwd = os.getenv('RDS_USER_PWD')
    rds_db_name = os.getenv('RDS_DB_NAME')

    return rds_host, rds_username, rds_user_pwd, rds_db_name

def main():
    rds_host, rds_username, rds_user_pwd, rds_db_name = get_env()
    conn = connect(rds_host, rds_username, rds_user_pwd, rds_db_name)
    handler(conn)
