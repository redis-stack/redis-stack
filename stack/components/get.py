import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

def get_stream_and_store(url: str, destfile: str):
    """Fetch a URL from a known location, and right to file,
    relying on retries.
    """
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=4, backoff_factor=1))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    r = requests.get(url, stream=True)
    if r.status_code > 204:
        logger.error(f"{url} could not be retrieved")
        raise requests.HTTPError
    open(destfile, "wb").write(r.content)
