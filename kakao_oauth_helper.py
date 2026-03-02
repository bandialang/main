from __future__ import annotations

import os
import urllib.parse

import requests
from dotenv import load_dotenv


AUTH_BASE = "https://kauth.kakao.com/oauth/authorize"
TOKEN_API = "https://kauth.kakao.com/oauth/token"


def print_auth_url() -> None:
    rest_api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI", "").strip()
    if not rest_api_key or not redirect_uri:
        raise RuntimeError("KAKAO_REST_API_KEY and KAKAO_REDIRECT_URI are required.")
    query = urllib.parse.urlencode(
        {
            "client_id": rest_api_key,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "talk_message",
        }
    )
    print(f"{AUTH_BASE}?{query}")


def exchange_code_for_tokens(code: str) -> None:
    rest_api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    client_secret = os.getenv("KAKAO_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI", "").strip()
    data = {
        "grant_type": "authorization_code",
        "client_id": rest_api_key,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    if client_secret:
        data["client_secret"] = client_secret
    resp = requests.post(TOKEN_API, data=data, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    print("access_token:", payload.get("access_token", ""))
    print("refresh_token:", payload.get("refresh_token", ""))
    print("expires_in:", payload.get("expires_in", ""))


def main() -> None:
    load_dotenv()
    print("1) Open this URL in browser and authorize:")
    print_auth_url()
    print("\n2) Paste the `code` from redirected URL query string.")
    code = input("code: ").strip()
    exchange_code_for_tokens(code)


if __name__ == "__main__":
    main()
