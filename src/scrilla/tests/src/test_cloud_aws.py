import pytest
import os
from moto import mock_dynamodb

from scrilla.cloud import aws
from botocore.exceptions import ClientError, ParamValidationError

@pytest.fixture(autouse=True)
def cache_env():
    os.environ.setdefault('CACHE_MODE', 'dynamodb')
    
@pytest.mark.parametrize('params,expected',[
    (
        {
            'param1' : 'test',
            'param2': 45,
            'param3': False,
            'param4': None,
            'param5': [1, 2, 3, 4],
            'param6': ['a', 'b', 'c'],
            'param7': 54.53
        },
        [
            { 'S': 'test' },
            { 'N': 45 },
            { 'BOOL': False },
            { 'NULL': True },
            { 'NS': [1, 2, 3, 4] },
            { 'SS': ['a', 'b', 'c'] },
            { 'N': 54.53 }
        ]
    ),
    (
        {},
        None
    ),
    (
        None, 
        None
    )
])
def test__dynamo_params(params, expected):
    assert aws._dynamo_params(params) == expected

def test_specify_dynamo_configuration(table_conf, expected):
    pass

@pytest.mark.parametrize('table_conf',[
    {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
        'TableName': 'prices',
        'KeySchema': [
            {
                'AttributeName': 'ticker',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'
            }
        ],
        'BillingMode': 'PAY_PER_REQUEST'
    }
])
@mock_dynamodb
def test_dynamo_table(table_conf):
    response = aws.dynamo_table(table_conf)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get('TableDescription', None) is not None
    assert response['TableDescription'].get('TableName', None) is not None
    assert response['TableDescription']['TableName'] == table_conf['TableName']
    assert response['TableDescription'].get('TableArn', None) is not None
    assert table_conf['TableName'] in response['TableDescription']['TableArn']
    assert response.get('ResponseMetadata') is not None
    assert response['ResponseMetadata'].get('HTTPStatusCode', None) is not None
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200 

@pytest.mark.parametrize('table_conf',[
    {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
    }
])
@mock_dynamodb
def test_dynamo_table_exceptions(table_conf):
    response= aws.dynamo_table(table_conf)
    assert isinstance(response, ParamValidationError)


@pytest.mark.parametrize('table_conf',[
    {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
        'TableName': 'prices',
        'KeySchema': [
            {
                'AttributeName': 'ticker',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'
            }
        ],
        'BillingMode': 'PAY_PER_REQUEST'
    }
])
@mock_dynamodb
def test_dynamo_table_duplication(table_conf):
    first = aws.dynamo_table(table_conf)
    second = aws.dynamo_table(table_conf)
    assert isinstance(first, dict)
    assert first['TableDescription']['TableName'] == table_conf['TableName']
    assert isinstance(second, ClientError)
