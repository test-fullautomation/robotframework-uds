from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from RobotFramework_DoIP.DoipKeywords import DoipKeywords
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from udsoncan.Response import Response
from udsoncan.BaseService import BaseService

class UDSLibrary:
    def __init__(self, doip_layer, name=None, close_connection=False):
        self.doip_layer = doip_layer
        self.name = name
        self.uds_connector = DoIPClientUDSConnector(doip_layer.client, name, close_connection)
        self.uds_connector.open()

    @keyword("Build payload")
    def build_payload(self, diag_service, parameters=None):
        if diag_service is None:
            raise ValueError("The request object cannot be None.")

        try:
            uds = ""
            param_dict = {}
            if parameters:
                for param in parameters:
                    isolate_list = param.split("=")
                    param_dict[isolate_list[0]] = eval(isolate_list[1])
                logger.info(f"[uds]parameters: {param_dict}")

                try:
                    uds = diag_service(**param_dict).hex()
                except Exception as e:
                    logger.warn(f"retrieve uds error: {e}")
            else:
                uds = diag_service().hex()
                if len(uds) > 0:
                    logger.warn(f"[uds]uds: {uds}")
                else:
                    logger.warn("[uds]uds: retrieve uds failed.")

            logger.info("Building payload for the request...")
            # Build the payload
            payload = self.doip_layer.build_payload(uds)

            logger.info("Payload successfully built.")
        except ValueError as e:
            logger.error(f"ValueError while building payload: {e}")
            raise
        except TypeError as e:
            logger.error(f"TypeError while building payload: {e}")
            raise

        return payload

    @keyword("Send request")
    def send_request(self, payload, timeout=2):
        if payload is None:
            raise ValueError("The payload cannot be None.")

        try:
            logger.info("Sending diagnostic message with payload...")

            # Send the diagnostic message
            self.doip_layer.client.send_doip(payload[0], payload[1])
            logger.info("Waiting for response...")

            # Receive the response with a specified timeout
            response_encoded = self.doip_layer.receive_diagnostic_message(timeout)
            logger.info("Response received.")
            logger.info(f"Response encoded: {response_encoded}")
            return response_encoded

        except TimeoutError as e:
            logger.error(f"Timeout occurred while waiting for response: {e}")
            raise e
        except ValueError as e:
            logger.error(f"ValueError encountered: {e}")
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred while sending request.")
            raise Exception(f"Failed to send request due to an unexpected error. {e}")

    @keyword("Interpret response data")
    def interpret_response_data(self, response):
        try:
            msg = bytes.fromhex(response)
            res = Response()
            res = res.from_payload(msg)
            logger.info("Successfully interpreted response")
            # Log relevant information from res if needed
            logger.info(f"Response details: {res.code_name}")

        except Exception as e:
            logger.error(f"Error interpreting response: {str(e)}")

    @keyword("Validate response content")
    def validate_content_response(response: Response, expected_service: int, expected_data=None) -> bool:
        """
        Validates the content of a UDS response.

        :param response: The UDS response object to validate.
        :param expected_service: The expected service ID of the response.
        :param expected_data: The expected data (optional) to be matched within the response.
        :return: True if the response is valid, False otherwise.
        """
        # Check if the response service is as expected
        if response.service != expected_service:
            logger.error(f"Unexpected service ID: {response.service} (expected: {expected_service})")
            return False

        # Check if the response is a positive response
        if response.code != Response.Code.PositiveResponse:
            logger.error(f"Unexpected response code: {response.code}")
            return False

        # Validate the content of the response data, if expected data is provided
        if expected_data is not None:
            if response.data != expected_data:
                logger.error(f"Unexpected response data: {response.data} (expected: {expected_data})")
                return False

        logger.info("Response is valid.")
        return True
