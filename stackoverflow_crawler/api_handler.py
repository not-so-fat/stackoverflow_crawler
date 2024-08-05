import logging
import requests
from typing import Callable


logger = logging.getLogger(__name__)


def api_error(api_call_func: Callable) -> Callable:
    """
    function decorator to raise Exception when API return isn't ok
    """
    def decorated_func(*args, **kwargs) -> requests.Response:
        try:
            res = api_call_func(*args, **kwargs)
            if not res.ok:
                raise APIError(res)
        except Exception as e:
            logger.error(e)
            raise e
        logger.info(f'Quota for API: {res.json()["quota_remaining"]} / {res.json()["quota_max"]}')
        return res

    return decorated_func


class StackExchangeAPIHandler:
    def __init__(self):
        self.base_url = f"https://api.stackexchange.com/2.3/"
        self.session = requests.Session()

    @api_error
    def search(self, params):
        url = f"{self.base_url}search?{get_params_string(params)}"
        return self.session.get(url)

    @api_error
    def answers(self, qid, params):
        url = f"{self.base_url}questions/{qid}/answers?{get_params_string(params)}"
        return self.session.get(url)


def get_params_string(params):
    return "&".join([f"{k}={v}" for k, v in params.items()])


class APIError(Exception):
    def __init__(self, res):
        super().__init__(f"StackExchange API execution failed: {res} @ {res.url}\n{res.text}")
