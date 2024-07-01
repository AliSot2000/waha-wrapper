from aiohttp import ClientResponse, ContentTypeError
import logging
import json


"""
Exceptions for the waha_python_wrapper package.
"""


logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """
    Base exception for the waha_python_wrapper package.
    """
    url: str
    code: int
    expected_code: int
    resp: ClientResponse

    def __init__(self, *args, url: str, code: int, expected_code: int, resp: ClientResponse):
        """
        Initialize the BaseAPIException

        :param args: Args to be passed to the super class
        :param url: Url of the API request
        :param code: status code of the API request
        :param expected_code: expected status code of the API request according to docs
        :param resp: response of the API request
        """
        super().__init__(*args)
        self.url = url
        self.code = code
        self.expected_code = expected_code
        self.resp = resp

    def __str__(self):
        return f"API request to {self.url} failed with status code {self.code}"


class APIError(BaseAPIException):
    """
    API Error that contained Json response.
    """
    error_resp: dict

    def __init__(self, *args, url: str, code: int, expected_code: int, resp: ClientResponse, error_resp: dict):
        super().__init__(*args, url=url, code=code, expected_code=expected_code, resp=resp)
        self.error_resp = error_resp

    def __str__(self):
        return f"API request to {self.url} failed with status code {self.code} and error description {self.error_resp}"


async def handle_error(resp: ClientResponse, expected_code: int = 200):
    """
    Handle API Errors, try to get as much information as possible, return and log it.

    :param expected_code: Expected Return code of the API
    :param resp: The response from the API

    :return: BaseAPIException if no JSON response was found, APIError if JSON response was found
    """
    content = None

    try:
        content = await resp.json()
    except ContentTypeError:
        logger.debug("No JSON response from API")
    except json.JSONDecodeError:
        logging.warning(f"API response contained invalid json, url: {resp.url}, status: {resp.status}")
        pass
    except Exception as e:
        logging.exception("Unknown error while handling API error", exc_info=e)

    if content is None:
        raise BaseAPIException(url=str(resp.url),
                               code=resp.status,
                               expected_code=expected_code,
                               resp=resp)
    else:
        raise APIError(url=str(resp.url),
                       code=resp.status,
                       expected_code=expected_code,
                       resp=resp,
                       error_resp=content)
