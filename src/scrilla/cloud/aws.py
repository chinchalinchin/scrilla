import boto3
from botocore.exceptions import ClientError, ParamValidationError

from scrilla import settings
from scrilla.util import outputter
logger = outputter.Logger("scrilla.cloud.aws", settings.LOG_LEVEL)


def _dynamo_params(document: dict):
    if document is None or len(document) == 0:
        return None
    dynamo_json = []
    for entry in document.values():
        if isinstance(entry, str):
            dynamo_json.append({'S': entry})
        elif isinstance(entry, bool):
            # NOTE: bool evaluation has to come before int/float evaluation
            # because False/True also evaluate to a ints in python
            dynamo_json.append({'BOOL': entry})
        elif isinstance(entry, int) or isinstance(entry, float):
            dynamo_json.append({'N': entry})
        elif isinstance(entry, list):
            if all(isinstance(el, str) for el in entry):
                dynamo_json.append({'SS': entry})
            if all(isinstance(el, int) or isinstance(el, float) for el in entry):
                dynamo_json.append({'NS': entry})
        elif entry is None:
            dynamo_json.append({'NULL': True})
    return dynamo_json

def specify_dynamo_table_conf(table_configuration):
    return table_configuration.update(settings.DYNAMO_CONF)

def dynamo_statement_args(statement, params = None):
    if params is None:
        return {
            'Statement': statement
        }
    return {
        'Statement': statement,
        'Params': _dynamo_params(params)
    }


def dynamo_client():
    return boto3.client('dynamodb')


def dynamo_resource():
    return boto3.resource('dynamodb')


def dynamo_table(table_configuration: dict):
    try:
        return dynamo_client().create_table(**table_configuration)
    except (ClientError, ParamValidationError) as e:
        logger.error(e)
        return e
