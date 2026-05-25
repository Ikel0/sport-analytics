"""S3 Uploader — Raw data lake ingestion layer."""
import gzip, io, json, logging
from datetime import date, datetime
import boto3, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from botocore.exceptions import BotoCoreError, ClientError
from ingestion.config import AWS_CONFIG, S3Paths
logger = logging.getLogger(__name__)

class S3Uploader:
    def __init__(self):
        self.client = boto3.client("s3", aws_access_key_id=AWS_CONFIG.access_key_id,
            aws_secret_access_key=AWS_CONFIG.secret_access_key, region_name=AWS_CONFIG.region)
        self.bucket = AWS_CONFIG.bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            if int(e.response["Error"]["Code"]) == 404:
                self.client.create_bucket(Bucket=self.bucket,
                    CreateBucketConfiguration={"LocationConstraint": AWS_CONFIG.region})

    def upload_json(self, data, s3_key, compress=True):
        payload = json.dumps(data, ensure_ascii=False, default=str)
        if compress:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz: gz.write(payload.encode())
            body = buf.getvalue()
            s3_key = s3_key if s3_key.endswith(".gz") else s3_key + ".gz"
            ct = "application/gzip"
        else:
            body = payload.encode(); ct = "application/json"
        self.client.put_object(Bucket=self.bucket, Key=s3_key, Body=body, ContentType=ct,
            Metadata={"uploaded-at": datetime.utcnow().isoformat()})
        uri = f"s3://{self.bucket}/{s3_key}"
        logger.info(f"Uploaded → {uri}")
        return uri

    def upload_parquet(self, df, s3_key):
        if not s3_key.endswith(".parquet"): s3_key += ".parquet"
        buf = io.BytesIO()
        pq.write_table(pa.Table.from_pandas(df, preserve_index=False), buf, compression="snappy")
        buf.seek(0)
        self.client.put_object(Bucket=self.bucket, Key=s3_key, Body=buf.getvalue())
        return f"s3://{self.bucket}/{s3_key}"

    def file_exists(self, s3_key):
        try: self.client.head_object(Bucket=self.bucket, Key=s3_key); return True
        except ClientError: return False

    def upload_nba_games(self, data, target_date):
        return self.upload_json(data, S3Paths.nba_games(target_date.strftime("%Y-%m-%d")))
    def upload_nba_player_stats(self, data, target_date):
        return self.upload_json(data, S3Paths.nba_stats(target_date.strftime("%Y-%m-%d")))
    def upload_nba_standings(self, data, target_date):
        return self.upload_json(data, S3Paths.nba_standings(target_date.strftime("%Y-%m-%d")))
    def upload_football_matches(self, data, league_id, target_date):
        return self.upload_json(data, S3Paths.football_matches(league_id, target_date.strftime("%Y-%m-%d")))
    def upload_football_standings(self, data, league_id, season):
        return self.upload_json(data, S3Paths.football_standings(league_id, season))
    def upload_football_player_stats(self, data, league_id, season):
        return self.upload_json(data, S3Paths.football_player_stats(league_id, season))
