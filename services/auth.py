"""
Supabase authentication helpers for Streamlit.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import streamlit as st

from config.settings import SUPABASE_ANON_KEY, SUPABASE_REDIRECT_URL, SUPABASE_URL

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - handled at runtime
    Client = Any  # type: ignore
    create_client = None


AUTH_USER_KEY = "auth_user"
AUTH_ERROR_KEY = "auth_error"


def _response_get(payload: Any, key: str) -> Any:
    if payload is None:
        return None
    if isinstance(payload, dict):
        return payload.get(key)
    return getattr(payload, key, None)


def is_supabase_ready() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY and create_client)


@st.cache_resource(show_spinner=False)
def _build_supabase_client() -> Optional[Client]:
    if not is_supabase_ready():
        return None
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_supabase_client() -> Optional[Client]:
    return _build_supabase_client()


def build_google_oauth_url() -> Tuple[Optional[str], Optional[str]]:
    client = get_supabase_client()
    if client is None:
        return None, "Supabase no esta configurado en variables de entorno."

    try:
        result = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": SUPABASE_REDIRECT_URL,
                    "query_params": {
                        "access_type": "offline",
                        "prompt": "consent",
                    },
                },
            }
        )
    except Exception as exc:  # pragma: no cover - external API
        return None, f"No se pudo iniciar OAuth con Google: {exc}"

    url = _response_get(result, "url")
    if not url:
        data = _response_get(result, "data")
        url = _response_get(data, "url")

    if not url:
        return None, "Supabase no devolvio URL de autenticacion."

    return str(url), None


def _normalize_user(user_payload: Any) -> Dict[str, Any]:
    if user_payload is None:
        return {}

    if not isinstance(user_payload, dict):
        user_payload = user_payload.__dict__

    metadata = user_payload.get("user_metadata") or {}
    app_metadata = user_payload.get("app_metadata") or {}

    return {
        "id": user_payload.get("id"),
        "email": user_payload.get("email") or metadata.get("email"),
        "name": metadata.get("full_name") or metadata.get("name") or metadata.get("preferred_username"),
        "avatar_url": metadata.get("avatar_url") or metadata.get("picture"),
        "provider": app_metadata.get("provider") or "google",
    }


def handle_oauth_callback() -> None:
    client = get_supabase_client()
    if client is None:
        return

    code = st.query_params.get("code")
    if not code:
        return

    try:
        response = client.auth.exchange_code_for_session({"auth_code": str(code)})
        user_payload = _response_get(response, "user")

        if user_payload is None:
            session_payload = _response_get(response, "session")
            user_payload = _response_get(session_payload, "user")

        normalized_user = _normalize_user(user_payload)
        if not normalized_user.get("id"):
            st.session_state[AUTH_ERROR_KEY] = "No se pudo recuperar el perfil del usuario despues del login."
        else:
            st.session_state[AUTH_USER_KEY] = normalized_user
            st.session_state.pop(AUTH_ERROR_KEY, None)

    except Exception as exc:  # pragma: no cover - external API
        st.session_state[AUTH_ERROR_KEY] = f"Error en callback OAuth: {exc}"

    st.query_params.clear()
    st.rerun()


def get_auth_user() -> Optional[Dict[str, Any]]:
    user = st.session_state.get(AUTH_USER_KEY)
    if isinstance(user, dict) and user.get("id"):
        return user
    client = get_supabase_client()
    if client is not None:
        try:
            response = client.auth.get_user()
            normalized = _normalize_user(_response_get(response, "user"))
            if normalized.get("id"):
                st.session_state[AUTH_USER_KEY] = normalized
                return normalized
        except Exception:
            return None
    return None


def logout_user() -> None:
    client = get_supabase_client()
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    st.session_state.pop(AUTH_USER_KEY, None)
    st.session_state.pop(AUTH_ERROR_KEY, None)


def get_auth_error() -> Optional[str]:
    err = st.session_state.get(AUTH_ERROR_KEY)
    return str(err) if err else None
