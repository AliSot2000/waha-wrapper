from waha_python_wrapper.tools import api_endpoint_wrapper, Methods
import waha_python_wrapper.waha_model as wm
from typing import List
from waha_python_wrapper.config import cfg
import asyncio

start_session = api_endpoint_wrapper(path="/api/sessions/start",
                                     request_model=wm.SessionStartRequest,
                                     response_model=wm.SessionDTO,
                                     expected_code=201,
                                     body_defaults={"name": "default"},
                                     method=Methods.POST,
                                     docstring="""
                                     Async python wrapper for the WAHA API to start a session
                                     
                                     session.name: str = "default"
                                     
                                     :param req: SessionStartRequest
                                     :return: SessionDTO
                                     """
                                     )


stop_session = api_endpoint_wrapper(path="/api/sessions/stop",
                                    request_model=wm.SessionStopRequest,
                                    expected_code=201,
                                    body_defaults={"name": "default"},
                                    method=Methods.POST,
                                    docstring="""
                                     Async python wrapper for the WAHA API to stop a session

                                     session.name: str = "default"

                                     :param req: SessionStartRequest
                                     :return: SessionDTO
                                     """
                                    )


list_session = api_endpoint_wrapper(path="/api/sessions/",
                                    response_model=List[wm.SessionInfo],
                                    expected_code=200,
                                    method=Methods.GET,
                                    docstring="""
                                     Async python wrapper for the WAHA API to list sessions

                                     :return: SessionListDTO
                                     """
                                    )


