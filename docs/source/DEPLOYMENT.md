# Deployment

TODO 

## AWS Deployments

TODO

### DynamoDB Cache

Tables
------

1. `prices`

```json
{
    'AttributeDefinitions': [
        {
            'AttributeName': 'ticker',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'date',
            'AttributeType': 'S'
        },
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
```

2. `interest`

```json
{
    'AttributeDefinitions': [
        {
            'AttributeName': 'maturity',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'date',
            'AttributeType': 'S'
        },
    ],
    'TableName': 'interest',
    'KeySchema': [
        {
            'AttributeName': 'maturity',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'date',
            'KeyType': 'RANGE'
        }
    ],
}
```

3. `profile`

```json
{
    'AttributeDefinitions': [
        {
            'AttributeName': 'ticker',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'start_date',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'end_date',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'method',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'weekends',
            'AttributeType': 'N'
        }
    ],
    'TableName': 'profile',
    'KeySchema': [
        {
            'AttributeName': 'ticker',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'start_date',
            'KeyType': 'RANGE'
        }
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'DateTelescoping',
            'KeySchema': [
                {
                    'AttributeName': 'weekends',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'end_date',
                    'KeyType': 'RANGE'
                },
            ],
            'Projection': {
                'ProjectionType': 'KEYS_ONLY'
            }
        },
        {
            'IndexName': 'EstimationTelescoping',
            'KeySchema': [
                {
                    'AttributeName': 'method',
                    'KeyType': 'HASH'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            }
        }
    ]
}
```

4. `correlation`

```json
{
    'AttributeDefinitions': [
        {
            'AttributeName': 'ticker_1',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'ticker_2',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'start_date',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'end_date',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'method',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'weekends',
            'AttributeType': 'N'
        },
    ],
    'TableName': 'correlations',
    'KeySchema': [
        {
            'AttributeName': 'ticker_1',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'start_date',
            'KeyType': 'RANGE'
        }
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'AssetTelescoping',
            'KeySchema': [
                {
                    'AttributeName': 'ticker_2',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'end_date',
                    'KeyType': 'RANGE'
                },
            ],
            'Projection': {
                'ProjectionType': 'KEYS_ONLY'
            }
        },
        {
            'IndexName': 'WeekendTelescoping',
            'KeySchema': [
                {
                    'AttributeName': 'weekends',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'KEYS_ONLY'
            }
        },
        {
            'IndexName': 'EstimationTelescoping',
            'KeySchema': [
                {
                    'AttributeName': 'method',
                    'KeyType': 'HASH'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            }
        },
    ]
}
```

Prices
------

TODO: Key schemas goes here

Interest
--------

TODO: Key schema goes here

Profile
-------

TODO: Key schema goes here

Correlation
-----------

TODO: Key schema goes here

### Lambda Function

TODO

docker image

environment variable for type of function
