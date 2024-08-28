from email import message
from robot.api.deco import keyword
from robot.api import logger
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan import CommunicationType, DynamicDidDefinition, IOMasks, IOValues, MemoryLocation
from udsoncan.client import Client
from udsoncan.Response import Response
from typing import Optional, Union, Dict, List, Any, cast
from udsoncan.common.Filesize import Filesize
from udsoncan.common.Baudrate import Baudrate
from udsoncan.common.DataFormatIdentifier import DataFormatIdentifier
from udsoncan.common.dtc import Dtc
from RobotFramework_UDS.DiagnosticServices import DiagnosticServices
from udsoncan.configs import default_client_config
from udsoncan import latest_standard
from udsoncan.typing import ClientConfig
from doipclient import DoIPClient
from doipclient import messages
from robot.libraries.BuiltIn import BuiltIn
import udsoncan

class UDSKeywords:
    def __init__(self):
        self.doip_layer = None
        self.name = None
        self.uds_connector = None
        self.diag_service_db = None
        self.client = None
        self.config = default_client_config
        self.config['data_identifiers'] = {
            'default' : '>H'                       # Default codec is a struct.pack/unpack string. 16bits little endian
            # 0xF190 : udsoncan.AsciiCodec(15),    # Codec that read ASCII string. We must tell the length of the string
            # 0x6330 : udsoncan.AsciiCodec(15)
        }

    @keyword("Connect UDS Connector")
    def connect_uds_connector(self, name=None, config=default_client_config, close_connection=False):
        self.name = name
        self.diag_service_db = None
        self.config = config
        self.uds_connector = DoIPClientUDSConnector(self.doip_layer.client, self.name, close_connection)
        self.client = Client(self.uds_connector, self.config)
        print("")

    @keyword("Create UDS Connector")
    def create_uds_connector(self,
                             ecu_ip_address,
                             ecu_logical_address,
                             name="doip",
                             activation_type=0,
                             client_logical_address=0x0E00,
                             client_ip_address=None):
        """
        **Description:**
            Create a connection to establish
        **Parameters:**
            * param ``name``: Name of connection

                - doip: Establish a doip connection to an (ECU)
            * type ``name``: str

            * param ``ecu_ip_address`` (required): The IP address of the ECU to establish a connection. This should be a string representing an IPv4
                    address like "192.168.1.1" or an IPv6 address like "2001:db8::".
            * type ``ecu_ip_address``: str

            * param ``ecu_logical_address`` (required): The logical address of the ECU.
            * type ``ecu_logical_address``: any

            * param ``activation_type`` (optional): The type of activation, which can be the default value (ActivationTypeDefault) or a specific value based on application-specific settings.
            * type ``activation_type``: RoutingActivationRequest.ActivationType,

            * param ``client_logical_address`` (optional): The logical address that this DoIP client will use to identify itself. Per the spec,
                    this should be 0x0E00 to 0x0FFF. Can typically be left as default.
            * type ``client_logical_address``: int

            * param ``client_ip_address`` (optional): If specified, attempts to bind to this IP as the source for both UDP and TCP communication.
                    Useful if you have multiple network adapters. Can be an IPv4 or IPv6 address just like `ecu_ip_address`, though
                    the type should match.
            * type ``client_ip_address``: str
        """
        if isinstance(ecu_logical_address, str):
            ecu_logical_address = int(ecu_logical_address)

        if isinstance(client_logical_address, str):
            client_logical_address = int(client_logical_address)

        ecu_ip_address = ecu_ip_address.strip()
        client_ip_address = client_ip_address.strip()

        if name=="doip":
            doip = DoIPClient()
            doip.connect_to_ecu(ecu_ip_address,
                                ecu_logical_address,
                                activation_type,
                                client_logical_address,
                                client_ip_address)
            self.doip_layer = doip

    @keyword("Load PDX")
    def load_pdx(self, pdx_file, variant):
        """
        **Description:**
            Load PDX
        **Parameters:**
            * param ``pdx_file``: pdx file path
            * type ``pdx_file``: str

            * param ``variant``:
            * type ``variant``: str
        """
        self.diag_service_db = DiagnosticServices(pdx_file, variant)

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
            if uds is None:
                raise ValueError("The request cannot be None.")
            
            msg = bytes.fromhex(uds)
            message = messages.DiagnosticMessage(self.client._client_logical_address, self.client._ecu_logical_address, msg)
            rtype = messages.payload_message_to_type[type(message)]
            rdata = message.pack()
            payload = self.client._pack_doip(self.client._protocol_version, rtype, rdata)

            logger.info("Payload successfully built.")
        except ValueError as e:
            logger.error(f"ValueError while building payload: {e}")
            raise
        except TypeError as e:
            logger.error(f"TypeError while building payload: {e}")
            raise

        return bytes(payload)


        if request is None:
            raise ValueError("The request cannot be None.")

        msg = bytes.fromhex(request)
        message = messages.DiagnosticMessage(self.client._client_logical_address, self.client._ecu_logical_address, msg)
        rtype = messages.payload_message_to_type[type(message)]
        rdata = message.pack()
        data_bytes = self.client._pack_doip(self.client._protocol_version, rtype, rdata)

        return bytes(data_bytes)

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
    def validate_content_response(self, response: Response, expected_service: int, expected_data=None):
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
    @keyword("Create UDS Config")
    def create_config(self,
                  exception_on_negative_response = True,
                  exception_on_invalid_response = True,
                  exception_on_unexpected_response = True,
                  security_algo = None,
                  security_algo_params = None,
                  tolerate_zero_padding = True,
                  ignore_all_zero_dtc = True,
                  dtc_snapshot_did_size = 2,
                  server_address_format = None,
                  server_memorysize_format = None,
                  data_identifiers = {},
                  input_output = {},
                  request_timeout = 5,
                  p2_timeout = 1,
                  p2_star_timeout = 5,
                  standard_version = latest_standard,
                  use_server_timing = True,
                  extended_data_size = None):
        """
        **Description:**
            Create a config for UDS connector
        **Parameters:**
            Will be update later
        """
        config = cast(ClientConfig, {
            'exception_on_negative_response': exception_on_negative_response,
            'exception_on_invalid_response': exception_on_invalid_response,
            'exception_on_unexpected_response': exception_on_unexpected_response,
            'security_algo': security_algo,
            'security_algo_params': security_algo_params,
            'tolerate_zero_padding': tolerate_zero_padding,
            'ignore_all_zero_dtc': ignore_all_zero_dtc,
            'dtc_snapshot_did_size': dtc_snapshot_did_size,  # Not specified in standard. 2 bytes matches other services format.
            'server_address_format': server_address_format,  # 8,16,24,32,40
            'server_memorysize_format': server_memorysize_format,  # 8,16,24,32,40
            'data_identifiers': data_identifiers,
            'input_output': input_output,
            'request_timeout': request_timeout,
            'p2_timeout': p2_timeout,
            'p2_star_timeout': p2_star_timeout,
            'standard_version': standard_version,  # 2006, 2013, 2020
            'use_server_timing': use_server_timing,
            'extended_data_size': extended_data_size})
        return config

    @keyword("Set UDS Config")
    def set_config(self):
        '''
        **Description:**
            Set UDS config
            Using create_configure to create a new config for UDS connector.
            If not, the default config will be use.
        '''
        self.client.set_configs(self.config)

    @keyword("Open uds connection")
    def connect(self):
        '''
        **Description:**
            Open uds connection
        '''
        self.uds_connector.open()

    @keyword("Close UDS Connection")
    def disconnect(self):
        '''
        **Description:**
            Close uds connection
        '''
        self.uds_connector.close()

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
        response = self.client.access_timing_parameter(access_type, timing_param_record)
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
        if isinstance(session_type, str):
            session_type = int(session_type)
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
        response = None
        if isinstance(reset_type, str):
            reset_type = int(reset_type)

        try:
            response = self.client.ecu_reset(reset_type)
        except Exception as e:
            BuiltIn().fail(f"Fail to send a ECU Reset request. Reason: {e}")
        return response

    @keyword("Input Output Control By Identifier")
    def io_control(self,
                   did: int,
                   control_param: Optional[int] = None,
                   values: Optional[Union[List[Any], Dict[str, Any], IOValues]] = None,
                   masks: Optional[Union[List[str], Dict[str, bool], IOMasks, bool]] = None):
        """
        **Description:**
            Substitutes the value of an input signal or overrides the state of an output by sending a InputOutputControlByIdentifier service request.
        **Parameters:**
            * param ``did`` (required): Data identifier to represent the IO
            * type ``did`: int

            * param ``control_param`` (optional):
                - returnControlToECU = 0
                - resetToDefault = 1
                - freezeCurrentState = 2
                - shortTermAdjustment = 3

            * type ``control_param``: int

            * param ``values`` (optional): Optional values to send to the server. This parameter will be given to DidCodec<DidCodec>.encode() method.
                It can be:
                        - A list for positional arguments
                        - A dict for named arguments
                        - An instance of IOValues<IOValues> for mixed arguments

            * type ``values``: list, dict, IOValues<IOValues>

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

    @keyword("Link Control")
    def link_control(self, control_type: int, baudrate: Optional[Baudrate] = None):
        """
        **Description:**
            Controls the communication baudrate by sending a LinkControl service request.
        **Parameters:**

            * param ``control_type`` (required): Allowed values are from 0 to 0xFF.
                - verifyBaudrateTransitionWithFixedBaudrate    = 1
                - verifyBaudrateTransitionWithSpecificBaudrate = 2
                - transitionBaudrate                           = 3
            * type ``control_type``: int

            * param ``baudrate`` (required): Required baudrate value when ``control_type`` is either ``verifyBaudrateTransitionWithFixedBaudrate`` (1) or ``verifyBaudrateTransitionWithSpecificBaudrate`` (2)
            * type ``baudrate``: Baudrate <Baudrate>
        """
        response = self.client.link_control(control_type, baudrate)
        return response

    @keyword("Read Data By Identifier")
    def read_data_by_identifier(self, data_id_list: Union[int, List[int]]):
        """
        **Description:**
            Requests a value associated with a data identifier (DID) through the :ref:`ReadDataByIdentifier<ReadDataByIdentifier>` service.
        **Parameters:**

        See :ref:`an example<reading_a_did>` about how to read a DID

        * param data_id_list: The list of DID to be read
        * type data_id_list: int | list[int]
        """
        response = self.client.read_data_by_identifier(data_id_list)
        return response

    @keyword("Read DTC Information")
    def read_dtc_information(self,
                             subfunction: int,
                             status_mask: Optional[int] = None,
                             severity_mask: Optional[int] = None,
                             dtc: Optional[Union[int, Dtc]] = None,
                             snapshot_record_number: Optional[int] = None,
                             extended_data_record_number: Optional[int] = None,
                             extended_data_size: Optional[int] = None,
                             memory_selection: Optional[int] = None):
        '''
            Update later
        '''
        response = self.client.read_dtc_information(subfunction, status_mask, severity_mask, dtc, snapshot_record_number,extended_data_record_number, extended_data_size, memory_selection)
        return response

    @keyword("Read Memory By Address")
    def read_memory_by_address(self, memory_location: MemoryLocation):
        '''
        **Description:**
            Reads a block of memory from the server by sending a ReadMemoryByAddress service request. 
        **Parameters:**
        
        * param ``memory_location`` (required): The address and the size of the memory block to read.
        * type ``memory_location``: MemoryLocation <MemoryLocation>
        '''
        response = self.client.read_memory_by_address(memory_location)
        return response

    @keyword("Request Download")
    def request_download(self, memory_location: MemoryLocation, dfi: Optional[DataFormatIdentifier] = None):
        '''
        **Description:**
            Informs the server that the client wants to initiate a download from the client to the server by sending a RequestDownload service request.

        :Effective configuration: ``exception_on_<type>_response`` ``server_address_format`` ``server_memorysize_format``
        **Parameters:**
            * param ``memory_location`` (required): The address and size of the memory block to be written.
            * type ``memory_location``: MemoryLocation <MemoryLocation>

            * param ``dfi`` (optional): Optional defining the compression and encryption scheme of the data. 
                If not specified, the default value of 00 will be used, specifying no encryption and no compression
            * type dfi: DataFormatIdentifier <DataFormatIdentifier>
        '''
        response = self.client.request_download(memory_location, dfi)
        return response
    
    @keyword("Request Transfer Exit")
    def request_transfer_exit(self, data: Optional[bytes] = None):
        '''
        **Description:**
            Informs the server that the client wants to stop the data transfer by sending a RequestTransferExit service request.

        :Effective configuration: ``exception_on_<type>_response``
        **Parameters:**
            * param ``data`` (optional): Optional additional data to send to the server
            * type ``data``: bytes
        '''
        response = self.client.request_transfer_exit(data)
        return response

    @keyword("Request Upload")
    def request_upload(self, memory_location: MemoryLocation, dfi: Optional[DataFormatIdentifier] = None):
        '''
        **Description:**
            Informs the server that the client wants to initiate an upload from the server to the client by sending a :ref:`RequestUpload<RequestUpload>` service request.

        :Effective configuration: ``exception_on_<type>_response`` ``server_address_format`` ``server_memorysize_format``
        **Parameters:**
            * param ``memory_location`` (required): The address and size of the memory block to be written.
            * type ``memory_location``: MemoryLocation <MemoryLocation>

            * param dfi (optional): Optional defining the compression and encryption scheme of the data. 
                If not specified, the default value of 00 will be used, specifying no encryption and no compression
            *type dfi: DataFormatIdentifier <DataFormatIdentifier>
        '''
        response = self.client.request_upload(memory_location, dfi)
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
        try:
            response = self.client.routine_control(routine_id, control_type, data)
        except Exception as e:
            BuiltIn().fail(f"Fail to send a Routine Control request. Reason: {e}")
        return response

    @keyword("Security Access")
    def security_access(self, level, seed_params=bytes()):
        '''
        **Description:**
        Successively calls request_seed and send_key to unlock a security level with the SecurityAccess service.
        The key computation is done by calling config['security_algo']

        :Effective configuration: ``exception_on_<type>_response`` ``security_algo`` ``security_algo_params``
        **Parameters:**
            * param ``level`` (required): The level to unlock. Can be the odd or even variant of it.
            * type ``level``: int

            * param ``seed_params`` (optional): Optional data to attach to the RequestSeed request (securityAccessDataRecord).
            * type ``seed_params``: bytes
        '''
        response = self.client.unlock_security_access(level, seed_params)
        return response

    @keyword("Tester Present")
    def tester_present(self):
        '''
        **Description:**
            Sends a TesterPresent request to keep the session active.

        :Effective configuration: ``exception_on_<type>_response``
        '''
        response = None
        try:
            response = self.client.tester_present()
        except Exception as e:
            BuiltIn().fail(f"Fail to send a TesterPresent request. Reason: {e}")
        return response

    @keyword("Transfer Data")
    def transfer_data(self, sequence_number: int, data: Optional[bytes] = None):
        '''
        **Description:**
            Transfer a block of data to/from the client to/from the server by sending a TransferData service request and returning the server response.

        :Effective configuration: ``exception_on_<type>_response``
        **Parameters:**
            * param ``sequence_number`` (required): Corresponds to an 8bit counter that should increment for each new block transferred.
                Allowed values are from 0 to 0xFF
            * type ``sequence_number``: int

            * param ``data`` (optional): Optional additional data to send to the server
            * type ``data``: bytes
        '''
        response = self.client.transfer_data(sequence_number, data)
        return response
    
    @keyword("Write Data By Identifier")
    def write_data_by_identifier(self, did: int, value: Any):
        '''
        **Description:**
            Requests to write a value associated with a data identifier (DID) through the WriteDataByIdentifier service.

        :Effective configuration:  ``exception_on_<type>_response`` ``data_identifiers``
        **Parameters:**
            * param did: The DID to write its value
            * type did: int

            * param value: Value given to the DidCodec.encode method. The payload returned by the codec will be sent to the server.
            * type value: int
        '''
        response = self.client.write_data_by_identifier(did, value)
        return response

    @keyword("Write Memory By Address")
    def write_memory_by_address(self, memory_location: MemoryLocation, data: bytes):
        '''
        **Description:**
            Writes a block of memory in the server by sending a WriteMemoryByAddress service request. 

        :Effective configuration: ``exception_on_<type>_response`` ``server_address_format`` ``server_memorysize_format``
        **Parameters:**
            * param ``memory_location`` (required): The address and the size of the memory block to read. 
            * type ``memory_location``: MemoryLocation <MemoryLocation>

            * param ``data`` (required): The data to write into memory.
            * type ``data``: bytes
        '''
        response = self.client.write_memory_by_address(memory_location, data)
        return response

    @keyword("Request File Transfer")
    def request_file_transfer(self, 
                              moop: int,
                              path: str = '',
                              dfi: Optional[DataFormatIdentifier] = None,
                              filesize: Optional[Union[int, Filesize]] = None):
        
        '''
        **Parameters:**
            * param ``moop`` (required): Mode operate
                - AddFile = 1
                - DeleteFile = 2
                - ReplaceFile = 3
                - ReadFile = 4
                - ReadDir = 5
                - ResumeFile = 6
            
            * type ``moop``: int
            
            * param ``path`` (required):
            * type ``path``: str

            * param ``dfi``: DataFormatIdentifier defining the compression and encryption scheme of the data.
                If not specified, the default value of 00 will be used, specifying no encryption and no compression.
                Use for ``moop``:
                    - AddFile = 1
                    - ReplaceFile = 3
                    - ReadFile = 4
                    - ResumeFile = 6

            * type ``dfi``: DataFormatIdentifier

            * param ``filesize`` (optional): The filesize of the file to write. 
            If filesize is an object of type Filesize<Filesize>, the uncompressed size and compressed size will be encoded on
            the minimum amount of bytes necessary, unless a ``width`` is explicitly defined. If no compressed size is given or filesize is an ``int``,
            then the compressed size will be set equal to the uncompressed size or the integer value given as specified by ISO-14229
            Use for ``moop``:
                    - AddFile = 1
                    - ReplaceFile = 3
                    - ResumeFile = 6

            * type ``filesize``: int | Filesize
        '''
        
        response = self.client.request_file_transfer(moop, path, dfi, filesize)
        return response

    @keyword("Authentication")
    def authentication(self,
                       authentication_task: int,
                       communication_configuration: Optional[int] = None,
                       certificate_client: Optional[bytes] = None,
                       challenge_client: Optional[bytes] = None,
                       algorithm_indicator: Optional[bytes] = None,
                       certificate_evaluation_id: Optional[int] = None,
                       certificate_data: Optional[bytes] = None,
                       proof_of_ownership_client: Optional[bytes] = None,
                       ephemeral_public_key_client: Optional[bytes] = None,
                       additional_parameter: Optional[bytes] = None):
        '''
        **Description:**
            Sends an Authentication request introduced in 2020 version of ISO-14229-1. You can also use the helper functions to send each authentication task (sub function).

        :Effective configuration: ``exception_on_<type>_response``
        **Parameters:**
            * param ``authentication_task`` (required): The authenticationTask (subfunction) to use.
                - deAuthenticate = 0
                - verifyCertificateUnidirectional = 1
                - verifyCertificateBidirectional = 2
                - proofOfOwnership = 3
                - transmitCertificate = 4
                - requestChallengeForAuthentication = 5
                - verifyProofOfOwnershipUnidirectional = 6
                - verifyProofOfOwnershipBidirectional = 7
                - authenticationConfiguration = 8

            * type ``authentication_task``: int

            * param ``communication_configuration`` (optional): Optional Configuration information about how to proceed with security in further diagnostic communication after the Authentication (vehicle manufacturer specific).
                Allowed values are from 0 to 255.
            * type ``communication_configuration``: int

            * param ``certificate_client`` (optional): Optional The Certificate to verify.
            * type ``certificate_client``: bytes

            * param ``challenge_client`` (optional): Optional The challenge contains vehicle manufacturer specific formatted client data (likely containing randomized information) or is a random number.
            * type ``challenge_client``: bytes

            * param ``algorithm_indicator`` (optional): Optional Indicates the algorithm used in the generating and verifying Proof of Ownership (POWN),
                which further determines the parameters used in the algorithm and possibly the session key creation mode.
                This field is a 16 byte value containing the BER encoded OID value of the algorithm used.
                The value is left aligned and right padded with zero up to 16 bytes.
            * type ``algorithm_indicator``: bytes

            * param ``certificate_evaluation_id``: Optional unique ID to identify the evaluation type of the transmitted certificate.
                The value of this parameter is vehicle manufacturer specific.
                Subsequent diagnostic requests with the same evaluationTypeId will overwrite the certificate data of the previous requests.
                Allowed values are from 0 to 0xFFFF.
            * type certificate_evaluation_id: int

            * param ``certificate_data`` (optional): Optional The Certificate to verify.
            * type ``certificate_data``: bytes

            * param ``proof_of_ownership_client`` (optional): Optional Proof of Ownership of the previous given challenge to be verified by the server.
            * type ``proof_of_ownership_client``: bytes

            * param ``ephemeral_public_key_client`` (optional): Optional Ephemeral public key generated by the client for Diffie-Hellman key agreement.
            * type ``ephemeral_public_key_client``: bytes

            * param ``additional_parameter`` (optional): Optional additional parameter is provided to the server if the server indicates as neededAdditionalParameter.
            * type ``additional_parameter``: bytes
        '''
        response = self.client.authentication(authentication_task,
                                              communication_configuration,
                                              certificate_client,
                                              challenge_client,
                                              algorithm_indicator,
                                              certificate_evaluation_id,
                                              certificate_data,
                                              proof_of_ownership_client,
                                              ephemeral_public_key_client,
                                              additional_parameter)
        return response

    @keyword("Routine Control By Name")
    def routine_control_by_name(self, routine_name, data = None):
        """
        **Description:**
            Sends a request for the RoutineControl service by routine name
        **Parameters:**
            * param ``routine_name`` (required): Name of routine
            * type ``routine_name``: str

            * param ``control_type`` (required): The service subfunction
            * type ``control_type`` int
            * valid ``control_type``
                - startRoutine          = 1
                - stopRoutine           = 2
                - requestRoutineResults = 3

            * param ``data`` (optional): Optional additional data to give to the server
            * type ``data`` bytes
        """
        diag_services = self.diag_service_db.get_data_by_name([routine_name])
        control_type = diag_services[0].request.parameters[1].coded_value
        if control_type != 1 and control_type != 2:
            control_type = 3
        routine_id = diag_services[0].request.parameters[2].coded_value
        
        response = self.routine_control(routine_id, control_type, data)
        return response

    @keyword("Read Data By Name")
    def read_data_by_name(self, service_name_list = [], parameters = None):
        """
        **Description:**
            Get diagnostic service list by list of service name
        **Parameters:**
            * param ``service_name_list``: list of service name
            * type ``service_name_list``: list[str]

            * param ``parameters``: parameter list
            * type ``parameters``: list[]
        """
        diag_service_list = []
        data_id_list = []

        diag_service_list = self.diag_service_db.get_data_by_name(service_name_list)
        for diag_service in diag_service_list:
            diag_service_request_list = []
            data_id = diag_service.request.parameters[1].coded_value
            data_id_list.append(data_id)
        response = self.read_data_by_identifier(data_id_list)
        return response

    @keyword("Get encoded request message")
    def get_encoded_request_message(self, diag_service_list, parameters=None):
        """
            **Description:**
                Get diagnostic service encoded request list (hex value)
            **Parameters:**
                * param ``diag_service_list``: Diagnostic service list
                * type ``diag_service_list``: []

                * param ``parameters``: parameter list
                * type ``parameters``: list[]
        """
        uds_list = []
        uds_list - self.diag_service_db.get_encoded_request_message(diag_service_list, parameters)
        return uds_list
