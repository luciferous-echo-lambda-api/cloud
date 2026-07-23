import pytest

import handlers.url_functions.url_functions as index


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
                        "binary-request": b"(\xb5/\xfd \nQ\x00\x00sinofseven",
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
                        "binary-request": b"(\xb5/\xfd 6\x8d\x01\x00d\x02\xe6\xae\xba\xe3\x81\x97\xe3\x81\xa6\xe8\xa7\xa3\xe4\xb8\xa6\xe3\x81\xb9\xe3\x81\xa6\xe6\x8f\x83\xe3\x81\x88\x99\x92\xe3\x82\x84\xe3\x82\x93\xe3\x82\x88\x03\x00>\x07\x03\xa1r(t",
                    }
                ],
            ),
        ],
        indirect=["prepare_ddb_table"],
    )
    def test_normal(self, resource_dynamodb, prepare_ddb_table, option, expected_items):
        index.insert(table_name=prepare_ddb_table, resource=resource_dynamodb, **option)

        table = resource_dynamodb.Table(prepare_ddb_table)

        resp = table.scan()
        assert resp["Items"] == expected_items
