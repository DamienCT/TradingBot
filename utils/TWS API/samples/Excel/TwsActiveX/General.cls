VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "General"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

'=================
' local constants
'=================
' table constants
Const CELL_CONNECTION_HOST = "A5"
Const CELL_CONNECTION_PORT = "C5"
Const CELL_CLIENT_ID = "E5"
Const CELL_CONNECT_OPTIONS = "G5"
Const CELL_SERVER_LOG_LEVEL = "A8"
Const CELL_CURRENT_TIME = "D8"
Const CELL_CURRENT_TIME_IN_MILLIS = "F8"
Const CELL_CONNECTION_STATUS = "Q7"
Const CELL_GLOBAL_CANCEL_EXT_OPERATOR = "J8"
Const CELL_GLOBAL_CANCEL_MANUAL_ORDER_INDICATOR = "L8"

'other constants
Const INCORRECT_HOST_PORT_STR = "You should enter valid Connection Host, Connection Port and Client ID"
Const CONNECTING_STR = "Connecting"
Const CONNECTED_STR = "Connected"
Const NOT_CONNECTED_STR = "Not connected"

Public Sub Initialise()
SetDisconnected
End Sub

Private Sub Worksheet_Activate()
Main.Initialise
End Sub

'=================
' private methods
'=================
' request global cancel
Private Sub RequestGlobalCancel_Click()
    If Not CheckConnected Then Exit Sub
    
    Dim orderCancel As TWSLib.IOrderCancel
    Set orderCancel = Api.Tws.createOrderCancel()
    
    orderCancel.extOperator = Util.SetNonEmptyValue(Range(CELL_GLOBAL_CANCEL_EXT_OPERATOR).value, orderCancel.extOperator)
    orderCancel.manualOrderIndicator = Util.SetNonEmptyValue(Range(CELL_GLOBAL_CANCEL_MANUAL_ORDER_INDICATOR).value, orderCancel.manualOrderIndicator)
    
    Api.Tws.ReqGlobalCancel orderCancel
End Sub

' request current time
Private Sub RequestCurrentTime_Click()
    If Not CheckConnected Then Exit Sub
    
    Api.Tws.reqCurrentTime
End Sub

' request current time in millis
Private Sub RequestCurrentTimeInMillis_Click()
    If Not CheckConnected Then Exit Sub
    
    Api.Tws.ReqCurrentTimeInMillis
End Sub

' set server log level
Private Sub SetServerLogLevel_Click()
    If Not CheckConnected Then Exit Sub
    
    Api.Tws.SetServerLogLevel Range(CELL_SERVER_LOG_LEVEL).value
End Sub

' connecting to TWS application
Private Sub ConnectToTWS_Click()
    If IsConnected Then
        MsgBox STR_TWS_CONTROL_ALREADY_CONNECTED
        Exit Sub
    End If
    
    Dim connectionHost As String, connectionPort As Long, clientId As Long, connectOptions As String

    ' load connectionHost, connectionPort and clientID from worksheet
    connectionHost = Range(CELL_CONNECTION_HOST).value
    connectionPort = Range(CELL_CONNECTION_PORT).value
    connectOptions = Range(CELL_CONNECT_OPTIONS).value
    clientId = Range(CELL_CLIENT_ID).value
    
    If connectionPort Like STR_EMPTY Or clientId Like STR_EMPTY Then
        MsgBox INCORRECT_HOST_PORT_STR
    Else
        SetConnecting
        Api.Tws.Connect connectionHost, connectionPort, clientId, connectOptions, False
    End If
End Sub

' disconnecting from TWS application
Private Sub DisconnectFromTWS_Click()
    If Not CheckConnected Then Exit Sub
    
    Api.Tws.Disconnect
    SetDisconnected
End Sub

'=================
' public methods
'=================
' current time
Public Sub UpdateCurrentTime(ByVal time As Long)
    Range(CELL_CURRENT_TIME).value = Util.ConvertLongStrToDateStr(CStr(time))
End Sub

' current time in millis
Public Sub UpdateCurrentTimeInMillis(ByVal time As String)
    Dim timeStr, millisStr
    timeStr = Left(time, Len(time) - 3)
    millisStr = Right(time, 3)
    Range(CELL_CURRENT_TIME_IN_MILLIS).value = Util.ConvertLongStrToDateStr(CStr(timeStr)) & "." & millisStr
End Sub

Public Sub SetDisconnected()
    Range(CELL_CONNECTION_STATUS).value = NOT_CONNECTED_STR
    Range(CELL_CONNECTION_STATUS).Interior.Color = RGB(255, 0, 0)
    IsConnected = False
End Sub

Public Sub SetConnected()
    Range(CELL_CONNECTION_STATUS).value = CONNECTED_STR
    Range(CELL_CONNECTION_STATUS).Interior.Color = RGB(0, 255, 0)
    IsConnected = True
End Sub

Public Sub SetConnecting()
    Range(CELL_CONNECTION_STATUS).value = CONNECTING_STR
    Range(CELL_CONNECTION_STATUS).Interior.Color = RGB(255, 220, 20)
    IsConnected = False
End Sub


