from robot.api import logger
from udsoncan.common.DidCodec import DidCodec
import odxtools


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

    def get_data_by_name(self, service_name_list):
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
        service = getattr(self.diag_services, service_name)
        logger.info(f"Encode {service.short_name} message")
        encode_message = None
        try:
            if not parameter_dict:
                encode_message = service.encode_request()
            else:
                request_parameters = service.request.parameters

                # The parameters from the Robot test are strings, so they are converted to the right types.
                for param in request_parameters:
                    # Just "VALUE" parameter are required for encode message
                    if param.parameter_type == "VALUE":
                        input_value = parameter_dict[param.long_name]
                        parameter_dict[param.long_name] = param.physical_type.base_data_type.from_string(input_value)
                    else:
                        pass

                encode_message = bytes(service.encode_request(**parameter_dict))
                logger.info(f"Full encode message: {encode_message}")
        except Exception as e:
            logger.error(f"Failed to encode {service.short_name} message.")
            raise Exception(f"Reason: {e}")
            
        return encode_message

    def get_decode_response_message(self, service_name, raw_message: bytes):
        service = getattr(self.diag_services, service_name)
        logger.info(f"Decode {service.short_name} message")
        decode_message = None

        decode_message = service.decode_message(raw_message).param_dict
        return decode_message

    def get_did_codec(self, service_id):
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
                request_parameters = self.service.request.parameters

                # The parameters from the Robot test are strings, so they are converted to the right types.
                for param in request_parameters:
                    # Just "VALUE" parameter are required for encode message
                    if param.parameter_type == "VALUE":
                        input_value = parameter_dict[param.long_name]
                        parameter_dict[param.long_name] = param.physical_type.base_data_type.from_string(input_value)
                    else:
                        pass

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
