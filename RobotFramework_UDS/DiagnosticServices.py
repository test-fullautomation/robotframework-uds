from udsoncan import Routine
from robot.api import logger
from robot.api.deco import keyword
import odxtools


class DiagnosticServices:
    def __init__(self, pdx_file, variant):
        self.variant = variant
        self.pdx_file = pdx_file
        # load pdx file
        odxtools.exceptions.strict_mode = False
        self.odx_db = odxtools.load_pdx_file(self.pdx_file)
        odxtools.exceptions.strict_mode = True
        self.odx_ecu = self.odx_db.ecus[self.variant]
        self.diag_services = self.get_diag_services()

    def get_diag_services(self):
        return self.odx_db.ecus[self.variant].services

    @keyword("Read data by name")
    def read_data_by_name(self, service_name_list):
        diag_service_list = []
        for service_name in service_name_list:
            try:
                diag_service = getattr(self.odx_db.ecus[self.variant].services, service_name)
                diag_service_list.append(diag_service)
            except Exception as e:
                logger.error(f"Diagnostic service does not contain an item named {service_name}")

        return diag_service_list

    @keyword("Routine Control By Name")
    def routine_control_by_name(self, routine_name, data):
        # TODO
        return