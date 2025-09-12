*** Settings ***
Library    RobotFramework_TestsuitesManagement    WITH NAME    testsuites
Library    BuiltIn
Library    RobotFramework_UDS
Suite Setup    Connect
Suite Teardown    Disconnect

*** Variables ***
#UDS CAN Specific definitions
${VBUS_INTERFACE}=         vector
${VBUS_CHANNEL}=             0
${TX_INTERFACE}=          0x79D
${RX_INTERFACE}=          0x7AD
${UDS_DEVICE_NAME}        uds_can

${FILE}=       ${CURDIR}/pdx/PDX_Suz_DA3_Ver1.7.pdx
${VARIANT}=    Suz_DA3_DA3_SVS

#Important: Isotp Parameters can be updated for specific HW interfaces if needed. Below are default values.
&{isotp_config_params}    stmin=${32}    blocksize=${8}    wftmax=${0}    tx_data_length=${8}
...    tx_data_min_length=${None}    tx_padding=${0}    rx_flowcontrol_timeout=${1000}    rx_consecutive_frame_timeout=${1000}
...    override_receiver_stmin=${None}    max_frame_size=${4095}    can_fd=${False}    bitrate_switch=${False}
...    rate_limit_enable=${False}    rate_limit_max_bitrate=${1000000}    rate_limit_window_size=${0.2}    listen_mode=${False}

*** Keywords ***
Connect
    Log    Create a uds Connector
    
    Create UDS Connector    device_name=${UDS_DEVICE_NAME}
    ...                     communication_name=CAN
    ...                     interface=${VBUS_INTERFACE}
    ...                     channel=${VBUS_CHANNEL}
    ...                     txid= ${TX_INTERFACE}
    ...                     rxid= ${RX_INTERFACE}
    ...                     baudrate=500000
    ...                     isotp_config=&{isotp_config_params}

    Log    Using UDS Connector
    Connect UDS Connector    device_name=${UDS_DEVICE_NAME}
    Log    Open uds connection
    Open UDS Connection    device_name=${UDS_DEVICE_NAME}
    Using pdx

Disconnect
    Log    Close uds connection
    Close UDS Connection    device_name=${UDS_DEVICE_NAME}

Using pdx
    Load PDX    ${FILE}    ${VARIANT}    device_name=${UDS_DEVICE_NAME}

*** Test Cases ***
Test user can use Tester Present service on ECU
    Log    Use Tester Present service
    ${response}=    Tester Present    device_name=${UDS_DEVICE_NAME}
    ${session_response}    Diagnostic Session Control    3    device_name=${UDS_DEVICE_NAME}
    Log    ${session_response}    console=True


Test user can use Read Data By Identifier service on ECU
    Log    Use Read Data By Identifier service

    ${list_identifers}=    Create List    0xF18C
    ${responses}=    Read Data By Identifier    ${list_identifers}    device_name=${UDS_DEVICE_NAME}
    Log    ${responses}    console=True


Test user can use Read Data By Name service if the services have sub-service on ECU
    ${list_read}=    Create List    Identification_Read
    ${sub_service}=    Create List    ComponentID
    ${dict_sub_service}=    Create Dictionary    Identification_Read=${sub_service}

    ${responses}=    Read Data By Name    ${list_read}    parameters=${dict_sub_service}    device_name=${UDS_DEVICE_NAME}

    Log    ${responses}    console=True

    FOR    ${request_did}    IN    @{responses.keys()}
        Log    Key: ${request_did}, Value: ${responses["${request_did}"]}    console=True
        ${response}=    Set Variable    ${responses["${request_did}"]}
        FOR    ${item}    IN    @{response.keys()}
            Log    ${item} : ${response["${item}"]}    console=True
        END
    END
Test user can use Read DTC service on ECU
    Log    Use Read Read DTC service

    Log    Use Read DTC with subfunction as 02 and status_mask as 0x4b

    ${responses}=    Read DTC Information    subfunction=0x02    status_mask=0x4B    device_name=${UDS_DEVICE_NAME}
    Log    ${responses}    console=True

    FOR    ${request_did}    IN    ${responses.service_data.dtcs}
        Log    ${request_did}    console=True
    END

