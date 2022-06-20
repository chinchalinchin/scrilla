import boto3


def dynamo_client():
    return boto3.client('dynamodb')


def dynamo_resource():
    return boto3.resource('dynamodb')
