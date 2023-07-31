dynamo_price_table_conf = {
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
dynamo_interest_table_conf = {
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
dynamo_correlation_table_conf = {
    'AttributeDefinitions': [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
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
            'AttributeName': 'id',
            'KeyType': 'HASH'
        },
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'AssetTelescoping1',
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
            'Projection': {
                'ProjectionType': 'KEYS_ONLY'
            }
        },
        {
            'IndexName': 'AssetTelescoping2',
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
dynamo_profile_table_conf = {
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
