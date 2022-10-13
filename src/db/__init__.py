from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List

import aioboto3
from boto3.dynamodb.conditions import Key

from context import APP_ENVIRONMENT, Environment


ENDPOINT_URL: str = (
    "http://localhost:8022"
    if APP_ENVIRONMENT == Environment.DEV
    else "https://dynamodb.us-east-1.amazonaws.com"
)
SESSION = aioboto3.Session()
TABLE_NAME: str = "vuln-management"


async def put_item(hash_key: str, range_key: str, **kwargs: Any) -> None:
    async with SESSION.resource(
        "dynamodb", endpoint_url=ENDPOINT_URL
    ) as dynamo_resource:
        table = await dynamo_resource.Table(TABLE_NAME)
        attrs: Any = {}
        for _key, _value in kwargs.items():
            if _value is None:
                continue
            if isinstance(_value, float):
                attrs.update({_key: Decimal(str(_value))})
            elif isinstance(_value, Enum):
                attrs.update({_key: _value.value})
            else:
                attrs.update({_key: _value})
        await table.put_item(
            Item={"hk": hash_key, "rk": range_key, **attrs}
        )


async def query(hash_key: str, range_key: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    async with SESSION.resource(
        "dynamodb", endpoint_url=ENDPOINT_URL
    ) as dynamo_resource:
        table = await dynamo_resource.Table(TABLE_NAME)
        response = await table.query(
            KeyConditionExpression=(
                Key("hk").eq(hash_key) & Key("rk").begins_with(range_key)
            )
        )
        results = response["Items"]

    return results
