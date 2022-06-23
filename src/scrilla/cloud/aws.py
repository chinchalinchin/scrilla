from pprint import pprint
import boto3
from botocore.exceptions import ClientError, ParamValidationError
from datetime import date
from scrilla import settings
from scrilla.util import outputter, dater
logger = outputter.Logger("scrilla.cloud.aws", settings.LOG_LEVEL)


def _dynamo_params(document: dict):
    if document is None or len(document) == 0:
        return None
    dynamo_json = []
    for entry in document.values():
        if isinstance(entry, str):
            dynamo_json.append({'S': str(entry)})
        elif isinstance(entry, bool):
            # NOTE: bool evaluation has to come before int/float evaluation
            # because False/True also evaluate to ints in python
            dynamo_json.append({'BOOL': str(entry)})
        elif isinstance(entry, (int, float)):
            dynamo_json.append({'N': str(entry)})
        elif isinstance(entry, list):
            if all(isinstance(el, str) for el in entry):
                dynamo_json.append({'SS': entry})
            if all(isinstance(el, (int, float)) for el in entry):
                dynamo_json.append({'NS': [str(el) for el in entry]})
        elif isinstance(entry, date):
            dynamo_json.append({'S': dater.to_string(entry)})

        elif entry is None:
            dynamo_json.append({'NULL': 'True'})
    return dynamo_json


def specify_dynamo_table_conf(table_configuration):
    table_configuration.update(settings.DYNAMO_CONF)
    return table_configuration


def dynamo_statement_args(statement, params=None):
    if params is None:
        return {
            'Statement': statement
        }
    return {
        'Statement': statement,
        'Parameters': _dynamo_params(params)
    }


def dynamo_client():
    return boto3.client('dynamodb')


def dynamo_resource():
    return boto3.resource('dynamodb')


def dynamo_table(table_configuration: dict):
    try:
        logger.debug(
            f'Provisioning DynamoDB {table_configuration["TableName"]} table', 'dynamo_table')
        return dynamo_client().create_table(**table_configuration)
    except (ClientError, ParamValidationError) as e:
        if not (
            'Table already exists' in e.response['Error']['Message'] or
            'Table is being created' in e.response['Error']['Message']
        ):
            logger.error(e, 'dynamo_table')
            logger.verbose(f'\n\t\t{table_configuration}', 'dynamo_table')
        return e
    except KeyError as e:
        logger.error(e, 'dynamo_table')
        return e


def dynamo_transaction(transaction, formatter):
    try:
        if isinstance(formatter, list):
            statements = [dynamo_statement_args(
                transaction, params) for params in formatter]
            return dynamo_client().execute_transaction(
                TransactStatements=statements
            )
        return dynamo_client().execute_transaction(
            TransactStatements=[
                dynamo_statement_args(transaction, formatter)]
        )
    except (ClientError, ParamValidationError) as e:
        logger.error(e, 'dynamo_table')
        logger.verbose(f'\n\t\t{transaction}')
        logger.verbose(f'\n\t\t{formatter}')
