"""Utilities to generate V4 signed URLs for GCS objects."""

from __future__ import annotations

from typing import Optional, Tuple
from datetime import timedelta

import json
from google.cloud import storage
from google.oauth2 import service_account

from config.settings import GCP_SA_KEY_JSON


def parse_gs_uri(gs_uri: str) -> Tuple[str, str]:
    """Parse a gs://bucket/object path into (bucket, object_name).

    Raises:
        ValueError: If the URI is not a valid gs:// path.
    """
    if not isinstance(gs_uri, str) or not gs_uri.startswith("gs://"):
        raise ValueError("URI must start with gs://")
    # Strip gs:// and split into bucket and the rest
    without_scheme = gs_uri[len("gs://"):]
    parts = without_scheme.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid GCS URI; expected gs://bucket/object")
    return parts[0], parts[1]


def generate_v4_signed_url(gs_uri: str, expires_minutes: int = 10) -> str:
    """Generate a V4 signed URL for a GCS object referenced by a gs:// URI.

    Args:
        gs_uri: e.g., gs://my-bucket/path/to/file.pdf
        expires_minutes: Expiration window in minutes (default 10)

    Returns:
        A time-limited HTTPS URL to download/view the object.
    """
    bucket_name, object_name = parse_gs_uri(gs_uri)

    # Build credentials from configured service account JSON
    sa_info = GCP_SA_KEY_JSON if isinstance(GCP_SA_KEY_JSON, dict) else json.loads(GCP_SA_KEY_JSON)
    creds = service_account.Credentials.from_service_account_info(sa_info)
    client = storage.Client(credentials=creds, project=creds.project_id)

    blob = client.bucket(bucket_name).blob(object_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expires_minutes),
        method="GET",
    )
    return url
