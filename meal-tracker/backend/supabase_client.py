"""
Supabase client helper for the Flask backend.

Reads `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`/`SUPABASE_KEY` from the environment
(use a `.env` file during local development) and exposes a configured `supabase`
client that can be imported anywhere in the backend.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Final, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables from .env if present (safe for local dev)
load_dotenv()

_URL_ENV_VAR: Final[str] = "SUPABASE_URL"
_SERVICE_ROLE_ENV_VAR: Final[str] = "SUPABASE_SERVICE_ROLE_KEY"
_FALLBACK_KEY_ENV_VAR: Final[str] = "SUPABASE_KEY"
_logger = logging.getLogger(__name__)


def _decode_jwt_role(token: str) -> Optional[str]:
    """Best-effort decode of Supabase key role claim (service_role vs anon)."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        data = base64.urlsafe_b64decode(payload.encode("ascii"))
        body = json.loads(data.decode("utf-8"))
        return body.get("role")
    except Exception:
        return None


def _log_key_role(key: str) -> None:
    role = _decode_jwt_role(key)
    if role == "anon":
        _logger.warning(
            "Supabase key looks like an anon key. Backend operations may fail; "
            "prefer the service role key on the server."
        )
    elif role == "service_role":
        _logger.info("Supabase service_role key detected (server-side privileges).")
    else:
        _logger.debug("Supabase key role could not be determined.")


def _init_client() -> Client:
    url = os.getenv(_URL_ENV_VAR)
    key = os.getenv(_SERVICE_ROLE_ENV_VAR) or os.getenv(_FALLBACK_KEY_ENV_VAR)
    if not url:
        raise RuntimeError(
            f"{_URL_ENV_VAR} is not set. Add it to your environment or .env file."
        )
    if not key:
        raise RuntimeError(
            f"{_SERVICE_ROLE_ENV_VAR} (preferred) or {_FALLBACK_KEY_ENV_VAR} must be set."
        )
    _log_key_role(key)
    return create_client(url, key)


# Instantiate a supabase client ready for import elsewhere
supabase: Client = _init_client()
