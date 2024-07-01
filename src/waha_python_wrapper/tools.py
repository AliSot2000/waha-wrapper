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


async def handle_response(resp: aiohttp.ClientResponse, expected_code: int = 200, response_model: BaseModel = None):
    """
    Check the status code, generate error if one occurred, otherwise parse data and return it.

    :raise BaseAPIException: If the request failed without a JSON response
    :raise APIError: If the request failed with a JSON response
    :raise ValidationError: If the response could not be validated with the response_model
    """
    if not resp.status != expected_code:
        raise handle_error(resp=resp, expected_code=expected_code)

    if response_model is None:
        return await resp.content.read()

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


async def _request_no_body_no_params(target_url: str,
                                     response_model: BaseModel,
                                     expected_code: int,
                                     method: Methods,
                                     session: aiohttp.ClientSession = None,
                                     ):
    """
    Send Request that does not require a body or parameters

    :param target_url: url to send the request to, may contain path parameters
    :param response_model: model to be used for the response
    :param expected_code: expected http status code of response
    :param method: http method to be used
    :param session: aiohttp.ClientSession to be used for the request

    :return: Instance of ResponseModel or raise an error
    """
    # Make the Request
    if session is None:
        async with aiohttp.ClientSession() as session:
            async with session.request(method=str(method), url=target_url) as resp:
                return await handle_response(response_model=response_model,
                                             resp=resp,
                                             expected_code=expected_code)
    else:
        async with session.request(method=str(method), url=target_url) as resp:
            return await handle_response(response_model=response_model,
                                         resp=resp,
                                         expected_code=expected_code)


async def _request_body_no_params(target_url: str,
                                  response_model: BaseModel,
                                  expected_code: int,
                                  method: Methods,
                                  body: BaseModel,
                                  session: aiohttp.ClientSession = None):
    """
    Send Request that requires a body but no parameters

    :param target_url: url to send the request to, may contain path parameters
    :param response_model: model to be used for the response
    :param expected_code: expected http status code of response
    :param method: http method to be used
    :param body: json body model to be used for the request
    :param session: aiohttp.ClientSession to be used for the request

    :return: Instance of ResponseModel or raise an error
    """
    # Make the Request
    if session is None:
        async with aiohttp.ClientSession() as session:
            async with session.request(url=target_url,
                                       json=body.model_dump(by_alias=True),
                                       method=str(method)) as resp:
                return await handle_response(response_model=response_model,
                                             resp=resp,
                                             expected_code=expected_code)
    else:
        async with session.request(url=target_url,
                                   json=body.model_dump(by_alias=True),
                                   method=str(method)) as resp:
            return await handle_response(response_model=response_model,
                                         resp=resp,
                                         expected_code=expected_code)


async def _request_no_body_params(target_url: str,
                                  response_model: BaseModel,
                                  expected_code: int,
                                  method: Methods,
                                  params: BaseModel,
                                  session: aiohttp.ClientSession = None):
    """
    Send Request that requires parameters but no body

    :param target_url: url to send the request to, may contain path parameters
    :param response_model: model to be used for the response
    :param expected_code: expected http status code of response
    :param method: http method to be used
    :param params: json parameters model to be used for the request
    :param session: aiohttp.ClientSession to be used for the request

    :return: Instance of ResponseModel or raise an error
    """
    # Make the Request
    if session is None:
        async with aiohttp.ClientSession() as session:
            async with session.request(url=target_url,
                                       params=params.model_dump(by_alias=True),
                                       method=str(method)) as resp:
                return await handle_response(response_model=response_model,
                                             resp=resp,
                                             expected_code=expected_code)
    else:
        async with session.request(url=target_url,
                                   params=params.model_dump(by_alias=True),
                                   method=str(method)) as resp:
            return await handle_response(response_model=response_model,
                                         resp=resp,
                                         expected_code=expected_code)


async def _request_body_params(target_url: str,
                               response_model: BaseModel,
                               expected_code: int,
                               method: Methods,
                               body: BaseModel,
                               params: BaseModel,
                               session: aiohttp.ClientSession = None):
    """
    Send Request that requires parameters and a body

    :param target_url: url to send the request to, may contain path parameters
    :param response_model: model to be used for the response
    :param expected_code: expected http status code of response
    :param method: http method to be used
    :param body: json body model to be used for the request
    :param params: json parameters model to be used for the request
    :param session: aiohttp.ClientSession to be used for the request

    :return: Instance of ResponseModel or raise an error
    """
    if session is None:
        async with aiohttp.ClientSession() as session:
            async with session.request(method=str(method),
                                       url=target_url,
                                       params=params.model_dump(by_alias=True),
                                       json=body.model_dump(by_alias=True)) as resp:
                return await handle_response(response_model=response_model,
                                             resp=resp,
                                             expected_code=expected_code)
    else:
        async with session.request(url=target_url,
                                   method=str(method),
                                   params=params.model_dump(by_alias=True),
                                   json=body.model_dump(by_alias=True)) as resp:
            return await handle_response(response_model=response_model,
                                         resp=resp,
                                         expected_code=expected_code)


def _function_factory(path: str,
                      response_model: BaseModel,
                      expected_code: int,
                      param_defaults: dict,
                      body_defaults: dict,
                      method: Methods = Methods.POST,
                      params_model: BaseModel = None,
                      request_model: BaseModel = None,
                      cleaned_args: List[str] = None,
                      ):
    """
    Factory function to generate an async callable to make the request. Differentiates the 8 different
    combinations of params_model, request_model and cleaned_args.

    :param path: path of the API endpoint, may include path parameters
    :param response_model: model to be used for the response
    :param expected_code: expected http status code of response
    :param param_defaults: param_defaults generated by the parent factory function
    :param body_defaults: body_defaults generated by the parent factory function
    :param method: http method to be used
    :param params_model: param_model to be used for the request if any
    :param request_model: request_model to be used for request if any
    :param cleaned_args: path arguments to be used for the request if any are present
    :return:
    """

    # 0, 0, 0
    if params_model is None and request_model is None and cleaned_args is None:
        async def api_call(cfg: WAHAConfig,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            target_url = f'{cfg.waha_url}{path}'

            return await _request_no_body_no_params(target_url=target_url,
                                                    response_model=response_model,
                                                    expected_code=expected_code,
                                                    method=method,
                                                    session=session)

    # 0, 0, 1
    if params_model is None and request_model is None and cleaned_args is not None:
        async def api_call(cfg: WAHAConfig,
                           session: aiohttp.ClientSession = None,
                           **kwargs) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Check Path Params
            if set(kwargs.keys()) != set(cleaned_args):
                raise ValueError(f"Expected path params {cleaned_args}, got {set(kwargs.keys())}")

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            return await _request_no_body_no_params(target_url=target_url,
                                                    response_model=response_model,
                                                    expected_code=expected_code,
                                                    method=method,
                                                    session=session)

    # 0, 1, 0
    if params_model is None and request_model is not None and cleaned_args is None:
        async def api_call(cfg: WAHAConfig,
                           body: request_model = None,
                           session: aiohttp.ClientSession = None) \
                -> response_model:
            f"""
            DEFAULT DOCSTRING: Simple API endpoint call for {path}
            """
            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{path}'

            return await _request_body_no_params(target_url=target_url,
                                                 response_model=response_model,
                                                 expected_code=expected_code,
                                                 method=method,
                                                 body=body,
                                                 session=session)

    # 0, 1, 1
    if params_model is None and request_model is not None and cleaned_args is not None:
        async def api_call(cfg: WAHAConfig,
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

            # Create default body
            if body is None:
                body = request_model.model_validate(body_defaults)

            target_url = f'{cfg.waha_url}{populate_path_params(path, kwargs)}'

            return await _request_body_no_params(target_url=target_url,
                                                 response_model=response_model,
                                                 expected_code=expected_code,
                                                 method=method,
                                                 body=body,
                                                 session=session)

    # 1, 0, 0
    if params_model is not None and request_model is None and cleaned_args is None:
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

            return await _request_no_body_params(target_url=target_url,
                                                 response_model=response_model,
                                                 expected_code=expected_code,
                                                 method=method,
                                                 params=params,
                                                 session=session)

    # 1, 0, 1
    if params_model is not None and request_model is None and cleaned_args is not None:
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

            return await _request_no_body_params(target_url=target_url,
                                                 response_model=response_model,
                                                 expected_code=expected_code,
                                                 method=method,
                                                 params=params,
                                                 session=session)

    # 1, 1, 0
    if params_model is not None and request_model is not None and cleaned_args is None:
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

            return await _request_body_params(target_url=target_url,
                                              response_model=response_model,
                                              expected_code=expected_code,
                                              method=method,
                                              body=body,
                                              params=params,
                                              session=session)

    # 1, 1, 1
    else:
        assert params_model is not None and request_model is not None and cleaned_args is not None, "Invalid combination of params"

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

            return await _request_body_params(target_url=target_url,
                                              response_model=response_model,
                                              expected_code=expected_code,
                                              method=method,
                                              body=body,
                                              params=params,
                                              session=session)

    return api_call


def api_endpoint_wrapper(path: str,
                         expected_code: int,
                         method: Methods | str,
                         docstring: str = None,
                         params_model: BaseModel = None,
                         request_model: BaseModel = None,
                         response_model: BaseModel = None,
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

    if len(cleaned_args) == 0:
        cleaned_args = None

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

    api_call = _function_factory(
        path=path,
        response_model=response_model,
        expected_code=expected_code,
        param_defaults=param_defaults,
        body_defaults=body_defaults,
        method=parsed_method,
        params_model=params_model,
        request_model=request_model,
        cleaned_args=cleaned_args,
    )

    if docstring is not None:
        api_call.__doc__ = docstring

    return api_call
