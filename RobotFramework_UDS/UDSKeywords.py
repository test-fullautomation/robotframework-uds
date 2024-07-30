from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from RobotFramework_DoIP.DoipKeywords import DoipKeywords
import time
import odxtools
import sys
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from udsoncan.services import *
from udsoncan.Request import Request
from udsoncan.Response import Response
from typing import Type, Optional, Union
from udsoncan.BaseService import BaseService
class UDSLibrary:
    def __init__(self, doip_layer, name=None, close_connection=False):
        self.doip_layer = doip_layer
        self.name = name
        self.uds_connector = DoIPClientUDSConnector(doip_layer.client, name, close_connection)

    @keyword("Build payload")
    def build_payload(self,
                      service: Optional[Union[BaseService, Type[BaseService]]] = None,
                      subfunction: Optional[int] = None,
                      suppress_positive_response: Optional[bool] = False,
                      data: Optional[bytes] = None,
                      encoded: Optional[bool] = True):
        
        uds_request = Request(service, subfunction, suppress_positive_response, data)
        payload = uds_request.get_payload()
        if encoded:
            return payload.hex()
        return payload

    @keyword("Send request")
    def send_request(self, payload, timeout=2):
        try:
            self.doip_layer.send_diagnostic_message(payload)
            response = self.doip_layer.receive_diagnostic_message(timeout)
            return response
        except Exception as e:
            print("Error:" + e)

    @keyword("Interpret response data")
    def interpret_response_data(self, response, mode):
        try:
            res = Response(service=None, code=1, data=response)
            interpret = SecurityAccess.interpret_response(response, mode)
            return interpret
        except Exception as e:
            print("Errore:" + e)

    @keyword("Validate response content")
    def validate_response_content(self, actual, expected):
        try:
            pass
        except:
            pass