import io
import json
import os

from minio import Minio


class MinIOStorage:
    """
    MinIO object storage client.
    """

    def __init__(
        self,
        endpoint=None,
        access_key=None,
        secret_key=None,
        bucket_name=None,
    ):
        self.endpoint = (
            endpoint
            or os.getenv(
                "MINIO_ENDPOINT",
                "minio:9000",
            )
        )

        self.access_key = (
            access_key
            or os.getenv(
                "MINIO_ACCESS_KEY",
                "minioadmin",
            )
        )

        self.secret_key = (
            secret_key
            or os.getenv(
                "MINIO_SECRET_KEY",
                "minioadmin",
            )
        )

        self.bucket_name = (
            bucket_name
            or os.getenv(
                "MINIO_BUCKET",
                "stock-raw-data",
            )
        )

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

    def ensure_bucket(self):
        """
        Create the bucket if it does not exist.
        """

        if not self.client.bucket_exists(
            self.bucket_name
        ):
            self.client.make_bucket(
                self.bucket_name
            )

    def upload_json(
        self,
        data,
        object_name,
    ):
        """
        Upload a Python object as JSON.
        """

        payload = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str,
        ).encode("utf-8")

        self.ensure_bucket()

        self.client.put_object(
            self.bucket_name,
            object_name,
            io.BytesIO(payload),
            length=len(payload),
            content_type="application/json",
        )