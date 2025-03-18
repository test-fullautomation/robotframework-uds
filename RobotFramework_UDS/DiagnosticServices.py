from robot.api import logger
from udsoncan.common.DidCodec import DidCodec
from enum import Enum
import odxtools
import re


class DiagnosticServices:
    def __init__(self, pdx_file, variant):
        self.variant = variant
        self.pdx_file = pdx_file
        # load pdx file
        odxtools.exceptions.strict_mode = False
        self.odx_db = odxtools.load_pdx_file(self.pdx_file)
        odxtools.exceptions.strict_mode = True
        self.ecus = self.odx_db.ecus[self.variant]
        self.diag_layers = self.odx_db.diag_layers[self.variant]
        self.diag_services = self.odx_db.ecus[self.variant].services

    @staticmethod
    def convert_sub_param(odx_param, req_sub_param):
        """
Recursive convert sub parameters in given request to correct data type

**Arguments:**

* ``odx_param``

  / *Condition*: required / *Type*: object /

  The ODX parameters.

* ``req_sub_param``

  / *Condition*: required / *Type*: dict /

  The dictionary of request parameter.

**Returns:**

* ``req_sub_param``

  / *Type*: dict /

  The dictionary of request parameters with the correct data types.
        """
        try:
            org_val = req_sub_param[odx_param.short_name]
            # process byte / byte string data
            if isinstance(org_val, (bytes, bytearray)):
                # convert byte to hex data
                org_val = org_val.hex()
            elif isinstance(org_val, str):
                match = re.match(r"^b['\"](.*)['\"]$", org_val, re.DOTALL)
                if match:
                    #convert byte string to hex data
                    org_val = bytes(match.group(1), "latin1").hex()
        except:
            raise Exception(f"required parameter {odx_param.short_name} is missing")

        if odx_param.dop and hasattr(odx_param.dop, "parameters"):
            for sub_param in odx_param.dop.parameters:
                print(f"{odx_param.short_name} - {sub_param.short_name}")
                req_sub_param[odx_param.short_name][sub_param.short_name] = DiagnosticServices.convert_sub_param(sub_param, org_val)
            return req_sub_param[odx_param.short_name]
        else:
            return odx_param.physical_type.base_data_type.from_string(org_val)

    @staticmethod
    def convert_request_data_type(request_parameters, parameter_dict):
        """
Convert given request parameters (dictionary) to correct data type

**Arguments:**

* ``service``

  / *Condition*: required / *Type*: object /

  The diagnostic service.

* ``parameter_dict``

  / *Condition*: required / *Type*: dict /

  The dictionary of request parameter.

**Returns:**

* ``parameter_dict``

  / *Type*: dict /

  The dictionary of request parameters with the correct data types.
        """
        # request_parameters = service.request.parameters

        # The parameters from the Robot test are strings, so they are converted to the right types.
        for param in request_parameters:
            # Just "VALUE" parameter are required for encode message
            if param.parameter_type == "VALUE":
                converted_param = DiagnosticServices.convert_sub_param(param, parameter_dict)
                parameter_dict[param.short_name] = converted_param

        return parameter_dict

    def get_diag_service_by_name(self, service_name_list):
        """
Retrieve the list of diagnostic services from a PDX file using a specified list of service names.

**Arguments:**

* ``service_name_list``

  / *Condition*: required / *Type*: list /

  The list of service names

**Returns:**

* ``diag_service_list``

  / *Type*: list /

  The list of diagnostic services from a PDX file.
        """
        diag_service_list = []
        for service_name in service_name_list:
            try:
                logger.info(f"Get {service_name} service")
                diag_service = getattr(self.diag_services, service_name)
                diag_service_list.append(diag_service)
            except:
                logger.error(f"Diagnostic services does not contain an item named {service_name}")

        return diag_service_list

    def get_encoded_request_message(self, service_name, parameter_dict, sub_service_name=None):
        """
Retrieve the encode request message from parameters dictionary.

**Arguments:**

* ``service_name``

  / *Condition*: required / *Type*: str /

  The service's names

* ``parameter_dict``

  / *Condition*: required / *Type*: dict /

  The dictionary of request parameter.

**Returns:**

* ``encode_message``

  / *Type*: bytes /

  The encoded message.
        """
        service = getattr(self.diag_services, service_name)
        logger.info(f"Encode {service.short_name} message")
        encode_message = None
        try:
            if not parameter_dict:
                encode_message = service.encode_request()
            else:
                # Convert the parameter data type to the correct type
                if (service.request.parameters[2].parameter_type == 'TABLE-KEY' and
                    service.request.parameters[3].parameter_type == 'TABLE-STRUCT' and
                    sub_service_name):

                    service_params = service.request.parameters[3].table_key.table.table_rows[sub_service_name].structure.parameters
                    request_parameters = self.convert_request_data_type(service_params, parameter_dict)
                    request_parameters = {
                        service.request.parameters[3].short_name: tuple([sub_service_name, request_parameters])
                    }
                else:
                    request_parameters = self.convert_request_data_type(service.request.parameters, parameter_dict)

                encode_message = bytes(service.encode_request(**request_parameters))
                logger.info(f"Full encode message: {encode_message}")
        except Exception as e:
            logger.error(f"Failed to encode {service.short_name} message.")
            raise Exception(f"Reason: {e}")

        return encode_message

    def get_decode_response_message(self, service_name, raw_message: bytes):
        """
Retrieve the encode request message from parameters dictionary.

**Arguments:**

* ``service_name``

  / *Condition*: required / *Type*: str /

  The service's names

* ``raw_message``

  / *Condition*: required / *Type*: bytes /

  The raw message from the response.

**Returns:**

* ``decode_message``

  / *Type*: bytes /

  The decoded message.
        """
        service = getattr(self.diag_services, service_name)
        logger.info(f"Decode {service.short_name} message")
        decode_message = None

        decode_message = service.decode_message(raw_message).param_dict
        return decode_message

    def get_full_positive_response_data(self, service_name, data: bytes):
        """
Retrieve the complete byte data from the response, as the UDS removes the service ID.

**Arguments:**

* ``service_name``

  / *Condition*: required / *Type*: str /

  The service's names

* ``data``

  / *Condition*: required / *Type*: bytes /

  The raw message from the response.

**Returns:**

* ``positive_response_data``

  / *Type*: bytes /

  The complete byte data from the response.
        """
        diag_service = self.get_diag_service_by_name([service_name])[0]
        positive_response_data = bytes.fromhex(hex(diag_service.positive_responses[0].parameters.SID_PR.coded_value).replace('0x','') + data.hex())
        return positive_response_data

    def get_did_codec(self, service_id, sub_services = None):
        """
Retrieves a dictionary of DID codecs for a given diagnostic service ID.

**Arguments:**

* ``service_id``

  / *Condition*: required / *Type*: int /

  The service's did

**Returns:**

* ``did_codec``

  / *Type*: dict /

  A dictionary where the keys are DIDs
        """
        did_codec = {}
        diag_services = self.ecus.service_groups[service_id]
        sub_service_list = None
        for diag_service in diag_services:
            if sub_services != None:
                try:
                    sub_service_list = sub_services[diag_service.short_name]
                except:
                    sub_service_list = None
            did = self.get_param_value_base_on_param_type(diag_service.request.parameters[1], sub_service_list)
            if isinstance(did, int):
                did_codec[did] = PDXCodec(diag_service, did)
            elif isinstance(did, dict):
                for data_id in list(did.keys()):
                    did_codec[data_id] = PDXCodec(diag_service, data_id, did[data_id])

        return did_codec

    @staticmethod
    def get_param_value_base_on_param_type(param, key_list = None):
        dict_value = {}
        try:
            parameter_type = param.parameter_type
            if parameter_type == "TABLE-KEY":
                if key_list == None:
                    for row in param.table.table_rows:
                        dict_value[row.key] = row.short_name
                else:
                    for key in key_list:
                        dict_value[param.table.table_rows[key].key] = key
                return dict_value
            elif parameter_type == "CODED-CONST":
                value = param.coded_value
                return value
            else:
                logger.info(f"Currently, this parameter type: {parameter_type} is not supported.")
                return
        except Exception as e:
            raise Exception(f"Reason: {e}")

class PDXCodec(DidCodec):
    def __init__(self, service, did, sub_service = None):
        self.service = service
        self.did = did
        self.sub_service = sub_service

    def decode(self, string_bin: bytes):
        parameters = self.service.positive_responses[0].parameters
        response_prefix_hex = ""
        # Get all CODED-CONST and insert to response message for decoding
        # SID_PR
        # DataIdentifier
        # ControlParam (IC Control Service)
        # ...
        for par in parameters:
            if par.parameter_type == "CODED-CONST":
                response_prefix_hex = response_prefix_hex + f"{par.coded_value:02x}"
            elif par.parameter_type == "MATCHING-REQUEST-PARAM":
                response_prefix_hex = response_prefix_hex + f"{self.did:02x}"

        string_hex = "".join([response_prefix_hex, string_bin.hex()])
        response = self.service.decode_message(bytearray.fromhex(string_hex)).param_dict
        return response

    def encode(self, *parameter_val, **parameter_dict):
        # encode() is called by WriteDataByIdentifier only pass value as positional argument(s)
        # request parameter dictionary is passed as first positional argument parameter_val[0]

        # encode is called by InputOutputControlByIdentifier pass value as positional or keyword argument(s)
        # request parameter dictionary is passed as keyword arguments **parameter_dict
        logger.info(f"Encode {self.service.short_name} message")
        encode_message = None
        request_parameters = {}
        try:
            for param in self.service.request.parameters:
                if param.parameter_type == 'TABLE-STRUCT':
                    service_params = param.table_key.table.table_rows[self.sub_service].structure.parameters
                    request_parameters[param.short_name] = dict()
                    request_parameters[param.short_name][self.sub_service] = parameter_dict
                    request_parameters = DiagnosticServices.convert_request_data_type(service_params, request_parameters)
                    request_parameters = {
                        param.short_name: tuple([self.sub_service, request_parameters])
                    }
                    encode_message = bytes(self.service.encode_request(**request_parameters))
                    logger.info(f"Full encode message: {encode_message}")
                    return encode_message

            if (not parameter_val) and (not parameter_dict):
                encode_message = self.service.encode_request()
            else:
                # Convert the parameter data type to the correct type
                if parameter_dict:
                    parameter_dict = DiagnosticServices.convert_request_data_type(self.service.request.parameters, parameter_dict)
                elif parameter_val and isinstance(parameter_val[0], dict):
                    parameter_dict = DiagnosticServices.convert_request_data_type(self.service.request.parameters, parameter_val[0])

                parameters = self.service.request.parameters
                pos_param = 0
                for par in parameters:
                    if par.parameter_type == "CODED-CONST":
                        pos_param = pos_param + (par.get_static_bit_length() >> 3)
                # Remove all CODED-CONST from encoded messages:
                # SID: 1 byte
                # DataIdentifier: 2 bytes
                # ControlParam (IC Control Service): 1 byte
                # ...
                encode_message = bytes(self.service.encode_request(**parameter_dict))[pos_param:]
                logger.info(f"Encode message: {encode_message}")
        except Exception as e:
            logger.error(f"Failed to encode {self.service.short_name} message.")
            raise Exception(f"Reason: {e}")

        return encode_message

    def __len__(self) -> int:
        bit_length = self.service.positive_responses[0].get_static_bit_length()
        if bit_length:
            return (bit_length >> 3) - 3
        elif self.sub_service is not None:
            bit_length = self.service.positive_responses[0].parameters[2].table.table_rows[self.sub_service].structure.get_static_bit_length()
            if bit_length:
                return (bit_length >> 3) - 3

        raise DidCodec.ReadAllRemainingData

class ServiceID(Enum):
    DIAGNOSTIC_SESSION_CONTROL = 0x10
    ECU_RESET = 0x11
    CLEAR_DIAGNOSTIC_INFORMATION = 0x14
    READ_DTC_INFORMATION = 0x19
    READ_DATA_BY_IDENTIFIER = 0x22
    READ_MEMORY_BY_ADDRESS = 0x23
    SECURITY_ACCESS = 0x27
    COMMUNICATION_CONTROL = 0x28
    READ_DATA_BY_PERIODIC_ID = 0x2A
    WRITE_DATA_BY_IDENTIFIER = 0x2E
    INPUT_OUTPUT_CONTROL_BY_IDENTIFIER = 0x2F
    ROUTINE_CONTROL = 0x31
    REQUEST_DOWNLOAD = 0x34
    REQUEST_UPLOAD = 0x35
    TRANSFER_DATA = 0x36
    TRANSFER_EXIT = 0x37
    WRITE_MEMORY_BY_ADDRESS = 0x3D
    TESTER_PRESENT = 0x3E
    CONTROL_DTC_SETTING = 0x85
