from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan import CommunicationType, DynamicDidDefinition, IOMasks, IOValues, MemoryLocation
from udsoncan.client import Client
from udsoncan.Response import Response
from typing import Optional, Union, Dict, List, Any, cast
from udsoncan.common.Filesize import Filesize
from udsoncan.common.Baudrate import Baudrate
from udsoncan.common.DataFormatIdentifier import DataFormatIdentifier
from udsoncan.common.dtc import Dtc
from .DiagnosticServices import DiagnosticServices
from udsoncan.configs import default_client_config
from udsoncan import latest_standard
from typing import cast
from udsoncan.typing import ClientConfig
from doipclient import DoIPClient, constants, messages
from udsoncan.connections import PythonIsoTpConnection
import udsoncan

class UDSKeywords:
    def __init__(self):
        self.connector = None
        self.name = None
        self.uds_connector = None
        self.diag_service_db = None
        self.client = None
        self.config = default_client_config
        self.config['data_identifiers'] = {
            'default' : '>H',                       # Default codec is a struct.pack/unpack string. 16bits little endian
            # 0xF190 : udsoncan.AsciiCodec(15)      # Codec that read ASCII string. We must tell the length of the string
            # 0x6330 : DidCodec(diag_service)       # See `get_did_codec` method for more info
        }

    @keyword("Connect UDS Connector")
    def connect_uds_connector(self, name=None, config=default_client_config, close_connection=False):
        self.name = name
        self.diag_service_db = None
        self.config = config
        self.uds_connector = DoIPClientUDSConnector(self.connector, self.name, close_connection)
        self.client = Client(self.uds_connector, self.config)

    @keyword("Create UDS Connector")
    def create_uds_connector(self, name="doip", **kwargs):
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

    * param ``tcp_port`` (optional): The TCP port used for unsecured data communication (default is **TCP_DATA_UNSECURED**).
    * type ``tcp_port``: int

    * param ``udp_port`` (optional): The UDP port used for ECU discovery (default is **UDP_DISCOVERY**).
    * type ``udp_port``: int

    * param ``activation_type`` (optional): The type of activation, which can be the default value (ActivationTypeDefault) or a specific value based on application-specific settings.
    * type ``activation_type``: RoutingActivationRequest.ActivationType,

    * param ``protocol_version`` (optional): The version of the protocol used for the connection (default is 0x02).
    * type ``protocol_version``: int

    * param ``client_logical_address`` (optional): The logical address that this DoIP client will use to identify itself. Per the spec,
            this should be 0x0E00 to 0x0FFF. Can typically be left as default.
    * type ``client_logical_address``: int

    * param ``client_ip_address`` (optional): If specified, attempts to bind to this IP as the source for both UDP and TCP communication.
            Useful if you have multiple network adapters. Can be an IPv4 or IPv6 address just like `ecu_ip_address`, though
            the type should match.
    * type ``client_ip_address``: str

    * param ``use_secure`` (optional): Enables TLS. If set to True, a default SSL context is used. For more control, a preconfigured
            SSL context can be passed directly. Untested. Should be combined with changing tcp_port to 3496.
    * type ``use_secure``: Union[bool,ssl.SSLContext]

    * param ``auto_reconnect_tcp`` (optional): Attempt to automatically reconnect TCP sockets that were closed by peer

    * type ``auto_reconnect_tcp``: bool

        """
        if name.lower() == "doip":
            # Define required parameters
            required_params = ['ecu_ip_address', 'ecu_logical_address']

            # Check for missing required parameters and raise an error if any are missing
            missing_params = [param for param in required_params if param not in kwargs]
            if missing_params:
                raise ValueError(f"Missing required parameter(s): {', '.join(missing_params)}")

            # Extract parameters from kwargs or set default values if they are optional
            ecu_ip_address = kwargs['ecu_ip_address'].strip()
            ecu_logical_address = kwargs['ecu_logical_address']
            tcp_port = kwargs.get('tcp_port', constants.TCP_DATA_UNSECURED)
            udp_port = kwargs.get('udp_port', constants.UDP_DISCOVERY)
            activation_type = kwargs.get('activation_type', messages.RoutingActivationRequest.ActivationType.Default)
            protocol_version = kwargs.get('protocol_version', 0x02)
            client_logical_address = kwargs.get('client_logical_address', 0x0E00)
            client_ip_address = kwargs.get('client_ip_address', None)
            use_secure = kwargs.get('use_secure', False)
            auto_reconnect_tcp = kwargs.get('auto_reconnect_tcp', True)

            if client_ip_address != None:
                client_ip_address = client_ip_address.strip()

            if isinstance(ecu_logical_address, str):
                ecu_logical_address = int(ecu_logical_address)

            if isinstance(client_logical_address, str):
                client_logical_address = int(client_logical_address)

            if isinstance(activation_type, str):
                activation_type = int(activation_type)

            self.connector = DoIPClient(ecu_ip_address,
                              ecu_logical_address,
                              tcp_port,
                              udp_port,
                              activation_type,
                              protocol_version,
                              client_logical_address,
                              client_ip_address,
                              use_secure,
                              auto_reconnect_tcp)

        elif name.lower() == "can":
            # Define required parameters
            required_params = ['interface', 'txid', 'rxid', 'baudrate']

            # Check for missing required parameters and raise an error if any are missing
            missing_params = [param for param in required_params if param not in kwargs]

            if missing_params:
                raise ValueError(f"Missing required parameter(s): {', '.join(missing_params)}")

            # Extract parameters from kwargs or set default values if they are optional
            interface = kwargs['interface_name']
            txid = int(kwargs['txid'], 16)
            rxid = int(kwargs['rxid'], 16)
            baudrate = kwargs['baudrate']

            self.connector = PythonIsoTpConnection(interface,
                                                   txid,
                                                   rxid,
                                                   baudrate)


    @keyword("Load PDX")
    def load_pdx(self, pdx_file, variant):
        """
**Description:**
    Load PDX
**Parameters:**
    * param ``pdx_file``: pdx file path
    * type ``pdx_file``: st

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

    @keyword("Validate response content")
    def validate_content_response(self, response, expected_data=None):
        """
**Description:**
    Validates the content of a UDS response
**Parameters:**
    * param `response`: The UDS response object to validate.
    * type `response`: udsoncan.Response<Response>

    * param `expected_data`: The expected data (optional) to be matched within the response.
    * type `expected_data`: byte
        """
        if response is None:
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
    * param `exception_on_negative_response`:
      When set to True, the client will raise a NegativeResponseException when the server responds with a negative response.
      When set to False, the returned Response will have its property positive set to False
    * type `exception_on_negative_response`: bool

    * param `exception_on_invalid_response`:
      When set to True, the client will raise a InvalidResponseException when the underlying service interpret_response raises the same exception.
      When set to False, the returned Response will have its property valid set to False
    * type `exception_on_invalid_response`: bool

    * param `exception_on_unexpected_response`:
      When set to True, the client will raise a UnexpectedResponseException when the server returns a response that is not expected.
      For instance, a response for a different service or when the subfunction echo doesn't match the request.
      When set to False, the returned Response will have its property unexpected set to True in the same case.
    * type `exception_on_unexpected_response`: bool

    * param `security_algo`:
      The implementation of the security algorithm necessary for the SecurityAccess service.
    * type `security_algo`:
      This function must have the following signatures:

      SomeAlgorithm(level, seed, params)

          Parameters:

              - level (int) - The requested security level.
              - seed (bytes) - The seed given by the server
              - params - The value provided by the client configuration security_algo_params

          Returns: The security key
          Return type: byte
    * param `security_algo_params`:
      This value will be given to the security algorithm defined in config['security_algo'].
    * type `security_algo_params`: object | dict

    * param `data_identifiers`:
      This configuration is a dictionary that is mapping an integer (the data identifier) with a DidCodec.
      These codecs will be used to convert values to byte payload and vice-versa when sending/receiving data for a service that needs a DID, i.e

          - ReadDataByIdentifier
          - ReadDataByName
          - WriteDataByIdentifier
          - ReadDTCInformation with subfunction reportDTCSnapshotRecordByDTCNumber and reportDTCSnapshotRecordByRecordNumber
    * type `data_identifiers`: dict
      Possible configuration values are
          - string : The string will be used as a pack/unpack string when processing the data
          - DidCodec (class or instance) : The encode/decode method will be used to process the data

    * param `input_output`:
      This configuration is a dictionary that is mapping an integer (the IO data identifier) with a DidCodec specifically for the InputOutputControlByIdentifier service.
      Just like config[data_identifers], these codecs will be used to convert values to byte payload and vice-versa when sending/receiving data.
      Since InputOutputControlByIdentifier supports composite codecs, it is possible to provide a sub-dictionary as a codec specifying the bitmasks.
    * type `input_output`: dict
      Possible configuration values are:
          - string : The string will be used as a pack/unpack string when processing the data
          - DidCodec (class or instance) : The encode/decode method will be used to process the data
          - dict : The dictionary entry indicates a composite DID. Three subkeys must be defined as:
                  - codec : The codec, a string or a DidCodec class/instance
                  - mask : A dictionary mapping the mask name with a bit
                  - mask_size : An integer indicating on how many bytes must the mask be encode

      The special dictionnary key `default` can be used to specify a fallback codec if an operation is done on a codec not part of the configuration.
      Useful for scanning a range of DID

    * param `tolerate_zero_padding`:
      This value will be passed to the services `interpret_response` when the parameter is supported as in ReadDataByIdentifier, ReadDTCInformation.
      It has to ignore trailing zeros in the response data to avoid falsely raising InvalidResponseException if the underlying protocol uses some zero-padding.
    * type `tolerate_zero_padding`: bool

    * param `ignore_all_zero_dtc`
      This value is used with the ReadDTCInformation service when reading DTCs. It will skip any DTC that has an ID of 0x000000.
      If the underlying protocol uses zero-padding, it may generate a valid response data of all zeros. This parameter is different from config['tolerate_zero_padding'].
      Read `https://udsoncan.readthedocs.io/en/latest/udsoncan/client.html#configuration` for more info.
    * type `ignore_all_zero_dtc`: bool

    * param `server_address_format`:
      The MemoryLocation server_address_format is the value to use when none is specified explicitly for methods expecting a parameter of type MemoryLocation.
    * type `server_address_format`: int

    * param `server_memorysize_format`:
      The MemoryLocation server_memorysize_format is the value to use when none is specified explicitly for methods expecting a parameter of type MemoryLocation
    * type `server_memorysize_format`: int

    * param `extended_data_size`:
      This is the description of all the DTC extended data record sizes.
      This value is used to decode the server response when requesting a DTC extended data.

      The value must be specified as follows
        |  config['extended_data_size'] = {
        |      0x123456 : 45, # Extended data for DTC 0x123456 is 45 bytes long
        |      0x123457 : 23 # Extended data for DTC 0x123457 is 23 bytes long
        |  }

    * type `extended_data_size`: dict[int] = int

    * param `dtc_snapshot_did_size`:
      The number of bytes used to encode a data identifier specifically for ReadDTCInformation subfunction reportDTCSnapshotRecordByDTCNumber and reportDTCSnapshotRecordByRecordNumber.
      The UDS standard does not specify a DID size although all other services expect a DID encoded over 2 bytes (16 bits). Default value of 2
    * type `dtc_snapshot_did_size`: int

    * param `standard_version`:
      The standard version to use, valid values are : 2006, 2013, 2020. Default value is 2020
    * type `standard_version`: int
    * param `request_timeout`:
      Maximum amount of time in seconds to wait for a response of any kind, positive or negative, after sending a request.
      After this time is elapsed, a TimeoutException will be raised regardless of other timeouts value or previous client responses.
      In particular even if the server requests that the client wait, by returning response requestCorrectlyReceived-ResponsePending (0x78), this timeout will still trigger.
      If you wish to disable this behaviour and have your server wait for as long as it takes for the ECU to finish whatever activity you have requested, set this value to None.
      Default value of 5
    * type `request_timeout`: float
    * param `p2_timeout`:
      Maximum amount of time in seconds to wait for a first response (positive, negative, or NRC 0x78).
      After this time is elapsed, a TimeoutException will be raised if no response has been received.
      See ISO 14229-2:2013 (UDS Session Layer Services) for more details. Default value of 1
    * type `p2_timeout`: float
    * param `p2_star_timeout`:
      Maximum amount of time in seconds to wait for a response (positive, negative, or NRC0x78) after the reception of a negative response with code 0x78 (requestCorrectlyReceived-ResponsePending).
      After this time is elapsed, a TimeoutException will be raised if no response has been received.
      See ISO 14229-2:2013 (UDS Session Layer Services) for more details. Default value of 5
    * type `p2_star_timeout`: float
    * param `use_server_timing`:
      When using 2013 standard or above, the server is required to provide its P2 and P2* timing values with a DiagnosticSessionControl request. By setting this parameter to True, the value received from the server will be used.
      When False, these timing values will be ignored and local configuration timing will be used. Note that no timeout value can exceed the config['request_timeout'] as it is meant to avoid the client from hanging for too long.
      This parameter has no effect when config['standard_version'] is set to 2006.
      Default value is True
    * type `use_server_timing`: bool
        """
        self.config = cast(ClientConfig, {
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

    * type ``access_type`` in

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
    * param ``group``: The group of DTCs to clear. It may refer to Powertrain DTCs, Chassis DTCs, etc. Values are defined by the ECU manufacturer except for two specific value

        - ``0x000000`` : Emissions-related systems
        - ``0xFFFFFF`` : All DTCs

    * type ``group``: in

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
    * param ``control_type`` (required): The action to request such as enabling or disabling some messages. This value can also be ECU manufacturer-specifi

        - enableRxAndTx                                      = 0
        - enableRxAndDisableTx                               = 1
        - disableRxAndEnableTx                               = 2
        - disableRxAndTx                                     = 3
        - enableRxAndDisableTxWithEnhancedAddressInformation = 4
        - enableRxAndTxWithEnhancedAddressInformation        = 5

    * type ``control_type``: int

    * param ``communication_type`` (required): Indicates what section of the network and the type of message that should be affected by the command. Refer to CommunicationType<CommunicationType for more details. If an `integer` or a `bytes` is given, the value will be decoded to create the required CommunicationType<CommunicationType object
    * type communication_type: CommunicationType<CommunicationType>, bytes, int.

    * param ``node_id`` (optional):

    DTC memory identifier (nodeIdentificationNumber).
    This value is user defined and introduced in 2013 version of ISO-14229-1.
    Possible only when control type is ``enableRxAndDisableTxWithEnhancedAddressInformation`` or ``enableRxAndTxWithEnhancedAddressInformation``
    Only added to the request payload when different from None.

    Default : None

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
        - systemSupplierSpecific      = (0x60, 0x7E)  # To be able to print textual name for logging only

    * type ``setting_type``: in

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
        If a ``MemoryLocation<MemoryLocation>`` object is given, definition will automatically be by memory address
    * type ``did_definition``: ``DynamicDidDefinition<DynamicDidDefinition>`` or ``MemoryLocation<MemoryLocation``
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
    * type ``did``: int

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
    Requests a value associated with a data identifier (DID) through the ReadDataByIdentifier service.
**Parameters:**
    See ``an example<reading_a_did>`` about how to read a DID

    * param data_id_list: The list of DID to be read
    * type data_id_list: int | list[int]
        """
        SID_RQ = 34 # The request id of read data by identifier

        # Get the did_codec from pdx file
        did_codec = self.diag_service_db.get_did_codec(SID_RQ)

        # Set it to uds config
        self.config['data_identifiers'].update(did_codec)
        self.set_config()

        response = self.client.read_data_by_identifier(data_id_list)
        logger.info(response.service_data.values[data_id_list[0]])
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
**Parameters:**
    * param ``memory_location`` (required): The address and size of the memory block to be written.
    * type ``memory_location``: MemoryLocation <MemoryLocation>

    * param ``dfi`` (optional):

    Optional defining the compression and encryption scheme of the data.
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
    Informs the server that the client wants to initiate an upload from the server to the client by sending a RequestUpload<RequestUpload service request.
**Parameters:**
    * param ``memory_location`` (required): The address and size of the memory block to be written.
    * type ``memory_location``: MemoryLocation <MemoryLocation>

    * param dfi (optional): Optional defining the compression and encryption scheme of the data.

        If not specified, the default value of 00 will be used, specifying no encryption and no compression

    * type dfi: DataFormatIdentifier

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

    If filesize is an object of type Filesize, the uncompressed size and compressed size will be encoded on
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

    * param ``algorithm_indicator`` (optional):

    Optional Indicates the algorithm used in the generating and verifying Proof of Ownership (POWN),
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

    Valid ``control_type``

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
