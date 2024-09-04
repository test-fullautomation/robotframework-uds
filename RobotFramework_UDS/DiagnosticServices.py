from robot.api import logger
import odxtools
from udsoncan.common.DidCodec import DidCodec


class DiagnosticServices:
    def __init__(self, pdx_file, variant):
        self.variant = variant
        self.pdx_file = pdx_file
        # load pdx file
        odxtools.exceptions.strict_mode = False
        self.odx_db = odxtools.load_pdx_file(self.pdx_file)
        odxtools.exceptions.strict_mode = True
        self.odx_ecu = self.odx_db.ecus[self.variant]
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

    def get_did_codec(self):
        did_codec = {}
        read_services = self.odx_db.diag_layers[self.variant].service_groups[0x22]
        for service_diag in read_services:
            did = service_diag.request.parameters[1].coded_value
            did_codec[did] = PDXDidCodec(service_diag)

        return did_codec

class PDXDidCodec(DidCodec):
    def __init__(self, service):
        self.service = service

    def decode(self, payload):
        return self.service.decode_message(payload).param_dict

    def __len__(self):
        bit_length = self.service.positive_responses[0].get_static_bit_length()
        return bit_length>>3
