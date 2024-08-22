import odxtools
from RobotFramework_DoIP.DoipKeywords import DoipKeywords
from UDSKeywords import UDSLibrary
from udsoncan.Request import Request
from udsoncan.Response import Response
from udsoncan import services
class keywords:
    """Collection of odx functions to translate services from odx db to service message payloads"""

    def __init__(self):
        self.odx_db = None
        self.odx_ecu = None
        self.variant = ""

    def get_encoded_request_message(self, service_name):
        """fetch UDS information from given service name, set parameter value while doing so"""

        # logger.info(f"[uds]service name: {service_name}")
        print(f"[uds]service name: {service_name}")
        diag_service = getattr(self.odx_db.ecus[self.variant].services, service_name)

        return diag_service

    def load_pdx_file(self, file, variant):
        """Uncompress .pdx file and retrieved data in odx"""
        odxtools.exceptions.strict_mode = False
        self.odx_db = odxtools.load_pdx_file(file)
        odxtools.exceptions.strict_mode = True
        self.odx_ecu = self.odx_db.ecus[variant]
        self.variant = variant

    def get_decoded_response(self, request_hex, response_hex):
        """ Decode raw response message to readable string for further verification """
        request_bytes = bytearray.fromhex(request_hex)
        response_bytes = bytearray.fromhex(response_hex)
        response_decoded = self.odx_db.ecus[self.variant].decode_response(response_bytes, request_bytes)

        return response_decoded
# ==================
def example_test(rf_doip):
   uds_on_doip = keywords()
   uds_on_doip.load_pdx_file("C:/Data/Git/hw_test/project/testbench/stla/doip/CTS_STLA_V1_15_2.pdx", "CTS_STLA_Brain")
   diag_service = uds_on_doip.get_encoded_request_message("readCPUClockFrequencies_Read")

   uds = UDSLibrary(doip_layer=rf_doip, name="UDSConnector", close_connection=False)
   payload = uds.build_payload(diag_service)
   print(payload)
   response_encoded = uds.send_request(payload)
   print(response_encoded)
#    response = "6263305efc68005efc68005efc68005efc68005efc68005efc6800714be800714be800"
#    uds.interpret_response_data(response)
   uds.interpret_response_data(response_encoded)

def example_PingTest(rf_doip):
   uds_on_doip = keywords()
   uds_on_doip.load_pdx_file("C:/Data/Git/hw_test/project/testbench/stla/doip/CTS_STLA_V1_15_2.pdx", "CTS_STLA_Brain")
   diag_service = uds_on_doip.get_encoded_request_message("PingTest_Results_NoResponse")

   uds = UDSLibrary(doip_layer=rf_doip, name="UDSConnector", close_connection=False)
   payload = uds.build_payload(diag_service)
   print(payload)
   response_encoded = uds.send_request(payload)
   print(response_encoded)
   uds.interpret_response_data(response_encoded)

def example_RealTimeClock_Read(rf_doip):
   uds_on_doip = keywords()
   uds_on_doip.load_pdx_file("C:/Data/Git/hw_test/project/testbench/stla/doip/CTS_STLA_V1_15_2.pdx", "CTS_STLA_Brain")
   diag_service = uds_on_doip.get_encoded_request_message("RealTimeClock_Read")

   uds = UDSLibrary(doip_layer=rf_doip, name="UDSConnector", close_connection=False)
   payload = uds.build_payload(diag_service)
   print(payload)
   response_encoded = uds.send_request(payload)
   print(response_encoded)
   uds.interpret_response_data(response_encoded)

def new_test(rf_doip):
   uds_on_doip = keywords()
   uds_on_doip.load_pdx_file("C:/Data/Git/hw_test/project/testbench/stla/doip/CTS_STLA_V1_15_2.pdx", "CTS_STLA_Brain")
   diag_service = uds_on_doip.get_encoded_request_message("RealTimeClock_Read")
   uds = UDSLibrary(doip_layer=rf_doip, name="UDSConnector", close_connection=False)
   uds.ecu_reset(1)

if __name__ == "__main__":
   SUT_IP_ADDRESS = "192.168.0.1"
   SUT_LOGICAL_ADDRESS = 1863
   TB_IP_ADDRESS = "192.168.0.99"
   TB_LOGICAL_ADDRESS = 1895

   uds_on_doip = keywords()
   uds_on_doip.load_pdx_file("C:/Data/Git/hw_test/project/testbench/stla/doip/CTS_STLA_V1_15_2.pdx", "CTS_STLA_Brain")
   diag_service = uds_on_doip.get_encoded_request_message("readCPUClockFrequencies_Read")

   rf_doip = DoipKeywords()

   rf_doip.connect_to_ecu(
         ecu_ip_address = SUT_IP_ADDRESS,
         ecu_logical_address = SUT_LOGICAL_ADDRESS,
         client_ip_address = TB_IP_ADDRESS,
         client_logical_address = TB_LOGICAL_ADDRESS,
         activation_type = 0)

   # new_test(rf_doip)
   # example_test(rf_doip)
   # example_PingTest(rf_doip)
   example_RealTimeClock_Read(rf_doip)
   # uds = UDSLibrary(doip_layer=rf_doip, name="UDSConnector", close_connection=False)
   # # payload = uds.build_payload(request_encoded)
   # payload = uds.build_payload(request_encoded, diag_service)
   # uds.build_payload(diag_service)
   # # uds.send_request(payload)
   # print(payload)
   # uds.doip_layer.send_diagnostic_message(diagnostic_payload)
   # uds.send_request(payload)
   # uds.uds_connector.send(data)
   # payload = uds.build_payload(DiagnosticSessionControl, 1)
   # payload = uds.build_payload(DiagnosticSessionControl, 1)



   # # translate service details (odx) to doip message (uds)
   # SERVICE_NAME = "readCPUClockFrequencies_Read"

   # RESP_PARAMS = ['frequency_1', 'frequency_2', 'frequency_3', 'frequency_4',
   #                   'frequency_5', 'frequency_6', 'frequency_7', 'frequency_8']

   # request_encoded = uds_on_doip.get_encoded_request_message(SERVICE_NAME)
   # rf_doip.send_diagnostic_message(request_encoded)
   # response_encoded = rf_doip.receive_diagnostic_message()