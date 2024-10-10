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


&{canConfig0}    CanConfigUsed=true     TX_CAN_Channel=0    timeout=100    waitTime=0    rxId=b'\x40\x12\x00\x00'    txId=b'\x40\x21\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
&{canConfig1}    CanConfigUsed=true     TX_CAN_Channel=1    timeout=100    waitTime=0    rxId=b'\x40\x12\x00\x00'    txId=b'\x40\x21\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
&{canConfig2}    CanConfigUsed=true     TX_CAN_Channel=2    timeout=100    waitTime=0    rxId=b'\x01\xDC\x00\x00'    txId=b'\x1F\xFF\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=client
&{canConfig3}    CanConfigUsed=true     TX_CAN_Channel=3    timeout=100    waitTime=0    rxId=b'\x1F\xFF\x00\x00'    txId=b'\x01\xDC\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
&{canConfig4}    CanConfigUsed=false    TX_CAN_Channel=4    timeout=100    waitTime=0    rxId=b'\x00\x00\x07\xFF'    txId=b'\x00\x00\x07\x77'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
&{canConfig5}    CanConfigUsed=false    TX_CAN_Channel=5    timeout=100    waitTime=0    rxId=b'\x00\x12\x00\x00'    txId=b'\x00\x21\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x0F\x04\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server

# &{canConfig}    &{canConfig0}    &{canConfig1}    &{canConfig2}    &{canConfig3}    &{canConfig4}    &{canConfig5}
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
    ${responses}=    Read Data By Name    ${service_name_list}
    Log    ${responses}

    FOR    ${request_did}    IN    @{responses.keys()}
        Log    Key: ${request_did}, Value: ${responses[${request_did}]}    console=True
        ${response}=    Set Variable    ${responses[${request_did}]}
        FOR    ${item}    IN    @{response.keys()}
            Log    ${item} : ${response["${item}"]}    console=True
        END
    END
Test user can use Routine Control By Name service on ECU
    Log    Routine Control By Name service

    ${param_dict}=    Create Dictionary    port=5101    argument=-i 0.5 -B 192.168.1.
    ${response}=    Routine Control By Name    StartIperfServer_Start    ${param_dict}
    Log    ${response}    console=True
    FOR    ${item}    IN    @{response.keys()}
        Log    ${item} : ${response["${item}"]}    console=True
    END

Test CAN_MasterSlaveEnduranceRun_Start can use Routine Control By Name service on ECU
    ${canConfig0}=    Create Dictionary    CanConfigUsed=true     TX_CAN_Channel=0    timeout=100    waitTime=0    rxId=b'\x40\x12\x00\x00'    txId=b'\x40\x21\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
    ${canConfig1}=    Create Dictionary    CanConfigUsed=true     TX_CAN_Channel=1    timeout=100    waitTime=0    rxId=b'\x40\x12\x00\x00'    txId=b'\x40\x21\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
    ${canConfig2}=    Create Dictionary    CanConfigUsed=true     TX_CAN_Channel=2    timeout=100    waitTime=0    rxId=b'\x01\xDC\x00\x00'    txId=b'\x1F\xFF\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=client
    ${canConfig3}=    Create Dictionary    CanConfigUsed=true     TX_CAN_Channel=3    timeout=100    waitTime=0    rxId=b'\x1F\xFF\x00\x00'    txId=b'\x01\xDC\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
    ${canConfig4}=    Create Dictionary    CanConfigUsed=false    TX_CAN_Channel=4    timeout=100    waitTime=0    rxId=b'\x00\x00\x07\xFF'    txId=b'\x00\x00\x07\x77'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x05\x02\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server
    ${canConfig5}=    Create Dictionary    CanConfigUsed=false    TX_CAN_Channel=5    timeout=100    waitTime=0    rxId=b'\x00\x12\x00\x00'    txId=b'\x00\x21\x00\x00'    dlc=4 Bytes    nominalBitTiming=b'\x08\x0F\x04\x01'    dataBitTiming=b'\x02\x0F\x04\x01'    tdcEnable=Enabled    tdcOffset=10    pattern=b'\xAA\xBB\xCC\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'    Can_Operation_Mode=server

    ${canConfig}=    Create Dictionary    canConfig0=&{canConfig0}    canConfig1=&{canConfig1}    canConfig2=&{canConfig2}    canConfig3=&{canConfig3}    canConfig4=&{canConfig4}    canConfig5=&{canConfig5}
    Load PDX    C:/Users/MAR3HC/Desktop/UDS/robotframework-uds/test/pdx/XTS_MPCI_Maas_1.23.45.pdx    XTS_MPCI_MaaS
    Routine Control By Name    CAN_MasterSlaveEnduranceRun_Start    ${canConfig}

Test user can use Diagnostic Session Control service on ECU
    Log    Diagnostic Session Control service

    Diagnostic Session Control    1

Test user can use Write Data By Name service on ECU
    Log    Write Data By Name service

    Log    RealTimeClock_Write
    ${PARAM_DICT}=    Create Dictionary    Day=26    Month=September    Year=2024    Hour=10    Second=45    Minute=0

    Write Data By Name    RealTimeClock_Write    ${PARAM_DICT}

    ${DICT}=    Create Dictionary    ipAddress=155
    Write Data By Name    CTS_IPAddress_Write    ${DICT}

    Log    Using service did instead service's name
    Write Data By Identifier    25382    ${PARAM_DICT}
