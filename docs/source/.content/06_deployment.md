# Deployment

_scrilla_ has been designed to interface with data services on the cloud. 

## AWS Deployments

_scrilla_ can be deployed relatively easily to **AWS** in a few different ways. 

The main thing to consider when deploying onto **AWS** is the cache. The cache can be pointed towards **DynamoDB**, instead of the default `sqlite` cache system, by configuring the **CACHE_MODE** environment variable (see [Configuration](./CONFIGURATION.md#environment-variables) for more information) so that all prices, interest and statistics are stored in tables on the cloud. 

A `lamdba_handler` included with the distribution can be deployed to **AWS Lambda**, given a role with **DynamoDB** and then configured via environment variables to execute a particular function from `scrilla`'s library. 


### IAM Role

The process executing `scrilla` must be given a role that gives it permission to access **DynamoDB**. The policy below can be adapted for your specific account,

TODO: list policy here.

```yaml
    # policy here
```

### DynamoDB Cache

Set the environment variable **CACHE_MODE** to `dynamodb`. Instead of using a **SQLite** backend, _scrilla_ will then attempt to provision four tables within **DynamoDB**: `prices`, `interest`, `correlations` and `profile`. The configuration for each table is given below.

**NOTE**: The variable **DYNAMO_CONF** gets appended to each table configuration before it is posted to the **AWS** API. This variable collectively controls the billing and provisioning modes for the **DynamoDB** tables,

```python
DYNAMO_CONF = {
    'BillingMode': 'PAY_PER_REQUEST'  # PAY_PER_REQUEST | PROVISIONED
    # If PROVISIONED, the following lines need uncommented and configured:
    #
    # 'ProvisionedThroughput' : {
    #       'ReadCapacityUnits': 123,
    #       'WriteCapacityUnits': 123
    #  },
}
```

If you want finer-grained control over the pricing and speed of each table, you will need to edit this variable in the source code, rebuild and then re-install the wheel . See [SETUP](./SETUP.md#source) for more information on building _scrilla_ from source.

**Table Configurations**

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

### Lambda Function

TODO

docker image

example of lambda handler

```python
from scrilla.cloud.aws.handlers import *_handler
```

TODO: specific handler for each function?

OR 

environment variable for type of function?
