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
                diag_service = getattr(self.diag_services, service_name)
                diag_service_list.append(diag_service)
            except:
                logger.error(f"Diagnostic service does not contain an item named {service_name}")

        return diag_service_list

    def get_encoded_request_message(self, diag_service_list, parameters=None):
        uds_list = []
        for diag_service in diag_service_list:
            param_dict = {}
            uds = ""
            logger.info(f"[uds] Service name: {diag_service}")
            if parameters:
                for param in parameters:
                    isolate_list = param.split("=")
                    param_dict[isolate_list[0]] = eval(isolate_list[1])

                logger.info(f"[uds] Parameters: {param_dict}")
                try:
                    uds = diag_service(**param_dict).hex()
                    uds_list.append(uds)
                except:
                    logger.info(f"UDS: Retrieve uds failed.")
            else:
                uds = diag_service().hex()
                if len(uds) > 0:
                    logger.info(f"UDS: {uds}")
                    uds_list.append(uds)
                else:
                    logger.info("UDS: Retrieve uds failed.")

        return uds_list

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

    def __len__(self) -> int:
        bit_length = self.service.positive_responses[0].get_static_bit_length()
        string_len =  (bit_length >> 3) - 3
        
        return string_len


