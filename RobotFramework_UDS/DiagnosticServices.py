from robot.api import logger
from udsoncan.common.DidCodec import DidCodec
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
        self.diag_layer = self.odx_db.ecus[self.variant]
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
            if isinstance(org_val, bytes):
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
    def convert_request_data_type(service, parameter_dict):
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
        request_parameters = service.request.parameters

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

    def get_encoded_request_message(self, service_name, parameter_dict):
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
                parameter_dict = self.convert_request_data_type(service, parameter_dict)
                encode_message = bytes(service.encode_request(**parameter_dict))
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

    def get_did_codec(self, service_id):
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

        diag_services = self.diag_layer.service_groups[service_id]
        for diag_service in diag_services:
            did = diag_service.request.parameters[1].coded_value
            did_codec[did] = PDXCodec(diag_service)

        return did_codec

class PDXCodec(DidCodec):
    def __init__(self, service):
        self.service = service

    def decode(self, string_bin: bytes):
        parameters = self.service.positive_responses[0].parameters
        response_prefix_hex = "".join([hex(parameters[0].coded_value).replace("0x", ""), hex(parameters[1].coded_value).replace("0x", "")])

        string_hex = "".join([response_prefix_hex, string_bin.hex()])
        response = self.service.decode_message(bytearray.fromhex(string_hex)).param_dict
        return response

    def encode(self, parameter_dict):
        logger.info(f"Encode {self.service.short_name} message")
        encode_message = None
        try:
            if not parameter_dict:
                encode_message = self.service.encode_request()
            else:
                # Convert the parameter data type to the correct type
                parameter_dict = DiagnosticServices.convert_request_data_type(self.service, parameter_dict)

                # Remove the first 3 bytes since the UDS library automatically adds the first 3 bytes for the DID.
                encode_message = bytes(self.service.encode_request(**parameter_dict))[3:]
                logger.info(f"Encode message: {encode_message}")
        except Exception as e:
            logger.error(f"Failed to encode {self.service.short_name} message.")
            raise Exception(f"Reason: {e}")
            
        return encode_message

    def __len__(self) -> int:
        bit_length = self.service.positive_responses[0].get_static_bit_length()
        if bit_length:
            return (bit_length >> 3) - 3
        else:
            raise DidCodec.ReadAllRemainingData
