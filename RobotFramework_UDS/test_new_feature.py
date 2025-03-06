from UDSKeywords import UDSKeywords


if __name__ == "__main__":
    pdx = "D:/fix-table-key-UDS/doipScripts/XTS_CAT5G.pdx"
    variant = "XTS_CAT5G_ProPlus"

    uds = UDSKeywords()
    uds.load_pdx(pdx, variant)
    # uds.read_data_by_name(["readCPUClockFrequencies_Read"])
    sub_services = {
      'Identification_Read': ['CTSSWVersion']
    }
    uds.routine_control_by_name('Routine_Control_Start', sub_service='AdbShellCmd')
    uds.read_data_by_name(["Identification_Read", "readCPUClockFrequencies_Read"])
   #  uds.write_data_by_name("Identification_Write", sub_service = 'ECUHWVersion')
   #  uds.write_data_by_name("Identification_Write", [])
   #  uds.read_data_by_name(["Identification_Read"])
    uds.io_control_by_name("IOControl_Control", sub_service='GNSS_BaudRate')
    # uds.read_data_by_name(["GPULoad_Read"])