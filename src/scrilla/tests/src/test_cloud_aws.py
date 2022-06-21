import pytest
from moto import mock_dynamodb

from scrilla.cloud import aws

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

def test_dynamo_table_exceptions():
    pass