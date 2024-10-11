*** Settings ***
Library    RobotFramework_TestsuitesManagement    WITH NAME    testsuites
Library    RobotFramework_UDS

*** Variables ***
${SUT_IP_ADDRESS_1}=         SUT_IP_ADDRESS_1
${SUT_LOGICAL_ADDRESS_1}=    SUT_LOGICAL_ADDRESS_1
${TB_IP_ADDRESS_1}=          TB_IP_ADDRESS_1
${TB_LOGICAL_ADDRESS_1}=     TB_LOGICAL_ADDRESS_1
${ACTIVATION_TYPE_1}=        0
${DEVICE_NAME_1}=            UDS Connector 1
${FILE_1}=                   path/file.pdx
${VARIANT_1}=                VARIANT_1

${SUT_IP_ADDRESS_2}=         SUT_IP_ADDRESS_2
${SUT_LOGICAL_ADDRESS_2}=    SUT_LOGICAL_ADDRESS_2
${TB_IP_ADDRESS_2}=          TB_IP_ADDRESS_2
${TB_LOGICAL_ADDRESS_2}=     TB_LOGICAL_ADDRESS_2
${ACTIVATION_TYPE_2}=        0
${DEVICE_NAME_2}=            UDS Connector 2
${FILE_2}=                   path/file.pdx
${VARIANT_2}=                VARIANT_2

${ERROR_STR}=    NegativeResponseException: ReadDataByIdentifier service execution returned a negative response IncorrectMessageLengthOrInvalidFormat (0x13)
*** Test Cases ***
Test user can connect single UDS connection
    Log    Test user can connect single UDS connection
    Log    If no device_name is provided, it will default to 'default'

    Create UDS Connector    ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}

    Connect UDS Connector
    Open UDS Connection
    Load PDX    ${FILE_1}    ${VARIANT_1}
    ${service_name_list}=    Create List    readCPUClockFrequencies_Read
    Read Data By Name    ${service_name_list}
    Close UDS Connection

Test user can connect multiple UDS connection
    Log    Test user can connect multiple UDS connection
    Log    Connect to device 1
    Create UDS Connector    device_name= ${DEVICE_NAME_1}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}
    Connect UDS Connector   device_name= ${DEVICE_NAME_1}

    Open UDS Connection    device_name= ${DEVICE_NAME_1}
    Load PDX    ${FILE_1}    ${VARIANT_1}    device_name= ${DEVICE_NAME_1}
    ${service_name_list_1}=    Create List    readCPUClockFrequencies_Read
    Read Data By Name    ${service_name_list_1}    device_name= ${DEVICE_NAME_1}

    Log    Connect to device 2
    Create UDS Connector    device_name= ${DEVICE_NAME_2}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_2}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_2}
    ...                     client_ip_address= ${TB_IP_ADDRESS_2}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_2}
    ...                     activation_type= ${ACTIVATION_TYPE_2}
    Connect UDS Connector    device_name= ${DEVICE_NAME_2}

    Open UDS Connection    device_name= ${DEVICE_NAME_2}
    Load PDX    ${FILE_2}    ${VARIANT_2}    device_name= ${DEVICE_NAME_2}
    ${service_name_list_2}=    Create List    CPULoad_Read
    Log    Expected device 2 cannot send readCPUClockFrequencies_Read service like device 1
    Run Keyword And Expect Error    ${ERROR_STR}    Read Data By Name    ${service_name_list_1}    device_name= ${DEVICE_NAME_2}

    Read Data By Name    ${service_name_list_2}    device_name= ${DEVICE_NAME_2}

Test user can connect multiple UDS connection but connect to the same ECU
    Log    Test user can connect multiple UDS connection
    Log    Connect to device 1
    Create UDS Connector    device_name= ${DEVICE_NAME_1}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}
    Connect UDS Connector    device_name= ${DEVICE_NAME_1}

    Log    Open uds connection
    Open UDS Connection    device_name= ${DEVICE_NAME_1}
    Load PDX    ${FILE_1}    ${VARIANT_1}    device_name= ${DEVICE_NAME_1}
    ${service_name_list_1}=    Create List    readCPUClockFrequencies_Read
    Read Data By Name    ${service_name_list_1}    device_name= ${DEVICE_NAME_1}

    Log    Connect to device 2 but same IP as device 1
    Log    The expected test case result in an error
    Run Keyword And Expect Error    TimeoutError: ECU failed to respond in time    Create UDS Connector    device_name= ${DEVICE_NAME_2}
    ...                                                                                                    ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                                                                                                    ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                                                                                                    client_ip_address= ${TB_IP_ADDRESS_1}
    ...                                                                                                    client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                                                                                                    activation_type= ${ACTIVATION_TYPE_1}

Test users can reconnect to the closed ECU
    Log    Connect to device 2
    Create UDS Connector    device_name= ${DEVICE_NAME_2}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_2}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_2}
    ...                     client_ip_address= ${TB_IP_ADDRESS_2}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_2}
    ...                     activation_type= ${ACTIVATION_TYPE_1}
    Connect UDS Connector    device_name= ${DEVICE_NAME_2}

    Open UDS Connection    device_name= ${DEVICE_NAME_2}
    Load PDX    ${FILE_2}    ${VARIANT_2}    device_name= ${DEVICE_NAME_2}
    ${service_name_list_2}=    Create List    CPULoad_Read
    Read Data By Name    ${service_name_list_2}    device_name= ${DEVICE_NAME_2}
    Close UDS Connection    device_name= ${DEVICE_NAME_2}

    Log    Connect to device 1
    Create UDS Connector    device_name= ${DEVICE_NAME_1}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}
    Connect UDS Connector    device_name= ${DEVICE_NAME_1}

    Open UDS Connection    device_name= ${DEVICE_NAME_1}
    Load PDX    ${FILE_1}    ${VARIANT_1}    device_name= ${DEVICE_NAME_1}
    ${service_name_list_1}=    Create List    readCPUClockFrequencies_Read
    Read Data By Name    ${service_name_list_1}    device_name= ${DEVICE_NAME_1}
    Close UDS Connection    device_name= ${DEVICE_NAME_1}


    Log    Re-opent uds connection device 2
    Open UDS Connection    device_name= ${DEVICE_NAME_2}
    Read Data By Name    ${service_name_list_2}    device_name= ${DEVICE_NAME_2}

    Log    Expected device 2 cannot send readCPUClockFrequencies_Read service like device 1
    Run Keyword And Expect Error    ${ERROR_STR}    Read Data By Name    ${service_name_list_1}    device_name= ${DEVICE_NAME_2}
    Close UDS Connection    device_name= ${DEVICE_NAME_2}