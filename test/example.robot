*** Settings ***
Library    RobotFramework_TestsuitesManagement    WITH NAME    testsuites
Library    RobotFramework_UDS
Suite Setup    Connect
Suite Teardown    Disconnect

*** Variables ***
${SUT_IP_ADDRESS}=    192.168.0.1
${SUT_LOGICAL_ADDRESS}=    1863
${TB_IP_ADDRESS}=    192.168.0.99
${TB_LOGICAL_ADDRESS}=    1895
${ACTIVATION_TYPE}=    0

${FILE}=    C:/Users/MAR3HC/Desktop/UDS/robotframework-uds/test/pdx/CTS_STLA_V1_15_2.pdx
${VARIANT}=    CTS_STLA_Brain

*** Keywords ***
Connect
    Log    Create a uds Connector
    Create UDS Connector    ecu_ip_address= ${SUT_IP_ADDRESS}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS}
    ...                     client_ip_address= ${TB_IP_ADDRESS}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS}
    ...                     activation_type= ${ACTIVATION_TYPE}
    Log    Using UDS Connector
    Connect UDS Connector
    Log    Open uds connection
    Open UDS Connection
    Using pdx

Disconnect
    Log    Close uds connection
    Close UDS Connection

Using pdx
    Load PDX    ${FILE}    ${VARIANT}

*** Test Cases ***
Test user can use Tester Present service on ECU
    Log    Use Tester Present service
    ${response}=    Tester Present

Test user can use ECU Reset service on ECU
    Log    Use ECU Reset service

    Log    Hard reset
    ${response_hr}=    ECU Reset    1

    Log    Key off on reset
    ${response_k}=    ECU Reset    2

    Log    Soft reset
    ${response_sr}=    ECU Reset    3

    Log    Enable rapid power shut down
    ${response_e}=    ECU Reset    4

    Log    disable rapid power shut down
    ${response_d}=    ECU Reset    5

Test user can use Read Data By Name service on ECU
    Log    Use Read Data By Name service

    Log    readCPUClockFrequencies_Read

    ${service_name_list}=    Create List    readCPUClockFrequencies_Read
    Read Data By Name    ${service_name_list}

Test user can use Routine Control By Name service on ECU
    Log    Routine Control By Name service

    Log    PingTest_Start_NoResponse
    Routine Control By Name    PingTest_Start_NoResponse

Test user can use Diagnostic Session Control service on ECU
    Log    Diagnostic Session Control service

    Diagnostic Session Control    1

Test user can use Write Data By Name service on ECU
    Log    Write Data By Name service

    Log    RealTimeClock_Write
    ${PARAM_DICT}=    Create Dictionary    Day=26    Month=September    Year=2024    Hour=10    Second=45    Minute=0
    Write Data By Name    RealTimeClock_Write    ${PARAM_DICT}

    Log    Using service did instead service's name
    Write Data By Identifier    25382    ${PARAM_DICT}
