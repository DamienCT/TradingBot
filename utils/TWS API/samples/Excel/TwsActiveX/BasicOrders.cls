VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "BasicOrders"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

Private contractTable As Range
Private orderTable As Range
Private orderStatusTable As Range
Private extendedAttributeTable As Range
Private commissionAndFeesMarginTable As Range

'=================
' methods
'=================
' apply template from Extended Order Attributes sheet
Private Sub ApplyExtendedTemplate_Click()
    OrderUtils.ApplyExtendedTemplate getActiveOrderIndex, extendedAttributeTable
End Sub

' cancel order
Private Sub CancelOrder_Click()
    OrderUtils.CancelOrders orderStatusTable, extendedAttributeTable
End Sub

' clear order statuses
Private Sub ClearOrderStatuses_Click()
    orderStatusTable.ClearContents
End Sub

' Combo Legs
Private Sub ComboLegs_Click()
   ComboLegForm.ShowForm contractTable
End Sub

Private Sub CreateTicker_Click()
    TickerForm.ShowForm contractTable
End Sub

' place / modify order
Public Sub PlaceModifyOrder_Click()
    If Not CheckConnected Then Exit Sub
    
    OrderUtils.PlaceModifyOrders _
                    contractTable, _
                    orderTable, _
                    orderStatusTable, _
                    extendedAttributeTable, _
                    WhatIf.value
End Sub

' update order status
Public Sub UpdateOrderStatus(id As Long, status As String, filled As Variant, remaining As Variant, avgFillPrice As Double, parentId As Long, lastFillPrice As Double)
    OrderUtils.UpdateOrderStatus orderStatusTable, id, status, filled, remaining, avgFillPrice, parentId, lastFillPrice
End Sub

Public Sub UpdateWhatIfInfo(orderId As Long, contract As TWSLib.IContract, order As TWSLib.IOrder, orderState As TWSLib.IOrderState)
    OrderUtils.UpdateWhatIfInfo orderStatusTable, commissionAndFeesMarginTable, orderId, contract, order, orderState
End Sub

' process error
Public Sub ProcessError(ByVal id As Long, ByVal errorTime As String, ByVal errorCode As Long, ByVal errorMsg As String)
    OrderUtils.ProcessError orderStatusTable, id, errorTime, errorCode, errorMsg
End Sub

Private Sub SmartComboRoutingParams_Click()
    ParamsForm.ShowForm getActiveOrderIndex, contractTable, extendedAttributeTable
End Sub

Private Function getActiveOrderIndex()
    getActiveOrderIndex = ActiveCell.row - orderTable.Rows(1).row + 1
End Function

Public Sub Initialise()
    Set contractTable = BasicOrders.Range("$A$7:$M$125")
    Set orderTable = BasicOrders.Range("$N$7:$S$125")
    Set orderStatusTable = BasicOrders.Range("$T$7:$Z$125")
    Set commissionAndFeesMarginTable = BasicOrders.Range("$AA$7:$AY$125")
    Set extendedAttributeTable = BasicOrders.Range("$AZ$7:$FC$125")
End Sub

Private Sub Worksheet_Activate()
    Main.Initialise
    Application.OnKey "+^p", "BasicOrders.PlaceModifyOrder_Click"
End Sub

Private Sub Worksheet_Deactivate()
    Application.OnKey "+^p"
End Sub

