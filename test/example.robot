*** Settings ***
Library    RobotFramework_TestsuitesManagement    WITH NAME    testsuites
Library    RobotFramework_DoIP
Library    RobotFramework_UDS
Suite Setup    Connect
Suite Teardown    Disconnect

*** Variables ***
${SUT_IP_ADDRESS}=    192.168.0.1
${SUT_LOGICAL_ADDRESS}=    1863
${TB_IP_ADDRESS}=    192.168.0.99
${TB_LOGICAL_ADDRESS}=    1895
${ACTIVATION_TYPE}=    ${None}

${FILE}=    C:/Data/Git/hw_test/project/testbench/stla/doip/CTS_STLA_V1_15_2.pdx
${VARIANT}=    CTS_STLA_Brain

${NAME}=    UDS Connector

*** Keywords ***
Connect
    Log    Connect to ECU
    ${doip_layer}=    Connect To ECU    ecu_ip_address= ${SUT_IP_ADDRESS}
    ...               ecu_logical_address= ${SUT_LOGICAL_ADDRESS}
    ...               client_ip_address= ${TB_IP_ADDRESS}
    ...               client_logical_address= ${TB_LOGICAL_ADDRESS}
    ...               activation_type= ${ACTIVATION_TYPE}
    Log    Using UDS Connector
    Connect UDS Connector    doip_layer=${doip_layer}    name=${NAME}
    Log    Open uds connection
    Open UDS Connection

Disconnect
    Log    Close uds connection
    Close UDS Connection

Using pdx
    Load PDX    ${FILE}    ${VARIANT}

*** Test Cases ***
Test user can get diagnostic service in pdx file by name
    ${diag_service_name_list}=    Create List    
    Read Data By Name    

