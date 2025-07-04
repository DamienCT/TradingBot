VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Errors"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
' constants
Const STR_SHEET_NAME = "Errors"
Const STR_REQERRORS = "reqErrors"

' cells
Const CELL_SERVER_NAME = "B5" ' cell with server name
Const CELL_SUBSCRIPTION_CONTROL = "M5" ' cell with subscription control

'rows
Const ERRORS_START_ROW = 10
Const ERRORS_END_ROW = 200

'range
Const TABLE_RANGE = "A" & ERRORS_START_ROW & ":AK" & ERRORS_END_ROW

Dim errorsStartIndex As Integer

' ========================================================
' Subscribes to error updates
' ========================================================
Sub subscribeErrors()
    With Worksheets(STR_SHEET_NAME)
        If CStr(.Range(CELL_SUBSCRIPTION_CONTROL).value <> util.STR_SUBSCRIBED) Then ' only if not subscribed
            errorsStartIndex = 0
    
            clearTable
            
            Dim server As String
            
            server = util.getServerVal(STR_SHEET_NAME, CELL_SERVER_NAME)
            If server = util.STR_EMPTY Then Exit Sub
            
            .Range(CELL_SUBSCRIPTION_CONTROL).Formula = util.composeLink(server, STR_REQERRORS, util.IDENTIFIER_ZERO, util.STR_ERROR) ' subscription control
            If util.cleanOnError(.Range(CELL_SUBSCRIPTION_CONTROL)) Then
                .Range(CELL_SUBSCRIPTION_CONTROL).value = util.STR_EMPTY
                Exit Sub
            End If
            
        End If
    End With
End Sub

' ========================================================
' Clear errors table
' ========================================================
Sub clearTable()
    ' clear table
    Worksheets(STR_SHEET_NAME).Range(TABLE_RANGE).ClearContents
End Sub

' ========================================================
' Cancel error updates subscription when button is pressed
' ========================================================
Sub cancelSubscription()
    errorsStartIndex = 0
    Worksheets(STR_SHEET_NAME).Range(CELL_SUBSCRIPTION_CONTROL).Formula = util.STR_EMPTY ' subscription control
End Sub

' ========================================================
' Cancel error updates subscription when when workbook is closed
' ========================================================
Sub cancelSubscriptionOnExit()
    With Worksheets(STR_SHEET_NAME)
        If CStr(.Range(CELL_SUBSCRIPTION_CONTROL).value = util.STR_SUBSCRIBED) Then ' only if subscribed
            errorsStartIndex = 0
            .Range(CELL_SUBSCRIPTION_CONTROL).Formula = util.STR_CANCELLED ' subscription control
        End If
    End With
End Sub

' ========================================================
'
' ========================================================
Sub startSubscription()
    If CStr(Worksheets(STR_SHEET_NAME).Range(CELL_SUBSCRIPTION_CONTROL).value) = util.STR_CANCELLED Then
        subscribeErrors
    End If
End Sub

' ========================================================
' Requests errors table/array
' Called when value in CELL_SUBSCRIPTION_CONTROL changes
' ========================================================
Private Sub Worksheet_Calculate()
    If Not util.sheetExists(STR_SHEET_NAME) Then Exit Sub
    
    With Worksheets(STR_SHEET_NAME)
        If CStr(.Range(CELL_SUBSCRIPTION_CONTROL).value) = util.STR_SUBSCRIBED Then
            Dim server As String, id As String
            Dim errorsArray() As Variant
            server = util.getServerVal(STR_SHEET_NAME, CELL_SERVER_NAME)
            If server = util.STR_EMPTY Then Exit Sub
            
            ' send request and receive errors table/array
            errorsArray = util.sendRequest(server, STR_REQERRORS, util.IDENTIFIER_ZERO & util.QMARK & errorsStartIndex) ' returned array can be 1-Dimension or 2-Dimension
            
            Dim dimension As Integer, row As Integer, i As Integer, j As Integer
            dimension = util.getDimension(errorsArray)
            If dimension = 2 Then
                ' several errors received (2d array)
                row = util.findEmptyRow(Worksheets("Errors"), ERRORS_START_ROW, ERRORS_END_ROW)
                For i = 1 To UBound(errorsArray) - LBound(errorsArray) + 1
                    .Cells(row + i - 1, 1).value = errorsArray(i, 1) ' error id
                    .Cells(row + i - 1, 2).value = errorsArray(i, 2) ' error time
                    .Cells(row + i - 1, 3).value = errorsArray(i, 3) ' error code
                    ' error messagee can be > 255 symbols, so we should concat all parts (each of length 255) of error message
                    Dim errorMsg, advancedOrderRejectJson, tempStr As String
                    errorMsg = util.STR_EMPTY
                    advancedOrderRejectJson = util.STR_EMPTY
                    tempStr = util.STR_EMPTY
                    Dim hasAdvancedOrderRejectJson As Boolean

                    For j = 3 To UBound(errorsArray, 2) - LBound(errorsArray, 2) + 1
                        If errorsArray(i, j) = util.ADVANCED_ORDER_REJECT_JSON Then
                            errorMsg = tempStr
                            tempStr = util.STR_EMPTY
                            hasAdvancedOrderRejectJson = True
                        Else
                            tempStr = tempStr + errorsArray(i, j)
                        End If
                    Next j
                    If hasAdvancedOrderRejectJson Then
                        advancedOrderRejectJson = tempStr
                        hasAdvancedOrderRejectJson = False
                    Else
                        errorMsg = tempStr
                    End If
                    .Cells(row + i - 1, 4).value = errorMsg ' error message
                    .Cells(row + i - 1, 32).value = advancedOrderRejectJson ' advanced order reject json
                    errorsStartIndex = errorsStartIndex + 1
                Next i
            ElseIf dimension = 1 Then
                ' single error received (1d array)
                row = util.findEmptyRow(Worksheets("Errors"), ERRORS_START_ROW, ERRORS_END_ROW)
                For i = 1 To UBound(errorsArray) - LBound(errorsArray) + 1
                    .Cells(row, i).value = errorsArray(i)
                Next i
                errorsStartIndex = errorsStartIndex + 1
            End If
        End If
    End With
End Sub

