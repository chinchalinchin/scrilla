import boto3
from botocore.exceptions import ClientError

from scrilla import settings
from scrilla.util import outputter
logger = outputter.Logger("scrilla.cloud.aws", settings.LOG_LEVEL)


def dynamo_client():
    return boto3.client('dynamodb')


def dynamo_resource():
    return boto3.resource('dynamodb')


def dynamo_table(table_configuration: dict):
    client = dynamo_client()
    try:
        return client.create_table(**table_configuration)
    except ClientError as e:
        logger.error(e)
        return e
        # TODO: error handling goes here
