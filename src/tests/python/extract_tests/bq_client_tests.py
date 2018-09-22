import unittest
from unittest.mock import patch, MagicMock, Mock

from google.api_core import exceptions
from google.cloud import bigquery
from google.cloud.bigquery import Client, Dataset, Table

from dp_extract.bq_client import BqClient


class TestBqClient(unittest.TestCase):
    @patch.object(bigquery, Dataset.table.__name__)
    @patch.object(bigquery, Client.dataset.__name__)
    @patch.object(bigquery, Client.__name__)
    def _get_bq_client(self, bq_client: Client, bq_dataset: Dataset, bq_table: Table):
        return BqClient('_project', '_dataset', '_table')

    def test_query_data(self):
        bq_client = self._get_bq_client()
        query_job = Mock()
        query_job.result = Mock(return_value='_job_result')
        query_job.state = '_state'
        bq_client.client.query = Mock(return_value=query_job)

        result = bq_client.query_data('_query_str', True)

        self.assertEqual(result, '_state')
        bq_client.client.query.assert_called_once()

    def test_is_table_exists(self):
        bq_client = self._get_bq_client()
        bq_client.client.get_table = Mock(return_value=True)

        result = bq_client.is_table_exists(bq_client.client, bq_client.table)

        self.assertTrue(result)

    def test_is_table_exists__not_found(self):
        bq_client = self._get_bq_client()
        bq_client.client.get_table = Mock(side_effect=exceptions.NotFound('_message'))

        result = bq_client.is_table_exists(bq_client.client, bq_client.table)

        self.assertFalse(result)

    def test_remove_table__exist(self):
        bq_client = self._get_bq_client()
        bq_client.client.delete_table = Mock()
        bq_client.is_table_exists = Mock(return_value=True)

        result = bq_client.remove_table()

        self.assertEqual(result, True)
        bq_client.client.delete_table.assert_called_once()

    def test_remove_table__not_exist(self):
        bq_client = self._get_bq_client()
        bq_client.client.delete_table = Mock()
        bq_client.is_table_exists = Mock(return_value=False)

        result = bq_client.remove_table()

        self.assertEqual(result, False)
        bq_client.client.delete_table.assert_not_called()

    def test_get_table_path(self):
        bq_client = self._get_bq_client()
        bq_client.client.project = 'project'
        bq_client.dataset.dataset_id = 'dataset_id'
        bq_client.table.table_id = 'table_id'

        result = bq_client.get_table_path()

        self.assertEqual(result, 'project:dataset_id.table_id')