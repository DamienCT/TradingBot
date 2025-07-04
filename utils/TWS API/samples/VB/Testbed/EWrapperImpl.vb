' Copyright (C) 2025 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
' and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.

Imports IBApi
Imports System.Text

Namespace Samples

    '! [ewrapperimpl]
    Public Class EWrapperImpl
        Implements EWrapper
        '! [ewrapperimpl]
        '! [socket_declare]
        Public eReaderSignal As EReaderSignal
        Public socketClient As EClientSocket
        '! [socket_declare]
        Public nextOrderId As Integer

        '! [socket_init]
        Sub New()
            eReaderSignal = New EReaderMonitorSignal
            socketClient = New EClientSocket(Me, eReaderSignal)
        End Sub
        '! [socket_init]

        Private _bboExchange As String

        Public Property BboExchange As String
            Get
                Return _bboExchange
            End Get
            Private Set(value As String)
                _bboExchange = value
            End Set
        End Property

        Function serverVersion() As Integer
            serverVersion = socketClient.ServerVersion
        End Function

        '! [accountdownloadend]
        Public Sub accountDownloadEnd(account As String) Implements IBApi.EWrapper.accountDownloadEnd
            Console.WriteLine("accountDownloadEnd - Account[" & account & "]")
        End Sub
        '! [accountdownloadend]

        '! [accountsummary]
        Public Sub accountSummary(reqId As Integer, account As String, tag As String, value As String, currency As String) Implements IBApi.EWrapper.accountSummary
            Console.WriteLine("AccountSummary - ReqId [" & reqId & "] Account [" & account & "] Tag [" & tag & "] Value [" & value &
                          "] Currency [" & currency & "]")
        End Sub
        '! [accountsummary]

        '! [accountsummaryend]
        Public Sub accountSummaryEnd(reqId As Integer) Implements IBApi.EWrapper.accountSummaryEnd
            Console.WriteLine("AccountSummaryEnd - ReqId [" & reqId & "]")
        End Sub
        '! [accountsummaryend]

        '! [accountupdatemulti]
        Public Sub accountUpdateMulti(requestId As Integer, account As String, modelCode As String, key As String, value As String, currency As String) Implements IBApi.EWrapper.accountUpdateMulti
            Console.WriteLine("accountUpdateMulti. Id: " & requestId & ", Account: " & account & ", modelCode: " & modelCode & ", key: " & key & ", value: " & value & ", currency: " & currency)
        End Sub
        '! [accountupdatemulti]

        '! [accountupdatemultiend]
        Public Sub accountUpdateMultiEnd(requestId As Integer) Implements IBApi.EWrapper.accountUpdateMultiEnd
            Console.WriteLine("accountUpdateMultiEnd. id: " & requestId)
        End Sub
        '! [accountupdatemultiend]

        '! [bondcontractdetails]
        Public Sub bondContractDetails(reqId As Integer, contract As IBApi.ContractDetails) Implements IBApi.EWrapper.bondContractDetails
            Console.WriteLine("BondContractDetails begin. ReqId: " & reqId)
            printBondContractDetailsMsg(contract)
            Console.WriteLine("BondContractDetails end. ReqId: " & reqId)
        End Sub
        '! [bondcontractdetails]

        '! [commissionandfeesreport]
        Public Sub commissionAndFeesReport(commissionAndFeesReport As IBApi.CommissionAndFeesReport) Implements IBApi.EWrapper.commissionAndFeesReport
            Console.WriteLine("CommissionAndFeesReport - CommissionAndFeesReport [" & Util.DoubleMaxString(commissionAndFeesReport.CommissionAndFees) & " " & commissionAndFeesReport.Currency & "]")
        End Sub
        '! [commissionandfeesreport]

        '! [connectack]
        Public Sub connectAck() Implements IBApi.EWrapper.connectAck
            Console.WriteLine("ConnectAck")
            If socketClient.AsyncEConnect Then
                socketClient.startApi()
            End If
        End Sub
        '! [connectack]
        Public Sub connectionClosed() Implements IBApi.EWrapper.connectionClosed
            Console.WriteLine("ConnectionClosed")
        End Sub

        '! [contractdetails]
        Public Sub contractDetails(reqId As Integer, contractDetails As IBApi.ContractDetails) Implements IBApi.EWrapper.contractDetails
            Console.WriteLine("ContractDetails begin. ReqId: " & reqId)
            printContractMsg(contractDetails.Contract)
            printContractDetailsMsg(contractDetails)
            Console.WriteLine("ContractDetails end. ReqId: " & reqId)
        End Sub
        '! [contractdetails]

        Public Sub printContractMsg(contract As IBApi.Contract)
            Console.WriteLine(vbTab & "ConId: " & contract.ConId)
            Console.WriteLine(vbTab & "Symbol: " & contract.Symbol)
            Console.WriteLine(vbTab & "SecType: " & contract.SecType)
            Console.WriteLine(vbTab & "LastTradeDateOrContractMonth: " & contract.LastTradeDateOrContractMonth)
            Console.WriteLine(vbTab & "LastTradeDate: " & contract.LastTradeDate)
            Console.WriteLine(vbTab & "Strike: " & Util.DoubleMaxString(contract.Strike))
            Console.WriteLine(vbTab & "Right: " & contract.Right)
            Console.WriteLine(vbTab & "Multiplier: " & contract.Multiplier)
            Console.WriteLine(vbTab & "Exchange: " & contract.Exchange)
            Console.WriteLine(vbTab & "PrimaryExchange: " & contract.PrimaryExch)
            Console.WriteLine(vbTab & "Currency: " & contract.Currency)
            Console.WriteLine(vbTab & "LocalSymbol: " & contract.LocalSymbol)
            Console.WriteLine(vbTab & "TradingClass: " & contract.TradingClass)
        End Sub

        Public Sub printContractDetailsMsg(contractDetails As IBApi.ContractDetails)
            Console.WriteLine(vbTab & "MarketName: " & contractDetails.MarketName)
            Console.WriteLine(vbTab & "MinTick: " & Util.DoubleMaxString(contractDetails.MinTick))
            Console.WriteLine(vbTab & "PriceMagnifier: " & Util.IntMaxString(contractDetails.PriceMagnifier))
            Console.WriteLine(vbTab & "OrderTypes: " & contractDetails.OrderTypes)
            Console.WriteLine(vbTab & "ValidExchanges: " & contractDetails.ValidExchanges)
            Console.WriteLine(vbTab & "UnderConId: " & Util.IntMaxString(contractDetails.UnderConId))
            Console.WriteLine(vbTab & "LongName: " & contractDetails.LongName)
            Console.WriteLine(vbTab & "ContractMonth: " & contractDetails.ContractMonth)
            Console.WriteLine(vbTab & "Indystry: " & contractDetails.Industry)
            Console.WriteLine(vbTab & "Category: " & contractDetails.Category)
            Console.WriteLine(vbTab & "SubCategory: " & contractDetails.Subcategory)
            Console.WriteLine(vbTab & "TimeZoneId: " & contractDetails.TimeZoneId)
            Console.WriteLine(vbTab & "TradingHours: " & contractDetails.TradingHours)
            Console.WriteLine(vbTab & "LiquidHours: " & contractDetails.LiquidHours)
            Console.WriteLine(vbTab & "EvRule: " & contractDetails.EvRule)
            Console.WriteLine(vbTab & "EvMultiplier: " & Util.DoubleMaxString(contractDetails.EvMultiplier))
            Console.WriteLine(vbTab & "AggGroup: " & Util.IntMaxString(contractDetails.AggGroup))
            Console.WriteLine(vbTab & "UnderSymbol: " & contractDetails.UnderSymbol)
            Console.WriteLine(vbTab & "UnderSecType: " & contractDetails.UnderSecType)
            Console.WriteLine(vbTab & "MarketRuleIds: " & contractDetails.MarketRuleIds)
            Console.WriteLine(vbTab & "RealExpirationDate: " & contractDetails.RealExpirationDate)
            Console.WriteLine(vbTab & "LastTradeTime: " & contractDetails.LastTradeTime)
            Console.WriteLine(vbTab & "StockType: " & contractDetails.StockType)
            Console.WriteLine(vbTab & "MinSize: " & Util.DecimalMaxString(contractDetails.MinSize))
            Console.WriteLine(vbTab & "SizeIncrement: " & Util.DecimalMaxString(contractDetails.SizeIncrement))
            Console.WriteLine(vbTab & "SuggestedSizeIncrement: " & Util.DecimalMaxString(contractDetails.SuggestedSizeIncrement))

            If contractDetails.Contract.SecType = "FUND" Then
                Console.WriteLine(vbTab & "Fund Data: ")
                Console.WriteLine(vbTab & vbTab & "FundName: " & contractDetails.FundName)
                Console.WriteLine(vbTab & vbTab & "FundFamily: " & contractDetails.FundFamily)
                Console.WriteLine(vbTab & vbTab & "FundType: " & contractDetails.FundType)
                Console.WriteLine(vbTab & vbTab & "FundFrontLoad: " & contractDetails.FundFrontLoad)
                Console.WriteLine(vbTab & vbTab & "FundBackLoad: " & contractDetails.FundBackLoad)
                Console.WriteLine(vbTab & vbTab & "FundBackLoadTimeInterval: " & contractDetails.FundBackLoadTimeInterval)
                Console.WriteLine(vbTab & vbTab & "FundManagementFee: " & contractDetails.FundManagementFee)
                Console.WriteLine(vbTab & vbTab & "FundClosed: " & contractDetails.FundClosed)
                Console.WriteLine(vbTab & vbTab & "FundClosedForNewInvestors: " & contractDetails.FundClosedForNewInvestors)
                Console.WriteLine(vbTab & vbTab & "FundClosedForNewMoney: " & contractDetails.FundClosedForNewMoney)
                Console.WriteLine(vbTab & vbTab & "FundNotifyAmount: " & contractDetails.FundNotifyAmount)
                Console.WriteLine(vbTab & vbTab & "FundMinimumInitialPurchase: " & contractDetails.FundMinimumInitialPurchase)
                Console.WriteLine(vbTab & vbTab & "FundSubsequentMinimumPurchase: " & contractDetails.FundSubsequentMinimumPurchase)
                Console.WriteLine(vbTab & vbTab & "FundBlueSkyStates: " & contractDetails.FundBlueSkyStates)
                Console.WriteLine(vbTab & vbTab & "FundBlueSkyTerritories: " & contractDetails.FundBlueSkyTerritories)
                Console.WriteLine(vbTab & vbTab & "FundDistributionPolicyIndicator: " & CFundDistributionPolicyIndicator.getFundDistributionPolicyIndicatorName(contractDetails.FundDistributionPolicyIndicator))
                Console.WriteLine(vbTab & vbTab & "FundAssetType: " & CFundAssetType.getFundAssetTypeName(contractDetails.FundAssetType))
            End If

            printContractDetailsSecIdList(contractDetails.SecIdList)
            printContractDetailsIneligibilityReasonList(contractDetails.IneligibilityReasonList)
        End Sub

        Public Sub printContractDetailsSecIdList(secIdList As List(Of IBApi.TagValue))
            If Not secIdList Is Nothing Then
                Console.Write(vbTab & "SecIdList: {")
                For Each tagValue In secIdList
                    Console.Write(tagValue.Tag & "=" & tagValue.Value & ";")
                Next
                Console.WriteLine("}")
            End If
        End Sub

        Public Sub printContractDetailsIneligibilityReasonList(ineligibilityReasonList As List(Of IBApi.IneligibilityReason))
            If Not ineligibilityReasonList Is Nothing Then
                Console.Write(vbTab & "IneligibilityReasonList: {")
                For Each ineligibilityReason In ineligibilityReasonList
                    Console.Write("[id: " & ineligibilityReason.Id & ", description: " & ineligibilityReason.Description & "];")
                Next
                Console.WriteLine("}")
            End If
        End Sub

        Public Sub printBondContractDetailsMsg(contractDetails As IBApi.ContractDetails)
            Console.WriteLine(vbTab & "Symbol: " & contractDetails.Contract.Symbol)
            Console.WriteLine(vbTab & "SecType: " & contractDetails.Contract.SecType)
            Console.WriteLine(vbTab & "Cusip: " & contractDetails.Cusip)
            Console.WriteLine(vbTab & "Coupon: " & Util.DoubleMaxString(contractDetails.Coupon))
            Console.WriteLine(vbTab & "Maturity: " & contractDetails.Maturity)
            Console.WriteLine(vbTab & "IssueDate: " & contractDetails.IssueDate)
            Console.WriteLine(vbTab & "Ratings: " & contractDetails.Ratings)
            Console.WriteLine(vbTab & "BondType: " & contractDetails.BondType)
            Console.WriteLine(vbTab & "CouponType: " & contractDetails.CouponType)
            Console.WriteLine(vbTab & "Convertible: " & contractDetails.Convertible)
            Console.WriteLine(vbTab & "Callable: " & contractDetails.Callable)
            Console.WriteLine(vbTab & "Putable: " & contractDetails.Putable)
            Console.WriteLine(vbTab & "DescAppend: " & contractDetails.DescAppend)
            Console.WriteLine(vbTab & "Exchange: " & contractDetails.Contract.Exchange)
            Console.WriteLine(vbTab & "Currency: " & contractDetails.Contract.Currency)
            Console.WriteLine(vbTab & "MarketName: " & contractDetails.MarketName)
            Console.WriteLine(vbTab & "TradingClass: " & contractDetails.Contract.TradingClass)
            Console.WriteLine(vbTab & "ConId: " & contractDetails.Contract.ConId)
            Console.WriteLine(vbTab & "MinTick: " & Util.DoubleMaxString(contractDetails.MinTick))
            Console.WriteLine(vbTab & "OrderTypes: " & contractDetails.OrderTypes)
            Console.WriteLine(vbTab & "ValidExchanges: " & contractDetails.ValidExchanges)
            Console.WriteLine(vbTab & "NextOptionDate: " & contractDetails.NextOptionDate)
            Console.WriteLine(vbTab & "NextOptionType: " & contractDetails.NextOptionType)
            Console.WriteLine(vbTab & "NextOptionPartial: " & contractDetails.NextOptionPartial)
            Console.WriteLine(vbTab & "Notes: " & contractDetails.Notes)
            Console.WriteLine(vbTab & "Long Name: " & contractDetails.LongName)
            Console.WriteLine(vbTab & "TimeZoneId: " & contractDetails.TimeZoneId)
            Console.WriteLine(vbTab & "TradingHours: " & contractDetails.TradingHours)
            Console.WriteLine(vbTab & "LiquidHours: " & contractDetails.LiquidHours)
            Console.WriteLine(vbTab & "EvRule: " & contractDetails.EvRule)
            Console.WriteLine(vbTab & "EvMultiplier: " & Util.DoubleMaxString(contractDetails.EvMultiplier))
            Console.WriteLine(vbTab & "AggGroup: " & Util.IntMaxString(contractDetails.AggGroup))
            Console.WriteLine(vbTab & "MarketRuleIds: " & contractDetails.MarketRuleIds)
            Console.WriteLine(vbTab & "LastTradeTime: " & contractDetails.LastTradeTime)
            Console.WriteLine(vbTab & "MinSize: " & Util.DecimalMaxString(contractDetails.MinSize))
            Console.WriteLine(vbTab & "SizeIncrement: " & Util.DecimalMaxString(contractDetails.SizeIncrement))
            Console.WriteLine(vbTab & "SuggestedSizeIncrement: " & Util.DecimalMaxString(contractDetails.SuggestedSizeIncrement))
            printContractDetailsSecIdList(contractDetails.SecIdList)
        End Sub


        '! [contractdetailsend]
        Public Sub contractDetailsEnd(reqId As Integer) Implements IBApi.EWrapper.contractDetailsEnd
            Console.WriteLine("ContractDetailsEnd - ReqId [" & reqId & "]")
        End Sub
        '! [contractdetailsend]

        '! [currenttime]
        Public Sub currentTime(time As Long) Implements IBApi.EWrapper.currentTime
            Console.WriteLine("CurrentTime - " & time & " : " & Util.UnixSecondsToString(time, "MMM dd, yyyy HH:mm:ss"))
        End Sub
        '! [currenttime]

        Public Sub deltaNeutralValidation(reqId As Integer, deltaNeutralContract As IBApi.DeltaNeutralContract) Implements IBApi.EWrapper.deltaNeutralValidation
            Console.WriteLine("DeltaNeutralValidation - ReqId [" & reqId & "] DeltaNeutralContract [ConId:" & deltaNeutralContract.ConId & ", Price:" &
                          Util.DoubleMaxString(deltaNeutralContract.Price) & ", Delta:" & Util.DoubleMaxString(deltaNeutralContract.Delta) & "]")
        End Sub

        '! [displaygrouplist]
        Public Sub displayGroupList(reqId As Integer, groups As String) Implements IBApi.EWrapper.displayGroupList
            Console.WriteLine("DisplayGroupList - ReqId [" & reqId & "] Groups [" & groups & "]")
        End Sub
        '! [displaygrouplist]

        '! [displaygroupupdated]
        Public Sub displayGroupUpdated(reqId As Integer, contractInfo As String) Implements IBApi.EWrapper.displayGroupUpdated
            Console.WriteLine("DisplayGroupUpdated - ReqId [" & reqId & "] ContractInfo [" & contractInfo & "]")
        End Sub
        '! [displaygroupupdated]

        '! [errors]
        Public Sub [error](id As Integer, errorTime As Long, errorCode As Integer, errorMsg As String, advancedOrderRejectJson As String) Implements IBApi.EWrapper.error
            Dim errorTimeStr As String = If(errorTime > 0, Util.UnixMilliSecondsToString(errorTime, "yyyyMMdd-HH:mm:ss"), "")
            If advancedOrderRejectJson <> "" Then
                Console.WriteLine("Error - Id [" & id & "] ErrorTime [" & errorTimeStr & "] ErrorCode [" & errorCode & "] ErrorMsg [" & errorMsg & "] AdvancedOrderRejectJson [" & advancedOrderRejectJson & "]")
            Else
                Console.WriteLine("Error - Id [" & id & "] ErrorTime [" & errorTimeStr & "] ErrorCode [" & errorCode & "] ErrorMsg [" & errorMsg & "]")
            End If
        End Sub
        '! [errors]

        Public Sub [error](str As String) Implements IBApi.EWrapper.error
            Console.WriteLine("Error - Str [" & str & "]")
        End Sub

        Public Sub [error](e As System.Exception) Implements IBApi.EWrapper.error
            Console.WriteLine("Error - Exception [" & e.Message & "]")
        End Sub

        '! [execdetails]
        Public Sub execDetails(reqId As Integer, contract As IBApi.Contract, execution As IBApi.Execution) Implements IBApi.EWrapper.execDetails
            Console.WriteLine("ExecDetails - ReqId [" & reqId & "] Contract [" & contract.Symbol & ", " & contract.SecType &
                          "] Execution [PermId: " & Util.LongMaxString(execution.PermId) & ", ExecId: " & execution.ExecId & ", Price: " & Util.DoubleMaxString(execution.Price) & ", Exchange: " & execution.Exchange & ", Last Liquidity: " & execution.LastLiquidity.ToString() & ", Shares: " & Util.DecimalMaxString(execution.Shares) & ", Cum Qty: " & Util.DecimalMaxString(execution.CumQty) & ", Pending Price Revision: " & execution.PendingPriceRevision & ", Submitter: " & execution.Submitter & "]")
        End Sub
        '! [execdetails]
        '! [execdetailsend]
        Public Sub execDetailsEnd(reqId As Integer) Implements IBApi.EWrapper.execDetailsEnd
            Console.WriteLine("ExecDetailsEnd - ReqId [" & reqId & "]")
        End Sub
        '! [execdetailsend]
        '! [fundamentaldata]
        Public Sub fundamentalData(reqId As Integer, data As String) Implements IBApi.EWrapper.fundamentalData
            Console.WriteLine("FundamentalData - ReqId [" & reqId & "] Data [" & data & "]")
        End Sub
        '! [fundamentaldata]

        '! [historicaldata]
        Public Sub historicalData(reqId As Integer, bar As Bar) Implements IBApi.EWrapper.historicalData
            Console.WriteLine("HistoricalData - ReqId [" & reqId & "] Date [" & bar.Time & "] Open [" & Util.DoubleMaxString(bar.Open) & "] High [" &
                          Util.DoubleMaxString(bar.High) & "] Low [" & Util.DoubleMaxString(bar.Low) & "] Volume [" & Util.DecimalMaxString(bar.Volume) & "] Count [" & Util.IntMaxString(bar.Count) &
                          "] WAP [" & Util.DecimalMaxString(bar.WAP) & "]")
        End Sub
        '! [historicaldata]

        '! [historicalDataUpdate]
        Public Sub historicalDataUpdate(reqId As Integer, bar As Bar) Implements IBApi.EWrapper.historicalDataUpdate
            Console.WriteLine("HistoricalDataUpdate - ReqId [" & reqId & "] Date [" & bar.Time & "] Open [" & Util.DoubleMaxString(bar.Open) & "] High [" &
                          Util.DoubleMaxString(bar.High) & "] Low [" & Util.DoubleMaxString(bar.Low) & "] Volume [" & Util.DecimalMaxString(bar.Volume) & "] Count [" & Util.IntMaxString(bar.Count) &
                          "] WAP [" & Util.DecimalMaxString(bar.WAP) & "]")
        End Sub
        '! [historicalDataUpdate]

        '! [historicaldataend]
        Public Sub historicalDataEnd(reqId As Integer, start As String, [end] As String) Implements IBApi.EWrapper.historicalDataEnd
            Console.WriteLine("HistoricalDataEnd - ReqId [" & reqId & "] Start [" & start & "] End [" & [end] & "]")
        End Sub
        '! [historicaldataend]

        '! [managedaccounts]
        Public Sub managedAccounts(accountsList As String) Implements IBApi.EWrapper.managedAccounts
            Console.WriteLine("ManagedAccounts - AccountsList [" & accountsList & "]")
        End Sub
        '! [managedaccounts]

        '! [marketdatatype]
        Public Sub marketDataType(reqId As Integer, marketDataType As Integer) Implements IBApi.EWrapper.marketDataType
            Console.WriteLine("MarketDataType - ReqId [" & reqId & "] MarketDataType [" & marketDataType & "]")
        End Sub
        '! [marketdatatype]

        '! [nextvalidid]
        Public Sub nextValidId(orderId As Integer) Implements IBApi.EWrapper.nextValidId
            Console.WriteLine("NextValidId - OrderId [" & orderId & "]")
            nextOrderId = orderId
        End Sub
        '! [nextvalidid]

        '! [openorder]
        Public Sub openOrder(orderId As Integer, contract As IBApi.Contract, order As IBApi.Order, orderState As IBApi.OrderState) Implements IBApi.EWrapper.openOrder
            Console.WriteLine("OpenOrder. PermID: " & Util.LongMaxString(order.PermId) & ", ClientId: " & Util.IntMaxString(order.ClientId) & ", OrderId: " & Util.IntMaxString(orderId) &
                              ", Account: " & order.Account & ", Symbol: " & contract.Symbol & ", SecType: " & contract.SecType & " , Exchange: " & contract.Exchange & ", Action: " & order.Action &
                              ", OrderType: " & order.OrderType & ", TotalQty: " & Util.DecimalMaxString(order.TotalQuantity) & ", CashQty: " & Util.DoubleMaxString(order.CashQty) & ", LmtPrice: " &
                              Util.DoubleMaxString(order.LmtPrice) & ", AuxPrice: " & Util.DoubleMaxString(order.AuxPrice) & ", Status: " & orderState.Status &
                              ", MinTradeQty: " & Util.IntMaxString(order.MinTradeQty) & ", MinCompeteSize: " & Util.IntMaxString(order.MinCompeteSize) &
                              ", CompeteAgainstBestOffset: " & If(order.CompeteAgainstBestOffset = Order.COMPETE_AGAINST_BEST_OFFSET_UP_TO_MID, "UpToMid", Util.DoubleMaxString(order.CompeteAgainstBestOffset)) &
                              ", MidOffsetAtWhole: " & Util.DoubleMaxString(order.MidOffsetAtWhole) & ", MidOffsetAtHalf: " & Util.DoubleMaxString(order.MidOffsetAtHalf) &
                              ", FAGroup: " & order.FaGroup & ", FAMethod: " & order.FaMethod & ", CustAcct: " & order.CustomerAccount & ", ProfCust: " & order.ProfessionalCustomer &
                              ", BondAccruedInterest: " & order.BondAccruedInterest & ", IncludeOvernight: " & order.IncludeOvernight & ", ExtOperator: " & order.ExtOperator &
                              ", ManualOrderIndicator: " & Util.IntMaxString(order.ManualOrderIndicator) & ", Submitter: " & order.Submitter & ", ImbalanceOnly: " & order.ImbalanceOnly)

            If order.WhatIf Then
                Console.WriteLine("WhatIf. InitMarginBefore: " & orderState.InitMarginBefore & ", MaintMarginBefore: " & orderState.MaintMarginBefore & ", EquityWithLoanBefore: " & orderState.EquityWithLoanBefore &
                    ", InitMarginChange: " & orderState.InitMarginChange & ", MaintMarginChange: " + orderState.MaintMarginChange & ", EquityWithLoanChange: " & orderState.EquityWithLoanChange &
                    ", InitMarginAfter: " & orderState.InitMarginAfter & ", MaintMarginAfter: " & orderState.MaintMarginAfter & ", EquityWithLoanAfter: " & orderState.EquityWithLoanAfter &
                    ", CommissionAndFees: " & Util.DoubleMaxString(orderState.CommissionAndFees) & ", MinCommissionAndFees: " & Util.DoubleMaxString(orderState.MinCommissionAndFees) & ", MaxCommissionAndFees: " & Util.DoubleMaxString(orderState.MaxCommissionAndFees) &
                    ", CommissionAndFeesCurrency: " & orderState.CommissionAndFeesCurrency & ", MarginCurrency: " & orderState.MarginCurrency &
                    ", InitMarginBeforeOutsideRTH: " & Util.DoubleMaxString(orderState.InitMarginBeforeOutsideRTH) & ", MaintMarginBeforeOutsideRTH: " & Util.DoubleMaxString(orderState.MaintMarginBeforeOutsideRTH) & ", EquityWithLoanBeforeOutsideRTH: " & Util.DoubleMaxString(orderState.EquityWithLoanBeforeOutsideRTH) &
                    ", InitMarginChangeOutsideRTH: " & Util.DoubleMaxString(orderState.InitMarginChangeOutsideRTH) & ", MaintMarginChangeOutsideRTH: " & Util.DoubleMaxString(orderState.MaintMarginChangeOutsideRTH) & ", EquityWithLoanChangeOutsideRTH: " & Util.DoubleMaxString(orderState.EquityWithLoanChangeOutsideRTH) &
                    ", InitMarginAfterOutsideRTH: " & Util.DoubleMaxString(orderState.InitMarginAfterOutsideRTH) & ", MaintMarginAfterOutsideRTH: " & Util.DoubleMaxString(orderState.MaintMarginAfterOutsideRTH) & ", EquityWithLoanAfterOutsideRTH: " & Util.DoubleMaxString(orderState.EquityWithLoanAfterOutsideRTH) &
                    ", SuggestedSize: " & Util.DecimalMaxString(orderState.SuggestedSize) & ", RejectReason: " & orderState.RejectReason & ", WarningText: " & orderState.WarningText)
                printOrderAllocationsList(orderState.OrderAllocations)
            End If
        End Sub
        '! [openorder]

        Public Sub printOrderAllocationsList(orderAllocationList As List(Of IBApi.OrderAllocation))
            If Not orderAllocationList Is Nothing And orderAllocationList.Count > 0 Then
                Console.Write(vbTab & "OrderAllocationList: {")
                For Each orderAllocation In orderAllocationList
                    Console.Write("Account: " & orderAllocation.Account & ", Position: " & Util.DecimalMaxString(orderAllocation.Position) &
                        ", PositionDesired: " & Util.DecimalMaxString(orderAllocation.PositionDesired) & ", PositionAfter: " & Util.DecimalMaxString(orderAllocation.PositionAfter) &
                        ", DesiredAllocQty: " & Util.DecimalMaxString(orderAllocation.DesiredAllocQty) & ", AllowedAllocQty: " & Util.DecimalMaxString(orderAllocation.AllowedAllocQty) &
                        ", IsMonetary: " & orderAllocation.IsMonetary & "; ")
                Next
                Console.WriteLine("}")
            End If
        End Sub

        '! [openorderend]
        Public Sub openOrderEnd() Implements IBApi.EWrapper.openOrderEnd
            Console.WriteLine("OpenOrderEnd")
        End Sub
        '! [openorderend]

        '! [orderstatus]
        Public Sub orderStatus(orderId As Integer, status As String, filled As Decimal, remaining As Decimal, avgFillPrice As Double, permId As Long, parentId As Integer, lastFillPrice As Double, clientId As Integer, whyHeld As String, mktCapPrice As Double) Implements IBApi.EWrapper.orderStatus
            Console.WriteLine("OrderStatus. Id: " & orderId & ", Status: " & status & ", Filled: " & Util.DecimalMaxString(filled) & ", Remaining: " & Util.DecimalMaxString(remaining) &
                ", AvgFillPrice: " & Util.DoubleMaxString(avgFillPrice) & ", PermId: " & Util.LongMaxString(permId) & ", ParentId: " & Util.IntMaxString(parentId) &
                ", LastFillPrice: " & Util.DoubleMaxString(lastFillPrice) & ", ClientId: " & Util.IntMaxString(clientId) & ", WhyHeld: " & whyHeld & ", mktCapPrice: " & Util.DoubleMaxString(mktCapPrice))
        End Sub
        '! [orderstatus]

        '! [position]
        Public Sub position(account As String, contract As IBApi.Contract, pos As Decimal, avgCost As Double) Implements IBApi.EWrapper.position
            Console.WriteLine("Position. " & account & " - Symbol: " & contract.Symbol & ", SecType: " & contract.SecType & ", Currency: " &
                          contract.Currency & ", Position: " & Util.DecimalMaxString(pos) & ", Avg cost: " & Util.DoubleMaxString(avgCost))
        End Sub
        '! [position]

        '! [positionend]
        Public Sub positionEnd() Implements IBApi.EWrapper.positionEnd
            Console.WriteLine("PositionEnd")
        End Sub
        '! [positionend]

        '! [positionmulti]
        Public Sub positionMulti(requestId As Integer, account As String, modelCode As String, contract As Contract, pos As Decimal, avgCost As Double) Implements IBApi.EWrapper.positionMulti
            Console.WriteLine("PositionMulti. Id: " & requestId & ", Account: " & account & ", ModelCode: " & modelCode & ", Contract: " & contract.Symbol & ", pos: " & Util.DecimalMaxString(pos) &
                              ", avgCost: " & Util.DoubleMaxString(avgCost))
        End Sub
        '! [positionmulti]

        '! [positionmultiend]
        Public Sub positionMultiEnd(requestId As Integer) Implements IBApi.EWrapper.positionMultiEnd
            Console.WriteLine("PositionMultiEnd")
        End Sub
        '! [positionmultiend]

        '! [realtimebar]
        Public Sub realtimeBar(reqId As Integer, time As Long, open As Double, high As Double, low As Double, close As Double, volume As Decimal, WAP As Decimal, count As Integer) Implements IBApi.EWrapper.realtimeBar
            Console.WriteLine("RealTimeBars. " & reqId & " - Time: " & Util.LongMaxString(time) & ", Open: " & Util.DoubleMaxString(open) & ", High: " & Util.DoubleMaxString(high) &
                              ", Low: " & Util.DoubleMaxString(low) & ", Close: " & Util.DoubleMaxString(close) & ", Volume: " & Util.DecimalMaxString(volume) & ", Count: " &
                              Util.IntMaxString(count) & ", WAP: " & Util.DecimalMaxString(WAP))
        End Sub
        '! [realtimebar]

        '! [receivefa]
        Public Sub receiveFA(faDataType As Integer, faXmlData As String) Implements IBApi.EWrapper.receiveFA
            Console.WriteLine("Receing FA: " & faDataType & " - " & faXmlData)
        End Sub
        '! [receivefa]

        '! [scannerdata]
        Public Sub scannerData(reqId As Integer, rank As Integer, contractDetails As IBApi.ContractDetails, distance As String, benchmark As String, projection As String, legsStr As String) Implements IBApi.EWrapper.scannerData
            Console.WriteLine("ScannerData. " & reqId & " - Rank: " & rank & ", Symbol: " & contractDetails.Contract.Symbol & ", SecType: " &
                          contractDetails.Contract.SecType & ", Currency: " & contractDetails.Contract.Currency & ", Distance: " & distance &
                          ", Benchmark: " & benchmark & ", Projection: " & projection & ", Legs String: " & legsStr)
        End Sub
        '! [scannerdata]

        '! [scannerdataend]
        Public Sub scannerDataEnd(reqId As Integer) Implements IBApi.EWrapper.scannerDataEnd
            Console.WriteLine("ScannerDataEnd. " & reqId & "\n")
        End Sub
        '! [scannerdataend]

        '! [scannerparameters]
        Public Sub scannerParameters(xml As String) Implements IBApi.EWrapper.scannerParameters
            Console.WriteLine("ScannerParameters. " & xml & "\n")
        End Sub
        '! [scannerparameters]

        '! [tickEFP]
        Public Sub tickEFP(tickerId As Integer, tickType As Integer, basisPoints As Double, formattedBasisPoints As String, impliedFuture As Double, holdDays As Integer, futureLastTradeDate As String, dividendImpact As Double, dividendsToLastTradeDate As Double) Implements IBApi.EWrapper.tickEFP
            Console.WriteLine("TickEFP. " & tickerId & ", Type: " & tickType & ", BasisPoints: " & Util.DoubleMaxString(basisPoints) & ", FormattedBasisPoints: " &
                          formattedBasisPoints & ", ImpliedFuture: " & Util.DoubleMaxString(impliedFuture) & ", HoldDays: " & Util.IntMaxString(holdDays) & ", FutureLastTradeDate: " &
                          futureLastTradeDate & ", DividendImpact: " & Util.DoubleMaxString(dividendImpact) & ", DividendsToLastTradeDate: " & Util.DoubleMaxString(dividendsToLastTradeDate))
        End Sub
        '! [tickefp]

        '! [tickgeneric]
        Public Sub tickGeneric(tickerId As Integer, field As Integer, value As Double) Implements IBApi.EWrapper.tickGeneric
            Console.WriteLine("Tick Generic. Ticker Id:" & tickerId & ", Field: " & field & ", Value: " & Util.DoubleMaxString(value))
        End Sub
        '! [tickgeneric]

        '! [tickoptioncomputation]
        Public Sub tickOptionComputation(tickerId As Integer, field As Integer, tickAttrib As Integer, impliedVolatility As Double, delta As Double, optPrice As Double, pvDividend As Double, gamma As Double, vega As Double, theta As Double, undPrice As Double) Implements IBApi.EWrapper.tickOptionComputation
            Console.WriteLine("TickOptionComputation. TickerId: " & tickerId & ", field: " & field & ", TickAttrib: " & Util.IntMaxString(tickAttrib) & ", ImpliedVolatility: " & Util.DoubleMaxString(impliedVolatility) &
                        ", Delta: " & Util.DoubleMaxString(delta) & ", OptionPrice: " & Util.DoubleMaxString(optPrice) & ", pvDividend: " & Util.DoubleMaxString(pvDividend) &
                        ", Gamma: " & Util.DoubleMaxString(gamma) & ", Vega: " & Util.DoubleMaxString(vega) & ", Theta: " & Util.DoubleMaxString(theta) & ", UnderlyingPrice: " & Util.DoubleMaxString(undPrice))
        End Sub
        '! [tickoptioncomputation]

        '! [tickprice]
        Public Sub tickPrice(tickerId As Integer, field As Integer, price As Double, attribs As TickAttrib) Implements IBApi.EWrapper.tickPrice
            Console.WriteLine("TickPrice - TickerId [" & CStr(tickerId) & "] Field [" & TickType.getField(field) & "] Price [" & Util.DoubleMaxString(price) & "] PreOpen [" & attribs.PreOpen & "]")
        End Sub
        '! [tickprice]

        '! [ticksize]
        Public Sub tickSize(tickerId As Integer, field As Integer, size As Decimal) Implements IBApi.EWrapper.tickSize
            Console.WriteLine("Tick Size. Ticker Id:" & CStr(tickerId) & ", Field: " & TickType.getField(field) & ", Size: " & Util.DecimalMaxString(size))
        End Sub
        '! [ticksize]

        '! [ticksnapshotend]
        Public Sub tickSnapshotEnd(tickerId As Integer) Implements IBApi.EWrapper.tickSnapshotEnd
            Console.WriteLine("TickSnapshotEnd: " & CStr(tickerId))
        End Sub
        '! [ticksnapshotend]

        '! [tickstring]
        Public Sub tickString(tickerId As Integer, field As Integer, value As String) Implements IBApi.EWrapper.tickString
            Console.WriteLine("Tick string. Ticker Id:" & CStr(tickerId) & ", Type: " & TickType.getField(field) & ", Value: " & value)
        End Sub
        '! [tickstring]

        '! [updateaccounttime]
        Public Sub updateAccountTime(timestamp As String) Implements IBApi.EWrapper.updateAccountTime
            Console.WriteLine("UpdateAccountTime. Time: " & timestamp)
        End Sub
        '! [updateaccounttime]

        '! [updateaccountvalue]
        Public Sub updateAccountValue(key As String, value As String, currency As String, accountName As String) Implements IBApi.EWrapper.updateAccountValue
            Console.WriteLine("UpdateAccountValue. Key: " & key & ", Value: " & value & ", Currency: " & currency & ", AccountName: " & accountName)
        End Sub
        '! [updateaccountvalue]

        '! [updatemktdepth]
        Public Sub updateMktDepth(tickerId As Integer, position As Integer, operation As Integer, side As Integer, price As Double, size As Decimal) Implements IBApi.EWrapper.updateMktDepth
            Console.WriteLine("UpdateMarketDepth. " & CStr(tickerId) & " - Position: " & CStr(position) & ", Operation: " & CStr(operation) & ", Side: " & CStr(side) &
                          ", Price: " & Util.DoubleMaxString(price) & ", Size: " & Util.DecimalMaxString(size))
        End Sub
        '! [updatemktdepth]

        '! [updatemktdepthl2]
        Public Sub updateMktDepthL2(tickerId As Integer, position As Integer, marketMaker As String, operation As Integer, side As Integer, price As Double, size As Decimal, isSmartDepth As Boolean) Implements IBApi.EWrapper.updateMktDepthL2
            Console.WriteLine("UpdateMarketDepthL2. " & CStr(tickerId) & " MarketMaker: " & marketMaker & ", Position: " & CStr(position) & ", Operation: " & CStr(operation) & ", Side: " & CStr(side) &
                          ", Price: " & Util.DoubleMaxString(price) & ", Size: " & Util.DecimalMaxString(size) & ", isSmartDepth: " & CStr(isSmartDepth))
        End Sub
        '! [updatemktdepthl2]

        '! [updatenewsbulletin]
        Public Sub updateNewsBulletin(msgId As Integer, msgType As Integer, message As String, origExchange As String) Implements IBApi.EWrapper.updateNewsBulletin
            Console.WriteLine("News Bulletins. " & msgId & " - Type: " & msgType & ", Message: " & message & ", Exchange of Origin: " & origExchange)
        End Sub
        '! [updatenewsbulletin]

        '! [updateportfolio]
        Public Sub updatePortfolio(contract As IBApi.Contract, position As Decimal, marketPrice As Double, marketValue As Double, averageCost As Double, unrealizedPNL As Double, realizedPNL As Double, accountName As String) Implements IBApi.EWrapper.updatePortfolio
            Console.WriteLine("UpdatePortfolio. " & contract.Symbol & ", " & contract.SecType & " @ " & contract.Exchange &
                ": Position: " & Util.DecimalMaxString(position) & ", MarketPrice: " & Util.DoubleMaxString(marketPrice) & ", MarketValue: " & Util.DoubleMaxString(marketValue) &
                ", AverageCost: " & Util.DoubleMaxString(averageCost) & ", UnrealizedPNL: " & Util.DoubleMaxString(unrealizedPNL) & ", RealizedPNL: " & Util.DoubleMaxString(realizedPNL) & ", AccountName: " & accountName)
        End Sub
        '! [updateportfolio]

        Public Sub verifyAndAuthCompleted(isSuccessful As Boolean, errorText As String) Implements IBApi.EWrapper.verifyAndAuthCompleted
            Console.WriteLine("verifyAndAuthCompleted. IsSuccessful: " & isSuccessful & " - Error: " & errorText)
        End Sub

        Public Sub verifyAndAuthMessageAPI(apiData As String, xyzChallenge As String) Implements IBApi.EWrapper.verifyAndAuthMessageAPI
            Console.WriteLine("verifyAndAuthMessageAPI: " & apiData & " " & xyzChallenge)
        End Sub

        Public Sub verifyCompleted(isSuccessful As Boolean, errorText As String) Implements IBApi.EWrapper.verifyCompleted
            Console.WriteLine("verifyCompleted. IsSuccessfule: " & isSuccessful & " - Error: " & errorText)
        End Sub

        Public Sub verifyMessageAPI(apiData As String) Implements IBApi.EWrapper.verifyMessageAPI
            Console.WriteLine("verifyMessageAPI: " & apiData)
        End Sub

        '! [securityDefinitionOptionParameter]
        Public Sub securityDefinitionOptionParameter(reqId As Integer, exchange As String, underlyingConId As Integer, tradingClass As String, multiplier As String, expirations As HashSet(Of String), strikes As HashSet(Of Double)) Implements EWrapper.securityDefinitionOptionParameter
            Console.WriteLine("securityDefinitionOptionParameter: " & reqId & " tradingClass: " & tradingClass & " multiplier: ")
        End Sub
        '! [securityDefinitionOptionParameter]

        '! [securityDefinitionOptionParameterEnd]
        Public Sub securityDefinitionOptionParameterEnd(reqId As Integer) Implements EWrapper.securityDefinitionOptionParameterEnd
            Console.WriteLine("Called securityDefinitionParameterEnd")
        End Sub
        '! [securityDefinitionOptionParameterEnd]

        '! [softDollarTiers]
        Public Sub softDollarTiers(reqid As Integer, tiers As SoftDollarTier()) Implements EWrapper.softDollarTiers
            Console.WriteLine("Soft Dollar Tiers:")

            For Each tier In tiers
                Console.WriteLine(tier.DisplayName)
            Next
        End Sub
        '! [softDollarTiers]

        '! [familyCodes]
        Public Sub familyCodes(familyCodes As FamilyCode()) Implements EWrapper.familyCodes
            Console.WriteLine("Family Codes:")

            For Each familyCode In familyCodes
                Console.WriteLine("Account ID: " & familyCode.AccountID & " Family Code Str: " & familyCode.FamilyCodeStr)
            Next
        End Sub
        '! [familyCodes]

        '! [symbolSamples]
        Public Sub symbolSamples(reqId As Integer, contractDescriptions As ContractDescription()) Implements EWrapper.symbolSamples
            Dim derivSecTypes As String

            Console.WriteLine("Symbol Samples. Request Id: " & reqId)

            For Each contractDescription In contractDescriptions
                derivSecTypes = ""
                For Each derivSecType In contractDescription.DerivativeSecTypes
                    derivSecTypes += derivSecType
                    derivSecTypes += " "
                Next
                Console.WriteLine("Contract conId: " & contractDescription.Contract.ConId & ", symbol: " & contractDescription.Contract.Symbol &
                                  ", secType: " & contractDescription.Contract.SecType & ", primExchange: " & contractDescription.Contract.PrimaryExch &
                                  ", currency: " & contractDescription.Contract.Currency & ", derivativeSecTypes: " & derivSecTypes &
                                  ", description: " & contractDescription.Contract.Description & ", issuerId: " & contractDescription.Contract.IssuerId)
            Next
        End Sub
        '! [symbolSamples]

        '! [mktDepthExchanges]
        Public Sub mktDepthExchanges(depthMktDataDescriptions As DepthMktDataDescription()) Implements EWrapper.mktDepthExchanges
            Console.WriteLine("Market Depth Exchanges:")

            For Each depthMktDataDescription In depthMktDataDescriptions
                Console.WriteLine("Depth Market Data Descriprion. Exchange: " & depthMktDataDescription.Exchange &
                                  " Security Type: " & depthMktDataDescription.SecType &
                                  " Listing Exch: " & depthMktDataDescription.ListingExch &
                                  " Service Data Type: " & depthMktDataDescription.ServiceDataType &
                                  "  Agg Group: " & Util.IntMaxString(depthMktDataDescription.AggGroup))
            Next
        End Sub
        '! [mktDepthExchanges]

        '! [tickNews]
        Public Sub tickNews(tickerId As Integer, timeStamp As Long, providerCode As String, articleId As String, headline As String, extraData As String) Implements IBApi.EWrapper.tickNews
            Console.WriteLine("Tick News. Ticker Id: " & tickerId & ", Time Stamp: " & Util.LongMaxString(timeStamp) & ", Provider Code: " & providerCode & ", Article Id: " & articleId & ", Headline: " & headline & ", Extra Data: " & extraData)
        End Sub
        '! [tickNews]

        '! [smartcomponents]
        Public Sub smartComponents(reqId As Integer, theMap As Dictionary(Of Integer, KeyValuePair(Of String, Char))) Implements EWrapper.smartComponents
            Dim sb As New StringBuilder

            sb.AppendFormat("==== Smart Components Begin (total={0}) reqId = {1} ===={2}", theMap.Count, reqId, Environment.NewLine)

            For Each item In theMap
                sb.AppendFormat("bit number: {0}, exchange: {1}, exchange letter: {2}{3}", item.Key, item.Value.Key, item.Value.Value, Environment.NewLine)
            Next

            sb.AppendFormat("==== Smart Components Begin (total={0}) reqId = {1} ===={2}", theMap.Count, reqId, Environment.NewLine)

            Console.WriteLine(sb)
        End Sub
        '! [smartcomponents]

        '! [tickReqParams]
        Public Sub tickReqParams(tickerId As Integer, minTick As Double, bboExchange As String, snapshotPermissions As Integer) Implements EWrapper.tickReqParams
            Console.WriteLine("id={0} minTick = {1} bboExchange = {2} snapshotPermissions = {3}", tickerId, Util.DoubleMaxString(minTick), bboExchange, Util.IntMaxString(snapshotPermissions))

            Me.BboExchange = bboExchange
        End Sub
        '! [tickReqParams]

        '! [newsProviders]
        Public Sub newsProviders(newsProviders As NewsProvider()) Implements EWrapper.newsProviders
            Console.WriteLine("News Providers")

            For Each newsProvider In newsProviders
                Console.WriteLine("News Provider: providerCode - " & newsProvider.ProviderCode & ", providerName - " & newsProvider.ProviderName)
            Next
        End Sub
        '! [newsProviders]

        '! [newsArticle]
        Public Sub newsArticle(requestId As Integer, articleType As Integer, articleText As String) Implements EWrapper.newsArticle
            Console.WriteLine("News Article. Request Id: " & requestId & ", Article Type: " & articleType)

            If articleType = 0 Then
                Console.WriteLine("News Article Text: " & articleText)
            ElseIf articleType = 1 Then
                Console.WriteLine("News Article Text: article text is binary/pdf and cannot be displayed")
            End If
        End Sub
        '! [newsArticle]

        '! [historicalNews]
        Public Sub historicalNews(requestId As Integer, time As String, providerCode As String, articleId As String, headline As String) Implements IBApi.EWrapper.historicalNews
            Console.WriteLine("Historical News. Request Id: " & requestId & ", Time: " & time & ", Provider Code: " & providerCode & ", Article Id: " & articleId & ", Headline: " & headline)
        End Sub
        '! [historicalNews]

        '! [historicalNewsEnd]
        Public Sub historicalNewsEnd(requestId As Integer, hasMore As Boolean) Implements IBApi.EWrapper.historicalNewsEnd
            Console.WriteLine("Historical News End. Request Id: " & requestId & ", Has More: " & hasMore)
        End Sub
        '! [historicalNewsEnd]

        '! [headTimestamp]
        Public Sub headTimestamp(requestId As Integer, timeStamp As String) Implements IBApi.EWrapper.headTimestamp
            Console.WriteLine("Head time stamp. Request Id: {0}, Head time stamp: {1}", requestId, timeStamp)
        End Sub
        '! [headTimestamp]

        '! [histogramData]
        Public Sub histogramData(reqId As Integer, data As HistogramEntry()) Implements EWrapper.histogramData
            Console.WriteLine("Histogram data. Request Id: {0}, data size: {1}", reqId, data.Length)
            data.ToList().ForEach(Sub(i) Console.WriteLine(vbTab & "Price: {0}, Size: {1}", Util.DoubleMaxString(i.Price), Util.DecimalMaxString(i.Size)))
        End Sub
        '! [histogramData]

        '! [rerouteMktDataReq]
        Public Sub rerouteMktDataReq(reqId As Integer, conId As Integer, exchange As String) Implements IBApi.EWrapper.rerouteMktDataReq
            Console.WriteLine("Re-route market data request. Req Id: {0}, Con Id: {1}, Exchange: {2}", reqId, conId, exchange)
        End Sub
        '! [rerouteMktDataReq]

        '! [rerouteMktDepthReq]
        Public Sub rerouteMktDepthReq(reqId As Integer, conId As Integer, exchange As String) Implements IBApi.EWrapper.rerouteMktDepthReq
            Console.WriteLine("Re-route market depth request. Req Id: {0}, Con Id: {1}, Exchange: {2}", reqId, conId, exchange)
        End Sub
        '! [rerouteMktDepthReq]

        '! [marketRule]
        Public Sub marketRule(marketRuleId As Integer, priceIncrements As PriceIncrement()) Implements EWrapper.marketRule
            Console.WriteLine("Market Rule Id:" & marketRuleId)

            For Each priceIncrement In priceIncrements
                Console.WriteLine("LowEdge: " & Util.DoubleMaxString(priceIncrement.LowEdge) & " Increment: " & Util.DoubleMaxString(priceIncrement.Increment))
            Next
        End Sub
        '! [marketRule]

        '! [pnl]
        Public Sub pnl(reqId As Integer, dailyPnL As Double, unrealizedPnL As Double, realizedPnL As Double) Implements EWrapper.pnl
            Console.WriteLine("PnL. Request Id: {0}, daily PnL: {1}, unrealized PnL: {2}, realized PnL: {3}", reqId, Util.DoubleMaxString(dailyPnL), Util.DoubleMaxString(unrealizedPnL), Util.DoubleMaxString(realizedPnL))
        End Sub
        '! [pnl]

        '! [pnlsingle]
        Public Sub pnlSingle(reqId As Integer, pos As Decimal, dailyPnL As Double, unrealizedPnL As Double, realizedPnL As Double, value As Double) Implements EWrapper.pnlSingle
            Console.WriteLine("PnL Single. Request Id: {0}, pos: {1}, daily PnL: {2}, unrealized PnL: {3}, realized PnL: {4}, value: {5}", reqId, Util.DecimalMaxString(pos),
                              Util.DoubleMaxString(dailyPnL), Util.DoubleMaxString(unrealizedPnL), Util.DoubleMaxString(realizedPnL), Util.DoubleMaxString(value))
        End Sub
        '! [pnlsingle]

        '! [historicalticks]
        Public Sub historicalTick(reqId As Integer, ticks As HistoricalTick(), done As Boolean) Implements EWrapper.historicalTicks
            For Each tick In ticks
                Console.WriteLine("Historical Tick. Request Id: {0}, Time: {1}, Price: {2}, Size: {3}", reqId, Util.UnixSecondsToString(tick.Time, "yyyyMMdd-HH:mm:ss"),
                                  Util.DoubleMaxString(tick.Price), Util.DecimalMaxString(tick.Size))
            Next
        End Sub
        '! [historicalticks]

        '! [historicalticksbidask]
        Public Sub historicalTickBidAsk(reqId As Integer, ticks As HistoricalTickBidAsk(), done As Boolean) Implements EWrapper.historicalTicksBidAsk
            For Each tick In ticks
                Console.WriteLine("Historical Tick Bid/Ask. Request Id: {0}, Time: {1}, Price Bid: {2}, Price Ask: {3}, Size Bid: {4}, Size Ask: {5}, Bid/Ask Tick Attribs: {6}",
                    reqId, Util.UnixSecondsToString(tick.Time, "yyyyMMdd-HH:mm:ss"), Util.DoubleMaxString(tick.PriceBid), Util.DoubleMaxString(tick.PriceAsk),
                    Util.DecimalMaxString(tick.SizeBid), Util.DecimalMaxString(tick.SizeAsk), tick.TickAttribBidAsk.ToString())
            Next
        End Sub
        '! [historicalticksbidask]

        '! [historicaltickslast]
        Public Sub historicalTickLast(reqId As Integer, ticks As HistoricalTickLast(), done As Boolean) Implements EWrapper.historicalTicksLast
            For Each tick In ticks
                Console.WriteLine("Historical Tick Last. Request Id: {0}, Time: {1}, Price: {2}, Size: {3}, Exchange: {4}, Special Conditions: {5}, Last Tick Attribs: {6}",
                    reqId, Util.UnixSecondsToString(tick.Time, "yyyyMMdd-HH:mm:ss"), Util.DoubleMaxString(tick.Price), Util.DecimalMaxString(tick.Size), tick.Exchange,
                    tick.SpecialConditions, tick.TickAttribLast.ToString())
            Next
        End Sub
        '! [historicaltickslast]

        '! [tickbytickalllast]
        Public Sub tickByTickAllLast(reqId As Integer, tickType As Integer, time As Long, price As Double, size As Decimal, tickAttribLast As TickAttribLast, exchange As String, specialConditions As String) Implements EWrapper.tickByTickAllLast
            Dim tickTypeStr As String
            If tickType = 1 Then
                tickTypeStr = "Last"
            Else
                tickTypeStr = "AllLast"
            End If
            Console.WriteLine("Tick-By-Tick. Request Id: {0}, TickType: {1}, Time: {2}, Price: {3}, Size: {4}, Exchange: {5}, Special Conditions: {6}, PastLimit: {7}, Unreported: {8}",
                reqId, tickTypeStr, Util.UnixSecondsToString(time, "yyyyMMdd-HH:mm:ss"), Util.DoubleMaxString(price), Util.DecimalMaxString(size), exchange, specialConditions,
                tickAttribLast.PastLimit, tickAttribLast.Unreported)
        End Sub
        '! [tickbytickalllast]

        '! [tickbytickbidask]
        Public Sub tickByTickBidAsk(reqId As Integer, time As Long, bidPrice As Double, askPrice As Double, bidSize As Decimal, askSize As Decimal, tickAttribBidAsk As TickAttribBidAsk) Implements EWrapper.tickByTickBidAsk
            Console.WriteLine("Tick-By-Tick. Request Id: {0}, TickType: BidAsk, Time: {1}, BidPrice: {2}, AskPrice: {3}, BidSize: {4}, AskSize: {5}, BidPastLow: {6}, AskPastHigh: {7}",
                reqId, Util.UnixSecondsToString(time, "yyyyMMdd-HH:mm:ss"), Util.DoubleMaxString(bidPrice), Util.DoubleMaxString(askPrice), Util.DecimalMaxString(bidSize), Util.DecimalMaxString(askSize),
                tickAttribBidAsk.BidPastLow, tickAttribBidAsk.AskPastHigh)
        End Sub
        '! [tickbytickbidask]

        '! [tickbytickmidpoint]
        Public Sub tickByTickMidPoint(reqId As Integer, time As Long, midPoint As Double) Implements EWrapper.tickByTickMidPoint
            Console.WriteLine("Tick-By-Tick. Request Id: {0}, TickType: MidPoint, Time: {1}, MidPoint: {2}",
                reqId, Util.UnixSecondsToString(time, "yyyyMMdd-HH:mm:ss"), Util.DoubleMaxString(midPoint))
        End Sub
        '! [tickbytickmidpoint]

        '! [orderbound]
        Public Sub orderBound(permId As Long, clientId As Integer, orderId As Integer) Implements EWrapper.orderBound
            Console.WriteLine("Order bound. PermId: {0}, ClientId: {1}, OrderId: {2}", Util.LongMaxString(permId), Util.IntMaxString(clientId), Util.IntMaxString(orderId))
        End Sub
        '! [orderbound]

        '! [completedorder]
        Public Sub completedOrder(contract As IBApi.Contract, order As IBApi.Order, orderState As IBApi.OrderState) Implements IBApi.EWrapper.completedOrder
            Console.WriteLine("CompletedOrder. PermID: " & Util.LongMaxString(order.PermId) & ", ParentPermID: " & Util.LongMaxString(order.ParentPermId) & ", Account: " & order.Account &
                              ", Symbol: " & contract.Symbol & ", SecType: " & contract.SecType & " , Exchange: " & contract.Exchange & ", Action: " & order.Action &
                              ", OrderType: " & order.OrderType & ", TotalQty: " & Util.DecimalMaxString(order.TotalQuantity) & ", CashQty: " & Util.DoubleMaxString(order.CashQty) &
                              ", FilledQty: " & Util.DecimalMaxString(order.FilledQuantity) & ", LmtPrice: " & Util.DoubleMaxString(order.LmtPrice) & ", AuxPrice: " & Util.DoubleMaxString(order.AuxPrice) &
                              ", Status: " & orderState.Status & ", CompletedTime: " & orderState.CompletedTime & ", CompletedStatus: " & orderState.CompletedStatus &
                              ", MinTradeQty: " & Util.IntMaxString(order.MinTradeQty) & ", MinCompeteSize: " & Util.IntMaxString(order.MinCompeteSize) &
                              ", CompeteAgainstBestOffset: " & If(order.CompeteAgainstBestOffset = Order.COMPETE_AGAINST_BEST_OFFSET_UP_TO_MID, "UpToMid", Util.DoubleMaxString(order.CompeteAgainstBestOffset)) &
                              ", MidOffsetAtWhole: " & Util.DoubleMaxString(order.MidOffsetAtWhole) & ", MidOffsetAtHalf: " & Util.DoubleMaxString(order.MidOffsetAtHalf) & ", CustAcct: " & order.CustomerAccount &
                              ", ProfCust: " & order.ProfessionalCustomer & ", Submitter: " & order.Submitter & ", ImbalanceOnly: " & order.ImbalanceOnly)
        End Sub
        '! [completedorder]

        '! [completedordersend]
        Public Sub completedOrdersEnd() Implements IBApi.EWrapper.completedOrdersEnd
            Console.WriteLine("CompletedOrdersEnd")
        End Sub
        '! [completedordersend]

        '! [replacefaend]
        Public Sub replaceFAEnd(reqId As Integer, text As String) Implements IBApi.EWrapper.replaceFAEnd
            Console.WriteLine("replaceFAEnd. ReqId: {0}, Text: {1}", reqId, text)
        End Sub
        '! [replacefaend]

        '! [wshMetaData]
        Public Sub wshMetaData(reqId As Integer, dataJson As String) Implements EWrapper.wshMetaData
            Console.WriteLine($"WSH Meta Data. Request Id: {reqId}, Data JSON: {dataJson}")
        End Sub
        '! [wshMetaData]

        '! [wshEventData]
        Public Sub wshEventData(reqId As Integer, dataJson As String) Implements EWrapper.wshEventData
            Console.WriteLine($"WSH Event Data. Request Id: {reqId}, Data JSON: {dataJson}")
        End Sub
        '! [wshEventData]

        '! [historicalSchedule]
        Public Sub historicalSchedule(reqId As Integer, startDateTime As String, endDateTime As String, timeZone As String, sessions As HistoricalSession()) Implements EWrapper.historicalSchedule
            Console.WriteLine($"Historical Schedule. ReqId: {reqId}, Start: {startDateTime}, End: {endDateTime}, Time Zone: {timeZone}")
            For Each session In sessions
                Console.WriteLine($"{Chr(9)}Session. Start: {session.StartDateTime}, End: {session.EndDateTime}, Ref Date: {session.RefDate}")
            Next
        End Sub
        '! [historicalSchedule]

        '! [userInfo]
        Public Sub userInfo(reqId As Integer, whiteBrandingId As String) Implements EWrapper.userInfo
            Console.WriteLine($"User Info. ReqId: {reqId}, WhiteBrandingId: {whiteBrandingId}")
        End Sub
        '! [userInfo]

        '! [currenttimeinmillis]
        Public Sub currentTimeInMillis(timeInMillis As Long) Implements IBApi.EWrapper.currentTimeInMillis
            Console.WriteLine("CurrentTimeInMillis Time - " & timeInMillis & " : " & Util.UnixMilliSecondsToString(timeInMillis, "MMM dd, yyyy HH:mm:ss.FFF"))
        End Sub
        '! [currenttimeinmillis]

    End Class

End Namespace
