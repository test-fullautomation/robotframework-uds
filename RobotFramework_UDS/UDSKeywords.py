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

class UDSDeviceManager:
    def __init__(self):
        self.uds_device = {}
        self.uds_device_available = []

    def is_device_exist(self, name):
        if name in self.uds_device:
            return True
        return False

class UDSDevice:
    def __init__(self):
        self.name = None
        self.diag_service_db = None
        self.config = None
        self.uds_connector = None
        self.client = None
        self.connector = None
        self.available = False

class UDSKeywords:
    def __init__(self):
        self.uds_manager = UDSDeviceManager()

    def __device_check(self, device_name):
        if self.uds_manager.is_device_exist(device_name):
            if self.uds_manager.uds_device[device_name].available:
                uds_device = self.uds_manager.uds_device[device_name]
                return uds_device
            else:
                raise ValueError(f"Device with name '{device_name}' is not available. Please use keyword \"Connect UDS Connector\" to connect.")
        else:
            raise ValueError(f"Device with name '{device_name}' does not exists. Please use keyword \"Create UDS Connector\" to create a new one.")

    @keyword("Connect UDS Connector")
    def connect_uds_connector(self, device_name="default", config=default_client_config, close_connection=False):
        if self.uds_manager.is_device_exist(device_name):
            if self.uds_manager.uds_device[device_name].available:
                logger.info(f"Device {device_name} is available to be use.")
            else:
                self.uds_manager.uds_device[device_name].config = config
                self.uds_manager.uds_device[device_name].uds_connector = DoIPClientUDSConnector(self.uds_manager.uds_device[device_name].connector, device_name, close_connection)
                self.uds_manager.uds_device[device_name].client = Client(self.uds_manager.uds_device[device_name].uds_connector, self.uds_manager.uds_device[device_name].config)
                self.uds_manager.uds_device[device_name].available = True
        else:
            raise ValueError(f"Device with name '{device_name}' does not exists. Please use keyword \"Create UDS Connector\" to create a new one.")

    @keyword("Create UDS Connector")
    def create_uds_connector(self, device_name="default", comunication_name="doip", **kwargs):
        """
**Description:**
    Create a connection to establish
**Parameters:**
    * param ``comunication_name``: Name of communication

        - doip: Establish a doip connection to an (ECU)
    * type ``comunication_name``: str

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
        if self.uds_manager.is_device_exist(device_name):
            raise ValueError(f"Device with name '{device_name}' already exists.")
        connector = None
        if comunication_name.lower() == "doip":
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

            connector = DoIPClient(ecu_ip_address,
                              ecu_logical_address,
                              tcp_port,
                              udp_port,
                              activation_type,
                              protocol_version,
                              client_logical_address,
                              client_ip_address,
                              use_secure,
                              auto_reconnect_tcp)

        elif comunication_name.lower() == "can":
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

            connector = PythonIsoTpConnection(interface,
                                                   txid,
                                                   rxid,
                                                   baudrate)

        uds_device = UDSDevice()
        uds_device.name = device_name
        uds_device.connector = connector
        self.uds_manager.uds_device[device_name] = uds_device

    @keyword("Load PDX")
    def load_pdx(self, pdx_file, variant, device_name="default"):
        """
Load PDX
**Arguments:**
* ``pdx_file``

  / *Type*: str /

  PDX file path

* ``variant``

  / *Type*: str /
        """
        self.__device_check(device_name)
        self.uds_manager.uds_device[device_name].diag_service_db = DiagnosticServices(pdx_file, variant)

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
    def set_config(self, config, device_name="default"):
        '''
This method sets the UDS config.

**Arguments:**

* No specific arguments for this method.

**Returns:**

* ``config``

  / *Type*: Configuration /

  Returns the new UDS configuration created by `create_configure` or the default config if none is provided.
        '''
        uds_device = self.__device_check(device_name)
        uds_device.client.set_configs(config)

    @keyword("Open uds connection")
    def connect(self, device_name="default"):
        '''
Opens a UDS connection.

**Arguments:**

* No specific arguments for this method.
        '''
        uds_device = self.__device_check(device_name)
        uds_device.uds_connector.open()

    @keyword("Close UDS Connection")
    def disconnect(self, device_name="default"):
        '''
Closes a UDS connection.

**Arguments:**

* No specific arguments for this method.
        '''
        uds_device = self.__device_check(device_name)
        uds_device.uds_connector.close()

    @keyword("Access Timing Parameter")
    def access_timing_parameter(self, access_type: int, timing_param_record: Optional[bytes] = None, device_name="default"):
        """
Sends a generic request for AccessTimingParameter service.

**Arguments:**

* ``access_type``

  / *Condition*: required / *Type*: int /

  The service subfunction:

  - readExtendedTimingParameterSet      = 1
  - setTimingParametersToDefaultValues  = 2
  - readCurrentlyActiveTimingParameters = 3
  - setTimingParametersToGivenValues    = 4

* ``timing_param_record``

  / *Condition*: optional / *Type*: bytes /

  The parameters data. Specific to each ECU.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the AccessTimingParameter service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.access_timing_parameter(access_type, timing_param_record)
        return response

    @keyword("Clear Dianostic Information")
    def clear_dianostic_infomation(self, group: int = 0xFFFFFF, memory_selection: Optional[int] = None, device_name="default"):
        """
Requests the server to clear its active Diagnostic Trouble Codes.

**Arguments:**

* ``group``

  / *Type*: int /

  The group of DTCs to clear. It may refer to Powertrain DTCs, Chassis DTCs, etc. Values are defined by the ECU manufacturer except for two specific values:

  - ``0x000000`` : Emissions-related systems
  - ``0xFFFFFF`` : All DTCs

* ``memory_selection``

  / *Condition*: optional / *Type*: int /

  MemorySelection byte (0-0xFF). This value is user-defined and introduced in the 2020 version of ISO-14229-1. Only added to the request payload when different from None. Default: None.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the server after attempting to clear the active Diagnostic Trouble Codes.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.clear_dtc(group, memory_selection)
        return response

    @keyword("Communication Control")
    def communication_control(self, control_type: int, communication_type: Union[int, bytes, CommunicationType], node_id: Optional[int] = None, device_name="default"):
        """
Switches the transmission or reception of certain messages on/off with CommunicationControl service.

**Arguments:**

* ``control_type``

  / *Condition*: required / *Type*: int /

  The action to request such as enabling or disabling some messages. This value can also be ECU manufacturer-specific:

  - enableRxAndTx                                      = 0
  - enableRxAndDisableTx                               = 1
  - disableRxAndEnableTx                               = 2
  - disableRxAndTx                                     = 3
  - enableRxAndDisableTxWithEnhancedAddressInformation = 4
  - enableRxAndTxWithEnhancedAddressInformation        = 5

* ``communication_type``

  / *Condition*: required / *Type*: CommunicationType<CommunicationType>, bytes, int /

  Indicates what section of the network and the type of message that should be affected by the command. Refer to CommunicationType<CommunicationType> for more details. If an `integer` or `bytes` is given, the value will be decoded to create the required CommunicationType<CommunicationType> object.

* ``node_id``

  / *Condition*: optional / *Type*: int /

  DTC memory identifier (nodeIdentificationNumber). This value is user-defined and introduced in the 2013 version of ISO-14229-1. Possible only when control type is ``enableRxAndDisableTxWithEnhancedAddressInformation`` or ``enableRxAndTxWithEnhancedAddressInformation``. Only added to the request payload when different from None. Default: None.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the CommunicationControl service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.communication_control(control_type, communication_type, node_id)
        return response

    @keyword("Control DTC Setting")
    def control_dtc_setting(self, setting_type: int, data: Optional[bytes] = None, device_name="default"):
        """
Controls some settings related to the Diagnostic Trouble Codes by sending a ControlDTCSetting service request.
It can enable/disable some DTCs or perform some ECU-specific configuration.

**Arguments:**

* ``setting_type``

  / *Condition*: required / *Type*: int /

  Allowed values are from 0 to 0x7F:

  - on  = 1
  - off = 2
  - vehicleManufacturerSpecific = (0x40, 0x5F)  # For logging purposes only.
  - systemSupplierSpecific      = (0x60, 0x7E)  # For logging purposes only.

* ``data``

  / *Condition*: optional / *Type*: bytes /

  Optional additional data sent with the request called `DTCSettingControlOptionRecord`.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the ControlDTCSetting service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.control_dtc_setting(setting_type, data)
        return response

    @keyword("Diagnostic Session Control")
    def diagnostic_session_control(self, session_type, device_name="default"):
        """
Requests the server to change the diagnostic session with a DiagnosticSessionControl service request.

**Arguments:**

* ``newsession``

  / *Condition*: required / *Type*: int /

  The session to try to switch:

  - defaultSession                = 1
  - programmingSession            = 2
  - extendedDiagnosticSession     = 3
  - safetySystemDiagnosticSession = 4

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the DiagnosticSessionControl service request.
        """
        uds_device = self.__device_check(device_name)
        if isinstance(session_type, str):
            session_type = int(session_type)
        response = uds_device.client.change_session(session_type)
        return response

    @keyword("Dynamically Define Data Identifier")
    def dynamically_define_did(self, did: int, did_definition: Union[DynamicDidDefinition, MemoryLocation], device_name="default"):
        """
Defines a dynamically defined DID.

**Arguments:**

* ``did``

  / *Type*: int /

  The data identifier to define.

* ``did_definition``

  / *Type*: DynamicDidDefinition<DynamicDidDefinition> or MemoryLocation<MemoryLocation> /

  The definition of the DID. Can be defined by source DID or memory address. If a ``MemoryLocation<MemoryLocation>`` object is given, the definition will automatically be by memory address.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the request to define the dynamically defined DID.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.dynamically_define_did(did, did_definition)
        return response

    @keyword("ECU Reset")
    def ecu_reset(self, reset_type: int, device_name="default"):
        """
Requests the server to execute a reset sequence through the ECUReset service.

**Arguments:**

* ``reset_type``

  / *Condition*: required / *Type*: int /

  The type of reset to perform:

  - hardReset                 = 1
  - keyOffOnReset             = 2
  - softReset                 = 3
  - enableRapidPowerShutDown  = 4
  - disableRapidPowerShutDown = 5

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the ECUReset service request.
        """
        uds_device = self.__device_check(device_name)
        response = None
        if isinstance(reset_type, str):
            reset_type = int(reset_type)

        try:
            response = uds_device.client.ecu_reset(reset_type)
        except Exception as e:
            BuiltIn().fail(f"Fail to send a ECU Reset request. Reason: {e}")
        return response

    @keyword("Input Output Control By Identifier")
    def io_control(self,
                   did: int,
                   control_param: Optional[int] = None,
                   values: Optional[Union[List[Any], Dict[str, Any], IOValues]] = None,
                   masks: Optional[Union[List[str], Dict[str, bool], IOMasks, bool]] = None,
                   device_name="default"):
        """
Substitutes the value of an input signal or overrides the state of an output by sending an InputOutputControlByIdentifier service request.

**Arguments:**

* ``did``

  / *Condition*: required / *Type*: int /

  Data identifier to represent the IO.

* ``control_param``

  / *Condition*: optional / *Type*: int /

  Control parameters:

  - returnControlToECU = 0
  - resetToDefault = 1
  - freezeCurrentState = 2
  - shortTermAdjustment = 3

* ``values``

  / *Condition*: optional / *Type*: list, dict, IOValues<IOValues> /

  Optional values to send to the server. This parameter will be given to DidCodec<DidCodec>.encode() method. It can be:

  - A list for positional arguments
  - A dict for named arguments
  - An instance of IOValues<IOValues> for mixed arguments

* ``masks``

  / *Condition*: optional / *Type*: list, dict, IOMask<IOMask>, bool /

  Optional mask record for composite values. The mask definition must be included in ``config['input_output']``. It can be:

  - A list naming the bit mask to set
  - A dict with the mask name as a key and a boolean setting or clearing the mask as the value
  - An instance of IOMask<IOMask>
  - A boolean value to set all masks to the same value.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the InputOutputControlByIdentifier service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.io_control(did, control_param, values, masks)
        return response

    @keyword("Link Control")
    def link_control(self, control_type: int, baudrate: Optional[Baudrate] = None, device_name="default"):
        """
Controls the communication baudrate by sending a LinkControl service request.

**Arguments:**

* ``control_type``

  / *Condition*: required / *Type*: int /

  Allowed values are from 0 to 0xFF:

  - verifyBaudrateTransitionWithFixedBaudrate    = 1
  - verifyBaudrateTransitionWithSpecificBaudrate = 2
  - transitionBaudrate                           = 3

* ``baudrate``

  / *Condition*: required / *Type*: Baudrate<Baudrate> /

  Required baudrate value when ``control_type`` is either ``verifyBaudrateTransitionWithFixedBaudrate`` (1) or ``verifyBaudrateTransitionWithSpecificBaudrate`` (2).

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the LinkControl service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.link_control(control_type, baudrate)
        return response

    @keyword("Read Data By Identifier")
    def read_data_by_identifier(self, data_id_list: Union[int, List[int]], device_name="default"):
        """
Requests a value associated with a data identifier (DID) through the ReadDataByIdentifier service.

**Arguments:**

* ``data_id_list``

  / *Type*: int | list[int] /

  The list of DIDs to be read.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the ReadDataByIdentifier service request.
        """
        uds_device = self.__device_check(device_name)
        SID_RQ = 34 # The request id of read data by identifier

        # Get the did_codec from pdx file
        did_codec = uds_device.diag_service_db.get_did_codec(SID_RQ)

        # Set it to uds config
        uds_device.config['data_identifiers'].update(did_codec)
        self.set_config(uds_device.config, device_name)

        response = uds_device.client.read_data_by_identifier(data_id_list)
        for i in range(0, len(data_id_list)):
            logger.info(response.service_data.values[data_id_list[i]])
        return response.service_data.values

    @keyword("Read DTC Information")
    def read_dtc_information(self,
                             subfunction: int,
                             status_mask: Optional[int] = None,
                             severity_mask: Optional[int] = None,
                             dtc: Optional[Union[int, Dtc]] = None,
                             snapshot_record_number: Optional[int] = None,
                             extended_data_record_number: Optional[int] = None,
                             extended_data_size: Optional[int] = None,
                             memory_selection: Optional[int] = None,
                             device_name="default"):
        """
Performs a ReadDiagnosticInformation service request.

**Arguments:**

* ``subfunction``

  / *Condition*: required / *Type*: int /

  The subfunction for the ReadDiagnosticInformation service.

* ``status_mask``

  / *Condition*: optional / *Type*: int /

  Status mask to filter the diagnostic information.

* ``severity_mask``

  / *Condition*: optional / *Type*: int /

  Severity mask to filter the diagnostic information.

* ``dtc``

  / *Condition*: optional / *Type*: int | Dtc /

  The Diagnostic Trouble Code to query. Can be an integer or a Dtc object.

* ``snapshot_record_number``

  / *Condition*: optional / *Type*: int /

  Snapshot record number to specify the snapshot to read.

* ``extended_data_record_number``

  / *Condition*: optional / *Type*: int /

  Extended data record number to specify the extended data to read.

* ``extended_data_size``

  / *Condition*: optional / *Type*: int /

  Size of the extended data to read.

* ``memory_selection``

  / *Condition*: optional / *Type*: int /

  Memory selection to specify the memory to be accessed.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the ReadDiagnosticInformation service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.read_dtc_information(subfunction, status_mask, severity_mask, dtc, snapshot_record_number,extended_data_record_number, extended_data_size, memory_selection)
        return response

    @keyword("Read Memory By Address")
    def read_memory_by_address(self, memory_location: MemoryLocation, device_name="default"):
        """
Reads a block of memory from the server by sending a ReadMemoryByAddress service request.

**Arguments:**

* ``memory_location``

  / *Condition*: required / *Type*: MemoryLocation<MemoryLocation> /

  The address and the size of the memory block to read.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the ReadMemoryByAddress service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.read_memory_by_address(memory_location)
        return response

    @keyword("Request Download")
    def request_download(self, memory_location: MemoryLocation, dfi: Optional[DataFormatIdentifier] = None, device_name="default"):
        """
Informs the server that the client wants to initiate a download from the client to the server by sending a RequestDownload service request.

**Arguments:**

* ``memory_location``

  / *Condition*: required / *Type*: MemoryLocation<MemoryLocation> /

  The address and size of the memory block to be written.

* ``dfi``

  / *Condition*: optional / *Type*: DataFormatIdentifier<DataFormatIdentifier> /

  Optional defining the compression and encryption scheme of the data. If not specified, the default value of 00 will be used, specifying no encryption and no compression.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the RequestDownload service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.request_download(memory_location, dfi)
        return response
    
    @keyword("Request Transfer Exit")
    def request_transfer_exit(self, data: Optional[bytes] = None, device_name="default"):
        """
Informs the server that the client wants to stop the data transfer by sending a RequestTransferExit service request.

**Arguments:**

* ``data``

  / *Condition*: optional / *Type*: bytes /

  Optional additional data to send to the server.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the RequestTransferExit service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.request_transfer_exit(data)
        return response

    @keyword("Request Upload")
    def request_upload(self, memory_location: MemoryLocation, dfi: Optional[DataFormatIdentifier] = None, device_name="default"):
        """
Informs the server that the client wants to initiate an upload from the server to the client by sending a RequestUpload service request.

**Arguments:**

* ``memory_location``

  / *Condition*: required / *Type*: MemoryLocation<MemoryLocation> /

  The address and size of the memory block to be written.

* ``dfi``

  / *Condition*: optional / *Type*: DataFormatIdentifier<DataFormatIdentifier> /

  Optional defining the compression and encryption scheme of the data. If not specified, the default value of 00 will be used, specifying no encryption and no compression.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the RequestUpload service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.request_upload(memory_location, dfi)
        return response

    @keyword("Routine Control")
    def routine_control(self, routine_id: int, control_type: int, data: Optional[bytes] = None, device_name="default"):
        """
Sends a generic request for the RoutineControl service.

**Arguments:**

* ``routine_id``

  / *Condition*: required / *Type*: int /

  The 16-bit numerical ID of the routine.

* ``control_type``

  / *Condition*: required / *Type*: int /

  The service subfunction. Valid values are:

  - startRoutine          = 1
  - stopRoutine           = 2
  - requestRoutineResults = 3

* ``data``

  / *Condition*: optional / *Type*: bytes /

  Optional additional data to give to the server.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the RoutineControl service request.
        """
        uds_device = self.__device_check(device_name)
        response = None
        try:
            response = uds_device.client.routine_control(routine_id, control_type, data)
        except Exception as e:
            BuiltIn().fail(f"Fail to send a Routine Control request. Reason: {e}")
        return response

    def security_access(self, level, seed_params=bytes(), device_name="default"):
        """
Successively calls request_seed and send_key to unlock a security level with the SecurityAccess service.
The key computation is done by calling config['security_algo'].

**Arguments:**

* ``level``

  / *Condition*: required / *Type*: int /

  The level to unlock. Can be the odd or even variant of it.

* ``seed_params``

  / *Condition*: optional / *Type*: bytes /

  Optional data to attach to the RequestSeed request (securityAccessDataRecord).

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the SecurityAccess service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.unlock_security_access(level, seed_params)
        return response

    @keyword("Tester Present")
    def tester_present(self, device_name="default"):
        """
Sends a TesterPresent request to keep the session active.

**Arguments:**

* No specific arguments for this method.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the TesterPresent request.
        """
        uds_device = self.__device_check(device_name)
        response = None
        try:
            response = uds_device.client.tester_present()
        except Exception as e:
            BuiltIn().fail(f"Fail to send a TesterPresent request. Reason: {e}")
        return response

    @keyword("Transfer Data")
    def transfer_data(self, sequence_number: int, data: Optional[bytes] = None, device_name="default"):
        """
Transfers a block of data to/from the client to/from the server by sending a TransferData service request and returning the server response.

**Arguments:**

* ``sequence_number``

  / *Condition*: required / *Type*: int /

  Corresponds to an 8-bit counter that should increment for each new block transferred. Allowed values are from 0 to 0xFF.

* ``data``

  / *Condition*: optional / *Type*: bytes /

  Optional additional data to send to the server.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the TransferData service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.transfer_data(sequence_number, data)
        return response
    
    @keyword("Write Data By Identifier")
    def write_data_by_identifier(self, did: int, value: Any, device_name="default"):
        """
Requests to write a value associated with a data identifier (DID) through the WriteDataByIdentifier service.

**Arguments:**

* ``did``

  / *Condition*: required / *Type*: int /

  The DID to write its value.

* ``value``

  / *Condition*: required / *Type*: dict /

  Value given to the DidCodec.encode method. The payload returned by the codec will be sent to the server.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the WriteDataByIdentifier service request.
        """
        logger.info(f"Service DID: {did}")
        uds_device = self.__device_check(device_name)
        SID_RQ = 46 # The request id of write data by identifier

        # Get the did_codec from pdx file
        did_codec = uds_device.diag_service_db.get_did_codec(SID_RQ)

        # Set it to uds config
        uds_device.config['data_identifiers'].update(did_codec)
        self.set_config(uds_device.config, device_name)

        response = uds_device.client.write_data_by_identifier(did, value)
        logger.info(f"DID echo: {response.service_data.did_echo}")
        return response

    @keyword("Write Memory By Address")
    def write_memory_by_address(self, memory_location: MemoryLocation, data: bytes, device_name="default"):
        """
Writes a block of memory in the server by sending a WriteMemoryByAddress service request.

**Arguments:**

* ``memory_location``

  / *Condition*: required / *Type*: MemoryLocation<MemoryLocation> /

  The address and the size of the memory block to write.

* ``data``

  / *Condition*: required / *Type*: bytes /

  The data to write into memory.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the WriteMemoryByAddress service request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.write_memory_by_address(memory_location, data)
        return response

    @keyword("Request File Transfer")
    def request_file_transfer(self, 
                              moop: int,
                              path: str = '',
                              dfi: Optional[DataFormatIdentifier] = None,
                              filesize: Optional[Union[int, Filesize]] = None,
                              device_name="default"):

        """
Sends a RequestFileTransfer request
**Arguments:**

* ``moop``

  / *Condition*: required / *Type*: int /

  Mode of operation:
  - AddFile = 1
  - DeleteFile = 2
  - ReplaceFile = 3
  - ReadFile = 4
  - ReadDir = 5
  - ResumeFile = 6

* ``path``

  / *Condition*: required / *Type*: str /

  The path of the file or directory.

* ``dfi``

  / *Condition*: optional / *Type*: DataFormatIdentifier /

  DataFormatIdentifier defining the compression and encryption scheme of the data. Defaults to no compression and no encryption.
  Use for:
  - AddFile = 1
  - ReplaceFile = 3
  - ReadFile = 4
  - ResumeFile = 6

* ``filesize``

  / *Condition*: optional / *Type*: int | Filesize /

  The filesize of the file to write. If `Filesize`, uncompressed and compressed sizes will be encoded as needed.
  Use for:
  - AddFile = 1
  - ReplaceFile = 3
  - ResumeFile = 6

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the file operation.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.request_file_transfer(moop, path, dfi, filesize)
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
                       additional_parameter: Optional[bytes] = None,
                       device_name = "default"):
        """
Sends an Authentication request introduced in 2020 version of ISO-14229-1.
**Arguments:**

* ``authentication_task``

  / *Condition*: required / *Type*: int /

  The authentication task (subfunction) to use:
  - deAuthenticate = 0
  - verifyCertificateUnidirectional = 1
  - verifyCertificateBidirectional = 2
  - proofOfOwnership = 3
  - transmitCertificate = 4
  - requestChallengeForAuthentication = 5
  - verifyProofOfOwnershipUnidirectional = 6
  - verifyProofOfOwnershipBidirectional = 7
  - authenticationConfiguration = 8

* ``communication_configuration``

  / *Condition*: optional / *Type*: int /

  Configuration about security in future diagnostic communication (vehicle manufacturer specific). Allowed values are from 0 to 255.

* ``certificate_client``

  / *Condition*: optional / *Type*: bytes /

  The certificate to verify.

* ``challenge_client``

  / *Condition*: optional / *Type*: bytes /

  Client challenge containing vehicle manufacturer-specific data or a random number.

* ``algorithm_indicator``

  / *Condition*: optional / *Type*: bytes /

  Algorithm used in Proof of Ownership (POWN). This is a 16-byte value containing the BER-encoded OID of the algorithm.

* ``certificate_evaluation_id``

  / *Condition*: optional / *Type*: int /

  Unique ID for evaluating the transmitted certificate. Allowed values are from 0 to 0xFFFF.

* ``certificate_data``

  / *Condition*: optional / *Type*: bytes /

  Certificate data for verification.

* ``proof_of_ownership_client``

  / *Condition*: optional / *Type*: bytes /

  Proof of Ownership of the challenge to be verified by the server.

* ``ephemeral_public_key_client``

  / *Condition*: optional / *Type*: bytes /

  Client's ephemeral public key for Diffie-Hellman key agreement.

* ``additional_parameter``

  / *Condition*: optional / *Type*: bytes /

  Additional parameter provided if required by the server.

**Returns:**

* ``response``

  / *Type*: Response /

  The server's response to the authentication request.
        """
        uds_device = self.__device_check(device_name)
        response = uds_device.client.authentication(authentication_task,
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
    def routine_control_by_name(self, routine_name, data = None, device_name="default"):
        """
Sends a request for the RoutineControl service by routine name.

**Arguments:**

* param ``routine_name`` (required): Name of the routine
  * type ``routine_name``: str

* param ``data`` (optional): Optional additional data to give to the server
  * type ``data``: bytes

**Returns:**

* ``response``  
  / *Type*: Response /  
  The server's response to the RoutineControl request.
        """
        response = None
        uds_device = self.__device_check(device_name)
        diag_services = uds_device.diag_service_db.get_diag_service_by_name([routine_name])
        control_type = diag_services[0].request.parameters[1].coded_value
        if control_type != 1 and control_type != 2:
            control_type = 3
        routine_id = diag_services[0].request.parameters[2].coded_value

        if data is not None:
            # Encoded data to bytes
            if isinstance(data, dict):
                original_encode_message = self.get_encoded_request_message(routine_name, data, device_name)

                # Remove the first 4 bytes since the UDS library automatically adds the first 4 bytes for the service id and control type.
                data = original_encode_message[4:]
                logger.info(f"The encode message send to UDS: {data}")

        response = self.routine_control(routine_id, control_type, data, device_name)

        # Decode response message
        decode_message = self.get_decoded_positive_response_message(routine_name, response.data, device_name)
        logger.info(f"Decode message: {decode_message}")
        return decode_message

    @keyword("Read Data By Name")
    def read_data_by_name(self, service_name_list = [], parameters = None, device_name="default"):
        """
Get diagnostic service list by a list of service names.

**Arguments:**

* param ``service_name_list``: List of service names
  * type ``service_name_list``: list[str]

* param ``parameters``: Parameter list
  * type ``parameters``: list[]

**Returns:**

* ``response``  
  / *Type*: Response /  
  The server's response containing the diagnostic service list.
        """
        uds_device = self.__device_check(device_name)
        diag_service_list = []
        data_id_list = []

        diag_service_list = uds_device.diag_service_db.get_diag_service_by_name(service_name_list)
        did_mapping = {}
        for diag_service in diag_service_list:
            data_id = diag_service.request.parameters[1].coded_value
            data_id_list.append(data_id)
            did_mapping[data_id] = diag_service.short_name
        response = self.read_data_by_identifier(data_id_list, device_name)

        # return service name as key instead of did
        updated_response = {}
        for did, did_res in response.items():
            updated_response[did_mapping[did]] = did_res

        return updated_response

    @keyword("Get Encoded Request Message")
    def get_encoded_request_message(self, service_name, parameters_dict=None, device_name="default"):
        """
Get diagnostic service encoded request (bytes value).

**Arguments:**

* param ``service_name``: Diagnostic service's name
  * type ``service_name``: string

* param ``parameters_dict``: Parameter dictionary
  * type ``parameters_dict``: dict

**Returns:**

* ``encoded_message``  
  / *Type*: bytes /  
  The encoded message in bytes value.
        """
        uds_device = self.__device_check(device_name)
        encoded_message = uds_device.diag_service_db.get_encoded_request_message(service_name, parameters_dict)
        return encoded_message

    @keyword("Get Decoded Response Message")
    def get_decoded_positive_response_message(self, service_name, response_data, device_name="default"):
        """
Get diagnostic service decoded positive response message.

**Arguments:**

* param ``service_name``: Diagnostic service's name
  * type ``service_name``: string

* param ``response_data``: Bytes data from the response
  * type ``parameters_dict``: bytes

* param ``device_name``: Name of the device
  * type ``device_name``: string

**Returns:**

* ``decode_message``
  / *Type*: dict /
  The decode message in dictionary.
        """
        uds_device = self.__device_check(device_name)
        response_message = uds_device.diag_service_db.get_full_positive_response_data(service_name, response_data)
        decode_message = uds_device.diag_service_db.get_decode_response_message(service_name, response_message)
        logger.info(f"Decode message: {decode_message}")
        return decode_message

    @keyword("Write Data By Name")
    def write_data_by_name(self, service_name = None, value = None, device_name = "default"):
        """
Requests to write a value associated with a name of service through the WriteDataByName service.

**Arguments:**

* ``did``

  / *Condition*: required / *Type*: int /

  The DID to write its value.

* ``value``

  / *Condition*: required / *Type*: dict /

  Value given to the DidCodec.encode method. The payload returned by the codec will be sent to the server.

**Returns:**

* ``response``

  / *Type*: Response /

  The response from the WriteDataByIdentifier service request.
        """
        # Verify the device is available
        uds_device = self.__device_check(device_name)

        # Get service from name and verify the service is available
        diag_service_list = uds_device.diag_service_db.get_diag_service_by_name([service_name])
        data_id = diag_service_list[0].request.parameters[1].coded_value

        response = self.write_data_by_identifier(data_id, value, device_name)
        logger.info(f"Write {service_name} successful")
        return response
