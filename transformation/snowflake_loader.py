"""Snowflake Loader — loads cleaned DataFrames into Snowflake."""
import logging
from typing import Literal
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from ingestion.config import SNOWFLAKE_CONFIG

logger = logging.getLogger(__name__)
Schema = Literal["raw", "staging", "analytics"]


class SnowflakeLoader:
    def __init__(self):
        self.conn = self._connect()

    def _connect(self):
        logger.info(f"Connecting to Snowflake: {SNOWFLAKE_CONFIG.account}")
        return snowflake.connector.connect(
            account=SNOWFLAKE_CONFIG.account, user=SNOWFLAKE_CONFIG.user,
            password=SNOWFLAKE_CONFIG.password, database=SNOWFLAKE_CONFIG.database,
            warehouse=SNOWFLAKE_CONFIG.warehouse, role=SNOWFLAKE_CONFIG.role,
            session_parameters={"QUERY_TAG": "sport-analytics-pipeline"},
        )

    def _get_schema(self, schema: Schema) -> str:
        return SNOWFLAKE_CONFIG.schemas.get(schema, schema.upper())

    def execute_sql(self, sql: str, params: dict = None) -> list:
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            try: return cur.fetchall()
            except: return []

    def execute_file(self, filepath: str) -> None:
        with open(filepath) as f:
            statements = [s.strip() for s in f.read().split(";") if s.strip()]
        with self.conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        logger.info(f"Executed {len(statements)} statements from {filepath}")

    def load_dataframe(self, df: pd.DataFrame, table: str,
                       schema: Schema = "raw", overwrite: bool = False,
                       chunk_size: int = 50_000) -> int:
        if df.empty:
            logger.warning(f"Empty DataFrame — skipping {schema}.{table}")
            return 0
        schema_name = self._get_schema(schema)
        df = df.copy()
        df.columns = [c.upper() for c in df.columns]
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).replace({"NaT": None, "nan": None})
        if overwrite:
            self.execute_sql(f"TRUNCATE TABLE IF EXISTS {schema_name}.{table}")
        success, _, num_rows, _ = write_pandas(
            conn=self.conn, df=df, table_name=table, schema=schema_name,
            database=SNOWFLAKE_CONFIG.database, chunk_size=chunk_size,
            auto_create_table=True, overwrite=False, quote_identifiers=False,
        )
        if not success:
            raise RuntimeError(f"Failed to load to {schema_name}.{table}")
        logger.info(f"Loaded {num_rows:,} rows → {schema_name}.{table}")
        return num_rows

    def run_transformation(self, sql_file: str) -> None:
        logger.info(f"Running: {sql_file}")
        self.execute_file(sql_file)

    def close(self):
        if self.conn: self.conn.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
