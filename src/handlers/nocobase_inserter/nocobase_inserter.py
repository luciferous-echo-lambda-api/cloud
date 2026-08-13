import json
from compression.zstd import decompress
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from aws_lambda_powertools.utilities.data_classes import (
    DynamoDBStreamEvent,
    event_source,
)
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecordEventName,
)
from pydantic_settings import BaseSettings

from utils.aws import create_client, create_resource
from utils.logger import create_logger, logging_function, logging_handler

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
    from mypy_boto3_ssm import SSMClient


class EnvironmentVariables(BaseSettings):
    ssm_parameter_name_nocobase_domain: str
    ssm_parameter_name_nocobase_collection: str
    ssm_parameter_name_nocobase_api_key: str
    ssm_parameter_name_cf_access_client_id: str
    ssm_parameter_name_cf_access_client_secret: str
    ddb_table_name: str


@dataclass(frozen=True)
class EventItem:
    event_name: str
    id: str


@dataclass(frozen=True)
class Secrets:
    nocobase_domain: str
    nocobase_collection: str
    nocobase_api_key: str
    cf_access_client_id: str
    cf_access_client_secret: str


logger = create_logger(__name__)


@event_source(data_class=DynamoDBStreamEvent)
@logging_handler(logger)
def handler(event, context):
    main(event=event)


@logging_function(logger)
def main(
    *,
    event: DynamoDBStreamEvent,
    resource_ddb: DynamoDBServiceResource = create_resource("dynamodb"),
    client_ssm: SSMClient = create_client("ssm"),
):
    event_item: EventItem = parse_event(event=event)
    if event_item.event_name != DynamoDBRecordEventName.INSERT:
        return

    env = EnvironmentVariables()

    request_event: str = get_request_event(
        item_id=event_item.id, table_name=env.ddb_table_name, resource=resource_ddb
    )

    create_nocobase_record(
        record_id=event_item.id, request_event=request_event, env=env, client=client_ssm
    )


@logging_function(logger, with_args=False)
def parse_event(*, event: DynamoDBStreamEvent) -> EventItem:
    record = next(event.records)

    return EventItem(
        # pyrefly: ignore [bad-argument-type]
        event_name=record.event_name,  # ty:ignore[invalid-argument-type]
        # pyrefly: ignore [missing-attribute]
        id=record.dynamodb.keys["id"],  # ty:ignore[unresolved-attribute]
    )


@logging_function(logger)
def get_request_event(
    *, item_id: str, table_name: str, resource: DynamoDBServiceResource
) -> str:
    table: Table = resource.Table(table_name)

    resp = table.get_item(Key={"id": item_id})

    # pyrefly: ignore [bad-assignment]
    raw: bytes = resp["Item"]["zstd_binary"]  # ty:ignore[invalid-assignment]
    return decompress(raw).decode()


@logging_function(logger)
def create_nocobase_record(
    *, record_id: str, request_event: str, env: EnvironmentVariables, client: SSMClient
):
    def get_parameters() -> Secrets:
        resp = client.get_parameters(
            Names=[
                env.ssm_parameter_name_cf_access_client_id,
                env.ssm_parameter_name_cf_access_client_secret,
                env.ssm_parameter_name_nocobase_api_key,
                env.ssm_parameter_name_nocobase_collection,
                env.ssm_parameter_name_nocobase_domain,
            ],
            WithDecryption=True,
        )

        mapping = {x["Name"]: x["Value"] for x in resp["Parameters"]}

        return Secrets(
            nocobase_domain=mapping[env.ssm_parameter_name_nocobase_domain],
            nocobase_collection=mapping[env.ssm_parameter_name_nocobase_collection],
            nocobase_api_key=mapping[env.ssm_parameter_name_nocobase_api_key],
            cf_access_client_id=mapping[env.ssm_parameter_name_cf_access_client_id],
            cf_access_client_secret=mapping[
                env.ssm_parameter_name_cf_access_client_secret
            ],
        )

    def process_create_nocobase_record():
        secrets = get_parameters()

        req = Request(
            url="https://{domain}/api/{collection_name}:create".format(
                domain=secrets.nocobase_domain,
                collection_name=secrets.nocobase_collection,
            ),
            method="POST",
            headers={
                "User-Agent": "sinofseven",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {secrets.nocobase_api_key}",
                "Cf-Access-Client-Id": secrets.cf_access_client_id,
                "Cf-Access-Client-Secret": secrets.cf_access_client_secret,
            },
            data=json.dumps(
                {
                    "record_id": record_id,
                    "type": "lambda_url_functions",
                    "event": request_event,
                },
                ensure_ascii=False,
            ).encode(),
        )

        try:
            with urlopen(req):
                pass
        except HTTPError as e:
            body = e.read()
            logger.warning(
                f"error occurred in process_create_nocobase_record(): [{type(e)}] {e}",
                data={"body": body, "headers": e.headers},
            )
            raise

    process_create_nocobase_record()
