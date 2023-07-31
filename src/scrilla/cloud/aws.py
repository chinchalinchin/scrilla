from typing import List, Union
import boto3
from botocore.exceptions import ClientError, ParamValidationError
from datetime import date
from scrilla import settings
from scrilla.util import outputter, dater
logger = outputter.Logger("scrilla.cloud.aws", settings.LOG_LEVEL)

DYNAMO_STATEMENT_LIMIT = 25


def dynamo_client():
    return boto3.client('dynamodb')


def dynamo_resource():
    return boto3.resource('dynamodb')


def dynamo_json_to_params(document: dict) -> list:
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


def dynamo_params_to_json(document: dict) -> list:
    if 'Items' in list(document.keys()):
        json_list = []
        for doc in document['Items']:
            json_dict = {}
            for entry_key, entry_value in doc.items():
                type_key = list(entry_value.keys())[0]
                type_value = list(entry_value.values())[0]
                if type_key == 'N':
                    json_dict[entry_key] = float(type_value)
                elif type_key == 'S':
                    json_dict[entry_key] = type_value
                elif type_key == 'BOOL':
                    json_dict[entry_key] = type_value.lower() == 'true'
                elif type_key == 'SS':
                    json_dict[entry_key] = type_value
                elif type_key == 'NS':
                    json_dict[entry_key] = [float(el) for el in type_value]
                elif type_key == 'NULL':
                    json_dict[entry_key] = None
            json_list.append(json_dict)
        return json_list
    elif 'Responses' in list(document.keys()):
        # TODO: Error handling?
        pass


def dynamo_table_conf(table_configuration) -> dict:
    table_configuration.update(settings.DYNAMO_CONF)
    return table_configuration


def dynamo_statement_args(statement: str, params=None) -> dict:
    if params is None:
        return {
            'Statement': statement
        }
    return {
        'Statement': statement,
        'Parameters': dynamo_json_to_params(params)
    }


def dynamo_table(table_configuration: dict):
    try:
        logger.debug(
            f'Provisioning DynamoDB {table_configuration["TableName"]} table', 'dynamo_table')
        return dynamo_client().create_table(**table_configuration)
    except ClientError as e:
        if not (
            'Table already exists' in e.response['Error']['Message'] or
            'Table is being created' in e.response['Error']['Message']
        ):
            logger.error(e, 'dynamo_table')
            logger.verbose(f'\n\t\t{table_configuration}', 'dynamo_table')
        return e
    except ParamValidationError as e:
        logger.error(e, 'dynamo_Table')
        return e
    except KeyError as e:
        logger.error(e, 'dynamo_table')
        return e


def dynamo_transaction(transaction, formatter=None):
    try:
        if isinstance(formatter, list):
            statements = [dynamo_statement_args(
                transaction, params) for params in formatter]
            if len(statements) > DYNAMO_STATEMENT_LIMIT:
                loops = len(statements) // DYNAMO_STATEMENT_LIMIT + \
                    (1 if len(statements) % DYNAMO_STATEMENT_LIMIT != 0 else 0)
                return [
                    dynamo_params_to_json(
                        dynamo_client().execute_transaction(
                            TransactStatements=statements[i*DYNAMO_STATEMENT_LIMIT:
                                                          (i+1)*DYNAMO_STATEMENT_LIMIT]
                        ))
                    for i in range(0, loops)
                ]
            return dynamo_params_to_json(
                dynamo_client().execute_transaction(TransactStatements=statements
                                                    ))
        return dynamo_params_to_json(
            dynamo_client().execute_transaction(TransactStatements=[
                dynamo_statement_args(transaction, formatter)]
            ))
    except (ClientError, ParamValidationError) as e:
        logger.error(e, 'dynamo_transaction')
        logger.debug(f'\n\t\t{transaction}', 'dynamo_transaction')


def dynamo_statement(query, formatter=None):
    try:
        if isinstance(formatter, list):
            statements = [dynamo_statement_args(
                query, params) for params in formatter]

            if len(statements) > DYNAMO_STATEMENT_LIMIT:

                loops = len(statements) // DYNAMO_STATEMENT_LIMIT + \
                    (1 if len(statements) % DYNAMO_STATEMENT_LIMIT != 0 else 0)

                return [
                    dynamo_params_to_json(
                        dynamo_client().batch_execute_statement(
                            Statements=statements[i*DYNAMO_STATEMENT_LIMIT:
                                                  (i+1)*DYNAMO_STATEMENT_LIMIT]
                        )) for i in range(0, loops)
                ]
            return dynamo_params_to_json(
                dynamo_client().batch_execute_statement(Statements=statements)
            )
        return dynamo_params_to_json(
            dynamo_client().execute_statement(**dynamo_statement_args(query, formatter)
                                              ))
    except (ClientError, ParamValidationError) as e:
        logger.error(e, 'dynamo_statement')
        logger.debug(f'\n\t\t{query}', 'dynamo_statement')
        return e


def dynamo_drop_table(tables: Union[str, List[str]]) -> bool:
    try:
        if isinstance(tables, list):
            for tbl in tables:
                db_table = dynamo_resource().Table(tbl)
                db_table.delete()
                return True
        elif isinstance(tables, str):
            db_table = dynamo_resource().Table(tables)
            db_table.delete()
            return True
        else:
            raise ValueError('`table` must be instance of `str` or `list`!')
    except (ClientError, ParamValidationError) as e:
        logger.error(e, 'dynamo_drop_table')
        return False
