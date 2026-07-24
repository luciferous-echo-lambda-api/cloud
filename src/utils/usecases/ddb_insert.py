from compression.zstd import compress
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from utils.logger import create_logger, logging_function

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table


logger = create_logger(__name__)


@logging_function(logger)
def ddb_insert(
    *, text: str, record_id: str, table_name: str, resource: DynamoDBServiceResource
):
    table: Table = resource.Table(table_name)
    binary = compress(text.encode(), level=10)
    # 60 (s/min) * 60 (min/h) * 24 (h/day) * 1 (day) = 86400 (s)
    ttl = int(datetime.now(timezone.utc).timestamp()) + 86400
    table.put_item(Item={"id": record_id, "zstd_binary": binary, "ttl": ttl})
