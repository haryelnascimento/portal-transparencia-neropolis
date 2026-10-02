import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = "portal-transparencia-neropolis/0.2 (+https://github.com/haryelnascimento/portal-transparencia-neropolis)"
RETRYABLE = {429, 500, 502, 503, 504}


def build_url(base: str, params: dict | None = None) -> str:
    return f"{base}?{urlencode(params, safe='.*,()')}" if params else base


def get_json(base: str, params: dict | None = None, headers: dict | None = None, retries: int = 4, timeout: int = 90):
    """GET com retentativas exponenciais para limites de taxa e falhas temporárias."""
    url = build_url(base, params)
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT, **(headers or {})})
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310 - origens públicas fixas
                return json.load(response)
        except HTTPError as error:
            if error.code not in RETRYABLE or attempt == retries:
                raise
        except URLError:
            if attempt == retries:
                raise
        time.sleep(2 ** attempt * 3)
    raise RuntimeError("inalcançável")
