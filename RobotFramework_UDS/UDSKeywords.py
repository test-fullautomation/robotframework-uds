from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from RobotFramework_DoIP.DoipKeywords import DoipKeywords
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan import CommunicationType, DynamicDidDefinition, IOMasks, IOValues, MemoryLocation
from udsoncan.client import Client
from udsoncan.Request import Request
from udsoncan.Response import Response
from udsoncan.BaseService import BaseService
from typing import Callable, Optional, Union, Dict, List, Any, cast, Type
from udsoncan.services import *

class UDSLibrary:
    def __init__(self, doip_layer, name=None, close_connection=False):
        self.doip_layer = doip_layer
        self.name = name
        self.uds_connector = DoIPClientUDSConnector(doip_layer.client, name, close_connection)
        self.uds_connector.open()
        self.service_list = None
        self.client = Client(self.uds_connector)

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
            print(f"Response details: {res.code_name}")
        except Exception as e:
            logger.error(f"Error interpreting response: {str(e)}")

    @keyword("Validate response content")
    def validate_content_response(response: Response, expected_service: int, expected_data=None):
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

# Client methods/keywords
    @keyword("Configure")
    def configure(self):
        return

    @keyword("Connect")
    def connect(self):
        return

    @keyword("Disconnect")
    def connect(self):
        return

    @keyword("Access Timing Parameter")
    def access_timing_parameter(self, access_type: int, timing_param_record: Optional[bytes] = None):
        """
        **Description:**
            Sends a generic request for AccessTimingParameter service
        **Parameters:**
            * param ``access_type`` (required): The service subfunction

                - readExtendedTimingParameterSet      = 1
                - setTimingParametersToDefaultValues  = 2
                - readCurrentlyActiveTimingParameters = 3
                - setTimingParametersToGivenValues    = 4
            * type ``access_type`` int

            * param ``timing_param_record`` (optional): The parameters data. Specific to each ECU.
            * type ``timing_param_record`` bytes
        """
        response = self.client.access_timing_parameter(self, access_type, timing_param_record)
        return response

    @keyword("Clear Diagnostic Information")
    def clear_dianostic_infomation(self, group: int = 0xFFFFFF, memory_selection: Optional[int] = None):
        """
        **Description:**
            Requests the server to clear its active Diagnostic Trouble Codes.
        **Parameters:**
            * param ``group``: The group of DTCs to clear. It may refer to Powertrain DTCs, Chassis DTCs, etc. Values are defined by the ECU manufacturer except for two specific values

                - ``0x000000`` : Emissions-related systems
                - ``0xFFFFFF`` : All DTCs
            * type ``group``: int

            * param memory_selection: MemorySelection byte (0-0xFF). This value is user defined and introduced in 2020 version of ISO-14229-1.
                Only added to the request payload when different from None. Default : None
            * type ``memory_selection``: int
        """
        response = self.client.clear_dtc(group, memory_selection)
        return response

    @keyword("Communication Control")
    def communication_control(self, control_type: int, communication_type: Union[int, bytes, CommunicationType], node_id: Optional[int] = None):
        """
        **Description:**
            Switches the transmission or reception of certain messages on/off with CommunicationControl service.
        **Parameter:**
            * param ``control_type`` (required): The action to request such as enabling or disabling some messages. This value can also be ECU manufacturer-specific

                - enableRxAndTx                                      = 0
                - enableRxAndDisableTx                               = 1
                - disableRxAndEnableTx                               = 2
                - disableRxAndTx                                     = 3
                - enableRxAndDisableTxWithEnhancedAddressInformation = 4
                - enableRxAndTxWithEnhancedAddressInformation        = 5
            * type ``control_type``: int

            * param ``communication_type`` (required): Indicates what section of the network and the type of message that should be affected by the command. Refer to :ref:`CommunicationType<CommunicationType>` for more details. If an `integer` or a `bytes` is given, the value will be decoded to create the required :ref:`CommunicationType<CommunicationType>` object
            * type communication_type: :ref:`CommunicationType<CommunicationType>`, bytes, int

            * param ``node_id`` (optional): DTC memory identifier (nodeIdentificationNumber). This value is user defined and introduced in 2013 version of ISO-14229-1.
            Possible only when control type is ``enableRxAndDisableTxWithEnhancedAddressInformation`` or ``enableRxAndTxWithEnhancedAddressInformation``
            Only added to the request payload when different from None. Default : None
            * type ``node_id``: int
        """
        response = self.client.communication_control(control_type, communication_type, node_id)
        return response

    @keyword("Control DTC Setting")
    def control_dtc_setting(self, setting_type: int, data: Optional[bytes] = None):
        """
        **Description:**
            Controls some settings related to the Diagnostic Trouble Codes by sending a ControlDTCSetting service request.
            It can enable/disable some DTCs or perform some ECU specific configuration.
        **Paramters:**
            * param ``setting_type`` (required): Allowed values are from 0 to 0x7F.
                - on  = 1
                - off = 2
                - vehicleManufacturerSpecific = (0x40, 0x5F)  # To be able to print textual name for logging only.
                - systemSupplierSpecific      = (0x60, 0x7E)  # To be able to print textual name for logging only.

            * type ``setting_type``: int

            * param ``data`` (optional): Optional additional data sent with the request called `DTCSettingControlOptionRecord`
            * type ``data``: bytes
        """
        response = self.client.control_dtc_setting(setting_type, data)
        return response

    @keyword("Diagnostic Session Control")
    def diagnostic_session_control(self, session_type):
        """
        **Description:**
            Requests the server to change the diagnostic session with a DiagnosticSessionControl service request.
        **Parameters:**
            * param ``newsession`` (required): The session to try to switch.
                - defaultSession                = 1
                - programmingSession            = 2
                - extendedDiagnosticSession     = 3
                - safetySystemDiagnosticSession = 4

            * type ``newsession``: int
        """
        response = self.client.change_session(session_type)
        return response

    @keyword("Dynamically Define Data Identifier")
    def dynamically_define_did(self, did: int, did_definition: Union[DynamicDidDefinition, MemoryLocation]):
        """
        **Description:**
            Defines a dynamically defined DID.
        **Parameters:**
            * param ``did``: The data identifier to define.
            * type ``did``: int

            * param ``did_definition``: The definition of the DID. Can be defined by source DID or memory address.
                If a :ref:`MemoryLocation<MemoryLocation>` object is given, definition will automatically be by memory address
            * type ``did_definition``: :ref:`DynamicDidDefinition<DynamicDidDefinition>` or :ref:`MemoryLocation<MemoryLocation>`
        """
        response = self.client.dynamically_define_did(did, did_definition)
        return response

    @keyword("ECU Reset")
    def ecu_reset(self, reset_type: int):
        """
        Requests the server to execute a reset sequence through the ECUReset service.

            * param ``reset_type`` (required): The type of reset to perform.
                - hardReset                 = 1
                - keyOffOnReset             = 2
                - softReset                 = 3
                - enableRapidPowerShutDown  = 4
                - disableRapidPowerShutDown = 5

            * type reset_type: int
        """
        response = self.client.ecu_reset(reset_type)
        return response

    @keyword("Input Output Control By Identifier")
    def io_control(self,
                   did: int,
                   control_param: Optional[int] = None,
                   values: Optional[Union[List[Any], Dict[str, Any], IOValues]] = None,
                   masks: Optional[Union[List[str], Dict[str, bool], IOMasks, bool]] = None):
        """
        **Description:**
            Substitutes the value of an input signal or overrides the state of an output by sending a InputOutputControlByIdentifier service request.`
        **Parameters:**
            * param ``did`` (required): Data identifier to represent the IO
            * type ``did`: int

            * param ``control_param`` (optional): Optional parameter that can be a value from :class:`InputOutputControlByIdentifier.ControlParam<udsoncan.services.InputOutputControlByIdentifier.ControlParam>`
            * type ``control_param``: int

            * param ``values`` (optional): Optional values to send to the server. This parameter will be given to :ref:`DidCodec<DidCodec>`.encode() method.
                It can be:
                        - A list for positional arguments
                        - A dict for named arguments
                        - An instance of IOValues<IOValues> for mixed arguments

            * type ``values`` (optional): list, dict, :ref:`IOValues<IOValues>`

            * param masks: Optional mask record for composite values. The mask definition must be included in ``config['input_output']``
                It can be:
                        - A list naming the bit mask to set
                        - A dict with the mask name as a key and a boolean setting or clearing the mask as the value
                        - An instance of IOMask<IOMask
                        - A boolean value to set all masks to the same value.
            * type masks: list, dict, IOMask<IOMask>, bool
        """
        response = self.client.io_control(did, control_param, values, masks)
        return response

    @keyword("Routine Control")
    def routine_control(self, routine_id: int, control_type: int, data: Optional[bytes] = None):
        """
        **Description:**
            Sends a generic request for the RoutineControl service
        **Parameters:**
            * param ``routine_id`` (required): The 16-bit numerical ID of the routine
            * type ``routine_id`` int

            * param ``control_type`` (required): The service subfunction
            * type ``control_type`` int
            * valid ``control_type``
                - startRoutine          = 1
                - stopRoutine           = 2
                - requestRoutineResults = 3

            * param ``data`` (optional): Optional additional data to give to the server
            * type ``data`` bytes
        """
        response = self.client.routine_control(routine_id, control_type, data)
        return response

    @keyword("Read Data By Identifier")
    def read_data_by_identifier(self, data_id_list):
        response = self.client.read_data_by_identifier(data_id_list)
        return response

    @keyword("Tester Present")
    def TesterPresent(self):
        response = self.client.tester_present()
        return response
