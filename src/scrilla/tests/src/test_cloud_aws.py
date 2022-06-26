import os
os.environ['CACHE_MODE'] = 'dynamodb'

import pytest
import datetime
from moto import mock_dynamodb
from botocore.exceptions import ClientError, ParamValidationError


from scrilla import settings
from scrilla.cloud import aws

@pytest.fixture()
def singleton_table_conf():
    return {
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
    }

@pytest.mark.parametrize('params,expected',[
    (
        {
            'param1' : 'test',
            'param2': 45,
            'param3': False,
            'param4': None,
            'param5': [1, 2, 3, 4],
            'param6': ['a', 'b', 'c'],
            'param7': 54.53,
            'param8': datetime.date(year=2020, month=2, day=1)
        },
        [
            { 'S': 'test' },
            { 'N': '45' },
            { 'BOOL': 'False' },
            { 'NULL': 'True' },
            { 'NS': [ '1', '2', '3', '4'] },
            { 'SS': ['a', 'b', 'c'] },
            { 'N': '54.53' },
            { 'S': '2020-02-01' }
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
def test_dynamo_json_to_params(params, expected):
    assert aws.dynamo_json_to_params(params) == expected


@pytest.mark.parametrize('params,expected',[
    (
        {
            'Items': [
                {
                    'annual_return': {
                        'N': '0.1223' 
                    },
                    'annual_volatility': {
                        'N': '0.0432'
                    }
                },
            ],
        },
        [
            {
                'annual_return': 0.1223,
                'annual_volatility': 0.0432
            },
        ]
    ),
    (
        {
            'Items': [
                {
                    'ticker': {
                        'S': 'ALLY'
                    },
                    'date': {
                        'S': '2020-01-01'
                    },
                    'open': {
                        'N': 10
                    },
                    'close': {
                        'N': 11
                    }
                },
                {
                    'ticker': {
                        'S': 'ALLY'
                    },
                    'date': {
                        'S': '2020-01-02'
                    },
                    'open': {
                        'N': 12
                    },
                    'close': {
                        'N': 13
                    }
                }
            ],
        },
        [
            {
                'ticker': 'ALLY',
                'date': '2020-01-01',
                'open': 10,
                'close': 11
            },
            {
                'ticker': 'ALLY',
                'date': '2020-01-02',
                'open': 12,
                'close': 13
            }
        ]

    )
])
def test_dynamo_params_to_json(params,expected):
    assert aws.dynamo_params_to_json(params) == expected

def test_specify_dynamo_configuration(singleton_table_conf):
    assert aws.dynamo_table_conf(singleton_table_conf)['BillingMode'] == settings.DYNAMO_CONF['BillingMode']


@mock_dynamodb
def test_dynamo_table(singleton_table_conf):
    singleton_table_conf = table_conf = aws.dynamo_table_conf(singleton_table_conf)
    response = aws.dynamo_table(singleton_table_conf)
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
def test_dynamo_table_exceptions_no_table(table_conf):
    response= aws.dynamo_table(table_conf)
    print(response)
    print(vars(response))
    assert isinstance(response, KeyError)

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
        'TableName': 'table'
    }
])
@mock_dynamodb
def test_dynamo_table_exceptions_bad_params(table_conf):
    response = aws.dynamo_table(table_conf)
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
