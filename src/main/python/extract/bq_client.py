from google.api_core import exceptions
from google.cloud import bigquery


class BqClient:
    def __init__(self, project, temp_dataset, temp_table):
        self.client = bigquery.Client(project)
        self.dataset = self.client.dataset(temp_dataset)
        self.table = self.dataset.table(temp_table)

    def query_data(self, query, is_legacy_sql):
        job_config = bigquery.QueryJobConfig()
        job_config.destination = self.table
        job_config.allow_large_results = True
        job_config.use_legacy_sql = is_legacy_sql
        job_config.write_disposition = 'WRITE_TRUNCATE'

        query_job = self.client.query(query, job_config=job_config)
        query_job.result()
        return query_job.state

    @staticmethod
    def is_table_exists(client: bigquery.Client, table: str) -> bool:
        try:
            client.get_table(table)
            return True
        except exceptions.NotFound:
            return False

    def remove_table(self) -> bool:
        table = self.table
        table_exist = self.is_table_exists(self.client, table)
        if table_exist:
            self.client.delete_table(table)
        return table_exist

    def get_table_path(self) -> str:
        return '{}:{}.{}'.format(self.client.project, self.dataset.dataset_id, self.table.table_id)
