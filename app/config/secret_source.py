"""Secret source utilities to normalize credentials from env or Streamlit secrets.

This layer reconstructs a canonical GCP service account JSON string from either:
 - .env: GCP_SA_KEY as a JSON string
 - Streamlit secrets TOML: a [gcp_service_account] table or equivalent dict/top-level keys

Precedence:
 - Default: prefer .env over secrets
 - If APP_ENV is 'prod' or 'production', prefer secrets over .env
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def _get_secrets():
    try:
        import streamlit as st  # type: ignore
        return st.secrets
    except Exception:
        return None


def _from_secrets(key: str, default=None):
    secrets = _get_secrets()
    if not secrets:
        return default
    if key in secrets:
        return secrets.get(key, default)
    if "default" in secrets and key in secrets["default"]:
        return secrets["default"].get(key, default)
    return default


def _collect_sa_from_top_level() -> Optional[Dict[str, Any]]:
    """Collect SA fields if user placed them as top-level/default keys in secrets."""
    keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
        "universe_domain",
    ]
    values = {}
    for k in keys:
        v = _from_secrets(k)
        if v is not None:
            values[k] = v
    return values or None


def _get_sa_dict_from_secrets() -> Optional[Dict[str, Any]]:
    """Get service account as a dict from Streamlit secrets in various shapes."""
    secrets = _get_secrets()
    if not secrets:
        return None

    # 1) Preferred: [gcp_service_account] table
    if "gcp_service_account" in secrets:
        sa = secrets["gcp_service_account"]
        if isinstance(sa, dict):
            return dict(sa)

    # 2) A dict or string under GCP_SA_KEY
    gcp_sa_key = _from_secrets("GCP_SA_KEY")
    if isinstance(gcp_sa_key, dict):
        return dict(gcp_sa_key)
    if isinstance(gcp_sa_key, str):
        try:
            return json.loads(gcp_sa_key)
        except Exception:
            pass

    # 3) Top-level/default decomposed fields
    top = _collect_sa_from_top_level()
    if top:
        return top

    return None


def _get_app_env() -> str:
    env = os.getenv("APP_ENV") or _from_secrets("APP_ENV", "dev")
    if isinstance(env, str):
        return env.lower()
    return "dev"


def get_gcp_sa_json(app_env: Optional[str] = None) -> Optional[str]:
    """Return a JSON string for the GCP service account, honoring precedence.

    Precedence rules:
    - If app_env is 'prod' or 'production': prefer secrets, else env
    - Otherwise (dev/default): prefer env, else secrets
    """
    env_json = os.getenv("GCP_SA_KEY")

    secrets_dict = _get_sa_dict_from_secrets()
    secrets_json = json.dumps(secrets_dict) if secrets_dict else None

    effective_env = (app_env or _get_app_env()).lower()
    prefer_secrets = effective_env in {"prod", "production"}

    if prefer_secrets:
        return secrets_json or env_json
    else:
        return env_json or secrets_json


def get_project_id_fallback(app_env: Optional[str] = None) -> Optional[str]:
    """Return project_id from secrets if needed as a fallback."""
    sa = _get_sa_dict_from_secrets()
    if sa and isinstance(sa, dict):
        proj = sa.get("project_id")
        if isinstance(proj, str) and proj:
            return proj
    return None
