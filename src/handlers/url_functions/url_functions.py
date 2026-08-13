import json
from typing import TYPE_CHECKING
from uuid import uuid7

from aws_lambda_powertools.utilities.data_classes import LambdaFunctionUrlEvent
from pydantic_settings import BaseSettings

from utils.aws import create_resource
from utils.logger import create_logger, logging_function, logging_handler
from utils.logger.logger import custom_default
from utils.usecases import ddb_insert

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table


class EnvironmentVariables(BaseSettings):
    ddb_table_name: str


logger = create_logger(__name__)


@logging_handler(logger)
def handler(event: dict, context):
    try:
        return main(event)
    except Exception as e:
        logger.error(f"error occurred in main: [{type(e)}]", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"msg": "internal server error"}),
        }


@logging_function(logger)
def main(
    event: dict, *, resource_ddb: DynamoDBServiceResource = create_resource("dynamodb")
) -> dict:
    env = EnvironmentVariables()
    record_id = str(uuid7())
    text = json.dumps(event, indent=2, ensure_ascii=False, default=custom_default)
    ddb_insert(
        text=text,
        record_id=record_id,
        table_name=env.ddb_table_name,
        resource=resource_ddb,
    )
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "X-Record-ID": record_id,
        },
        "body": json.dumps(
            {"id": record_id, "event": event},
            ensure_ascii=False,
            default=custom_default,
        ),
    }


@logging_function(logger)
def parse_host(*, raw_event: dict) -> str | None:
    event = LambdaFunctionUrlEvent(raw_event)
