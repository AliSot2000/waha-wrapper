from pydantic import BaseModel
from typing import Callable, List, Dict
from waha_python_wrapper.errors import handle_error
import aiohttp
from waha_python_wrapper.config import WAHAConfig
from enum import Enum
import re


class Methods(str, Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"


async def handle_response(response_model: BaseModel, resp: aiohttp.ClientResponse, expected_code: int = 200):
    """
    Check the status code, generate error if one occurred, otherwise parse data and return it.

    :raise BaseAPIException: If the request failed without a JSON response
    :raise APIError: If the request failed with a JSON response
    :raise ValidationError: If the response could not be validated with the response_model
    """
    if not resp.status != expected_code:
        raise handle_error(resp=resp, expected_code=expected_code)

    # Validate against response_model
    resp_data = response_model.model_validate(await resp.json())
    return resp_data


def populate_path_params(path: str, lookup: Dict[str, str]):
    """
    Populate path params in a path string with the given values

    :param lookup: parameters including
    :param path: original path string

    :return: path string with populated path params
    """
    for key, value in lookup.items():
        filled_key = "{" + key + "}"
        path = path.replace(f'{filled_key}', value)

    return path


def plain_path_wrapper(path: str,
                       params_model: BaseModel,
                       response_model: BaseModel,
                       expected_code: int,
                       method: Methods | str = Methods.GET,
                       docstring: str = None,
                       request_model: BaseModel = None,
                       body_defaults: dict = None,
                       param_defaults: dict = None) -> Callable:
    """
    Wrapper for a plain path api endpoint that generates an async callable to make the request.

    Generated function may raise the following errors:
    - BaseAPIException: If the request failed without a JSON response
    - APIError: If the request failed with a JSON response
    - ValidationError: If the response could not be validated with the response_model

    Supported Methods are:
    - GET
    - POST
    - PUT
    - DELETE
    - PATCH

    :param path: API endpoint path
    :param params_model: model to be used for the requests parameters
    :param request_model: request model to be used
    :param response_model: response model to be used
    :param expected_code: expected status code from operation
    :param method: HTTP Method to be used
    :param docstring: docstring for the generated function
    :param param_defaults: arguments passed to the param_model.model_validate method when the params are None.
    :param body_defaults: default values for the body model

    :return: function to call the api endpoint
    """
    if param_defaults is None:
        param_defaults = {}

    if body_defaults is None:
        body_defaults = {}

    if not isinstance(method, Methods):

        # Try to parse the method, assuming string.
        try:
            parsed_method = Methods(str(method).upper())
        except ValueError:
            raise ValueError(f"Method {method} not supported, allowed are {list(Methods.__members__.keys())}")
        except Exception as e:
            raise e

    # Method of correct type, can be used directly
    else:
        parsed_method = method

    # Generate a GET function
    if parsed_method == method.GET:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            target_url = f'{cfg.waha_url}{path}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.get(target_url,
                                           params=params.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.get(target_url,
                                       params=params.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a POST function
    elif parsed_method == method.POST:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{path}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.post(target_url,
                                            params=params.model_dump(by_alias=True),
                                            json=body.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.post(target_url,
                                        params=params.model_dump(by_alias=True),
                                        json=body.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a PUT function
    elif parsed_method == method.PUT:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{path}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.put(target_url,
                                           params=params.model_dump(by_alias=True),
                                           json=body.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.put(target_url,
                                       params=params.model_dump(by_alias=True),
                                       json=body.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a DELETE function
    elif parsed_method == method.DELETE:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            target_url = f'{cfg.waha_url}{path}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.delete(target_url,
                                              params=params.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.delete(target_url,
                                          params=params.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a PATCH function
    elif parsed_method == method.PATCH:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{path}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.patch(target_url,
                                             params=params.model_dump(by_alias=True),
                                             json=body.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.patch(target_url,
                                         params=params.model_dump(by_alias=True),
                                         json=body.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)
    else:
        raise ValueError(f"Method {method} not supported, allowed are ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']")

    if docstring is not None:
        api_call.__doc__ = docstring

    return api_call


def path_param_wrapper(path: str,
                       params_model: BaseModel,
                       response_model: BaseModel,
                       expected_code: int,
                       method: Methods | str = Methods.GET,
                       docstring: str = None,
                       request_model: BaseModel = None,
                       body_defaults: dict = None,
                       param_defaults: dict = None):
    """
    Wrapper for a plain path api endpoint that generates an async callable to make the request.

    Generated function may raise the following errors:
    - BaseAPIException: If the request failed without a JSON response
    - APIError: If the request failed with a JSON response
    - ValidationError: If the response could not be validated with the response_model

    Supported Methods are:
    - GET
    - POST
    - PUT
    - DELETE
    - PATCH

    :param path: API endpoint path
    :param params_model: model to be used for the requests parameters
    :param request_model: request model to be used
    :param response_model: response model to be used
    :param expected_code: expected status code from operation
    :param method: HTTP Method to be used
    :param docstring: docstring for the generated function
    :param param_defaults: arguments passed to the param_model.model_validate method when the params are None.
    :param body_defaults: default values for the body model

    :return: function to call the api endpoint
    """
    # Extract path params
    pattern = re.compile(r'/{[a-zA-Z]*}/?')
    path_params = pattern.findall(path)
    cleaned_args = []
    for param in path_params:
        cleaned_args.append(param.replace("/", "").replace("{", "").replace("}", ""))

    if param_defaults is None:
        param_defaults = {}

    if body_defaults is None:
        body_defaults = {}

    if not isinstance(method, Methods):

        # Try to parse the method, assuming string.
        try:
            parsed_method = Methods(str(method).upper())
        except ValueError:
            raise ValueError(f"Method {method} not supported, allowed are {list(Methods.__members__.keys())}")
        except Exception as e:
            raise e

    # Method of correct type, can be used directly
    else:
        parsed_method = method

    # Generate a GET function
    if parsed_method == method.GET:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           session: aiohttp.ClientSession = None,
                           **kwargs) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Check Path Params
            if set(kwargs.keys()) != set(cleaned_args):
                raise ValueError(f"Expected path params {cleaned_args}, got {set(kwargs.keys())}")

            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.get(target_url,
                                           params=params.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.get(target_url,
                                       params=params.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a POST function
    elif parsed_method == method.POST:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None,
                           **kwargs) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Check Path Params
            if set(kwargs.keys()) != set(cleaned_args):
                raise ValueError(f"Expected path params {cleaned_args}, got {set(kwargs.keys())}")

            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.post(target_url,
                                            params=params.model_dump(by_alias=True),
                                            json=body.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.post(target_url,
                                        params=params.model_dump(by_alias=True),
                                        json=body.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a PUT function
    elif parsed_method == method.PUT:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None,
                           **kwargs) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Check Path Params
            if set(kwargs.keys()) != set(cleaned_args):
                raise ValueError(f"Expected path params {cleaned_args}, got {set(kwargs.keys())}")

            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.put(target_url,
                                           params=params.model_dump(by_alias=True),
                                           json=body.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.put(target_url,
                                       params=params.model_dump(by_alias=True),
                                       json=body.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a DELETE function
    elif parsed_method == method.DELETE:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           session: aiohttp.ClientSession = None,
                           **kwargs) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Check Path Params
            if set(kwargs.keys()) != set(cleaned_args):
                raise ValueError(f"Expected path params {cleaned_args}, got {set(kwargs.keys())}")

            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.delete(target_url,
                                              params=params.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.delete(target_url,
                                          params=params.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)

    # Generate a PATCH function
    elif parsed_method == method.PATCH:
        async def api_call(cfg: WAHAConfig,
                           params: params_model = None,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None,
                           **kwargs) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Check Path Params
            if set(kwargs.keys()) != set(cleaned_args):
                raise ValueError(f"Expected path params {cleaned_args}, got {set(kwargs.keys())}")

            # Create default params
            if params is None:
                params = params_model.model_validate(param_defaults)

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            # Make the Request
            if session is None:
                async with aiohttp.ClientSession() as session:

                    async with session.patch(target_url,
                                             params=params.model_dump(by_alias=True),
                                             json=body.model_dump(by_alias=True)) as resp:
                        return handle_response(response_model=response_model,
                                               resp=resp,
                                               expected_code=expected_code)
            else:
                async with session.patch(target_url,
                                         params=params.model_dump(by_alias=True),
                                         json=body.model_dump(by_alias=True)) as resp:

                    return handle_response(response_model=response_model,
                                           resp=resp,
                                           expected_code=expected_code)
    else:
        raise ValueError(f"Method {method} not supported, allowed are ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']")

    if docstring is not None:
        api_call.__doc__ = docstring

    return api_call
