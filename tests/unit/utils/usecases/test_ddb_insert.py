import pytest
from freezegun import freeze_time

from utils.usecases.ddb_insert import ddb_insert


class TestInsert:
    @pytest.mark.parametrize(
        "prepare_ddb_table, option, expected_items",
        [
            (
                [],
                {"record_id": "test_id", "text": "sinofseven"},
                [
                    {
                        "id": "test_id",
                        "zstd_binary": b"(\xb5/\xfd \nQ\x00\x00sinofseven",
                        "ttl": 1784944521,
                    }
                ],
            ),
            (
                [],
                {
                    "record_id": "test_id",
                    "text": "殺して解して並べて揃えて晒してやんよ",
                },
                [
                    {
                        "id": "test_id",
                        "zstd_binary": b"(\xb5/\xfd 6\x8d\x01\x00d\x02\xe6\xae\xba\xe3\x81\x97\xe3\x81\xa6\xe8\xa7\xa3\xe4\xb8\xa6\xe3\x81\xb9\xe3\x81\xa6\xe6\x8f\x83\xe3\x81\x88\x99\x92\xe3\x82\x84\xe3\x82\x93\xe3\x82\x88\x03\x00>\x07\x03\xa1r(t",
                        "ttl": 1784944521,
                    }
                ],
            ),
        ],
        indirect=["prepare_ddb_table"],
    )
    @freeze_time("2026-07-24T10:55:21.781094+09:00")
    def test_normal(self, resource_dynamodb, prepare_ddb_table, option, expected_items):
        ddb_insert(table_name=prepare_ddb_table, resource=resource_dynamodb, **option)

        table = resource_dynamodb.Table(prepare_ddb_table)

        resp = table.scan()
        assert resp["Items"] == expected_items
