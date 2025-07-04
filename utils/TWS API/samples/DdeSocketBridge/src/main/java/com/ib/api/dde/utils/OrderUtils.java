/* Copyright (C) 2025 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 * and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable. */

package com.ib.api.dde.utils;

import java.util.ArrayList;
import java.util.List;

import com.ib.api.dde.dde2socket.requests.DdeRequestType;
import com.ib.api.dde.dde2socket.requests.orders.OrderStatusRequest;
import com.ib.api.dde.socket2dde.data.OpenOrderData;
import com.ib.api.dde.socket2dde.data.OrderData;
import com.ib.api.dde.socket2dde.data.OrderStatusData;
import com.ib.client.OrderAllocation;

/** Class contains some utility methods related to order requests */
public class OrderUtils {

    /** Method converts openOrderData list to byte array*/
   public static byte[] openOrderDataListToByteArray(List<OrderData> openOrderDataList, List<OrderData> allOpenOrderDataList) {
        ArrayList<ArrayList<String>> list = new ArrayList<ArrayList<String>>();

        int index = 1;
        if (allOpenOrderDataList != null) {
            for (int i = 0; i < allOpenOrderDataList.size(); i++) {
                OrderData msg = allOpenOrderDataList.get(i);
                ArrayList<String> item = createTableItem(msg, index++);
                list.add(new ArrayList<String>(item));
                item.clear();
            }
        }
        for (int i = 0; i < openOrderDataList.size(); i++) {
            OrderData msg = openOrderDataList.get(i);
            ArrayList<String> item = createTableItem(msg, index++);
            list.add(new ArrayList<String>(item));
            item.clear();
        }
        byte[] bytes = list.size() > 0 ? Utils.convertTableToByteArray(list) : null;
        return bytes;
    }

    /** Method creates single table row (array of strings) from OrderData */
    private static ArrayList<String> createTableItem(OrderData orderData, int index) {
        if (orderData instanceof OpenOrderData) {
            return createOpenOrderTableItem((OpenOrderData)orderData, index);
        } else {
            return createCompletedOrderTableItem(orderData);
        }
    }
    
    /** Method creates single table row (array of strings) from completed order */
    private static ArrayList<String> createCompletedOrderTableItem(OrderData completedOrderData) {
        ArrayList<String> item = new ArrayList<String>();

        if (completedOrderData.contract() != null) {
            item.add(Utils.toString(completedOrderData.contract().symbol()));
            item.add(Utils.toString(completedOrderData.contract().getSecType()));
            item.add(Utils.toString(completedOrderData.contract().lastTradeDateOrContractMonth()));
            item.add(Utils.toString(completedOrderData.contract().strike()));
            item.add(Utils.toString(completedOrderData.contract().getRight()));
            item.add(Utils.toString(completedOrderData.contract().multiplier()));
            item.add(Utils.toString(completedOrderData.contract().tradingClass()));
            item.add(Utils.toString(completedOrderData.contract().exchange()));
            item.add(Utils.toString(completedOrderData.contract().primaryExch()));
            item.add(Utils.toString(completedOrderData.contract().currency()));
            item.add(Utils.toString(completedOrderData.contract().localSymbol()));
            item.add(Utils.toString(completedOrderData.contract().conid()));
            item.add(Utils.comboLegsListToString(completedOrderData.contract().comboLegs()));
            item.add(Utils.deltaNeutralContractToString(completedOrderData.contract().deltaNeutralContract()));
        } else {
            for (int j = 0; j < 14; j++) {
                item.add(Utils.toString(""));
            }
        }
        
        if (completedOrderData.order() != null) {
            item.add(Utils.toString(completedOrderData.order().getAction()));
            item.add(completedOrderData.order().totalQuantity().toString());
            item.add(Utils.toString(completedOrderData.order().cashQty()));
            item.add(completedOrderData.order().filledQuantity().toString());
            item.add(Utils.toString(completedOrderData.order().getOrderType()));
            item.add(Utils.toString(completedOrderData.order().lmtPrice()));
            item.add(Utils.toString(completedOrderData.order().auxPrice()));
        } else {
            for (int j = 0; j < 7; j++) {
                item.add(Utils.toString(""));
            }
        }
        
        if (completedOrderData.orderState() != null) {
            item.add(Utils.toString(completedOrderData.orderState().status().toString()));
            item.add(Utils.toString(completedOrderData.orderState().completedTime()));
            item.add(Utils.toString(completedOrderData.orderState().completedStatus()));
        } else {
            for (int j = 0; j < 3; j++) {
                item.add(Utils.toString(""));
            }
        }

        if (completedOrderData.order() != null) {
            item.add(Utils.toString(completedOrderData.order().permId()));
            item.add(Utils.toString(completedOrderData.order().parentPermId()));
            item.add(Utils.toString(completedOrderData.order().getTif()));
            item.add(Utils.toString(completedOrderData.order().displaySize()));
            item.add(Utils.toString(completedOrderData.order().settlingFirm()));
            item.add(Utils.toString(completedOrderData.order().clearingAccount()));
            item.add(Utils.toString(completedOrderData.order().clearingIntent()));
            item.add(Utils.toString(completedOrderData.order().openClose()));
            item.add(Utils.toString(completedOrderData.order().origin()));
            item.add(Utils.toString(completedOrderData.order().shortSaleSlot()));
            item.add(Utils.toString(completedOrderData.order().designatedLocation()));
            item.add(Utils.toString(completedOrderData.order().exemptCode()));
            item.add(Utils.toString(completedOrderData.order().allOrNone()));
            item.add(Utils.toString(completedOrderData.order().hidden()));
            item.add(Utils.toString(completedOrderData.order().outsideRth()));
            item.add(Utils.toString(completedOrderData.order().sweepToFill()));
            item.add(Utils.toString(completedOrderData.order().percentOffset()));
            item.add(Utils.toString(completedOrderData.order().trailingPercent()));
            item.add(Utils.toString(completedOrderData.order().trailStopPrice()));
            item.add(Utils.toString(completedOrderData.order().minQty()));
            item.add(Utils.toString(completedOrderData.order().goodAfterTime()));
            item.add(Utils.toString(completedOrderData.order().goodTillDate()));
            item.add(Utils.toString(completedOrderData.order().ocaGroup()));
            item.add(Utils.toString(completedOrderData.order().getOcaType()));
            item.add(Utils.toString(completedOrderData.order().orderRef()));
            item.add(Utils.toString(completedOrderData.order().getRule80A()));
            item.add(Utils.toString(completedOrderData.order().getTriggerMethod()));
            item.add(Utils.toString(completedOrderData.order().account()));
            item.add(Utils.toString(completedOrderData.order().faGroup()));
            item.add(Utils.toString(completedOrderData.order().getFaMethod()));
            item.add(Utils.toString(completedOrderData.order().faPercentage()));
            item.add(Utils.toString(completedOrderData.order().volatility()));
            item.add(Utils.toString(completedOrderData.order().getVolatilityType()));
            item.add(Utils.toString(completedOrderData.order().continuousUpdate()));
            item.add(Utils.toString(completedOrderData.order().getReferencePriceType()));
            item.add(Utils.toString(completedOrderData.order().getDeltaNeutralOrderType()));
            item.add(Utils.toString(completedOrderData.order().deltaNeutralAuxPrice()));
            item.add(Utils.toString(completedOrderData.order().deltaNeutralConId()));
            item.add(Utils.toString(completedOrderData.order().deltaNeutralShortSale()));
            item.add(Utils.toString(completedOrderData.order().deltaNeutralShortSaleSlot()));
            item.add(Utils.toString(completedOrderData.order().deltaNeutralDesignatedLocation()));
            item.add(Utils.toString(completedOrderData.order().scaleInitLevelSize()));
            item.add(Utils.toString(completedOrderData.order().scaleSubsLevelSize()));
            item.add(Utils.toString(completedOrderData.order().scalePriceIncrement()));
            item.add(Utils.toString(completedOrderData.order().scalePriceAdjustValue()));
            item.add(Utils.toString(completedOrderData.order().scalePriceAdjustInterval()));
            item.add(Utils.toString(completedOrderData.order().scaleProfitOffset()));
            item.add(Utils.toString(completedOrderData.order().scaleAutoReset()));
            item.add(Utils.toString(completedOrderData.order().scaleInitPosition()));
            item.add(Utils.toString(completedOrderData.order().scaleInitFillQty()));
            item.add(Utils.toString(completedOrderData.order().scaleRandomPercent()));
            item.add(Utils.toString(completedOrderData.order().getHedgeType()));
            item.add(Utils.toString(completedOrderData.order().hedgeParam()));
            item.add(Utils.toString(completedOrderData.order().dontUseAutoPriceForHedge()));
            item.add(Utils.toString(completedOrderData.order().getAlgoStrategy()));
            item.add(Utils.tagValueListToString(completedOrderData.order().algoParams()));
            item.add(Utils.tagValueListToString(completedOrderData.order().smartComboRoutingParams()));
            item.add(Utils.orderComboLegsListToString(completedOrderData.order().orderComboLegs()));
            item.add(Utils.toString(completedOrderData.order().discretionaryAmt()));
            item.add(Utils.toString(completedOrderData.order().startingPrice()));
            item.add(Utils.toString(completedOrderData.order().stockRefPrice()));
            item.add(Utils.toString(completedOrderData.order().delta()));
            item.add(Utils.toString(completedOrderData.order().stockRangeLower()));
            item.add(Utils.toString(completedOrderData.order().stockRangeUpper()));
            item.add(Utils.toString(completedOrderData.order().notHeld()));
            item.add(Utils.toString(completedOrderData.order().solicited()));
            item.add(Utils.toString(completedOrderData.order().randomizeSize()));
            item.add(Utils.toString(completedOrderData.order().randomizePrice()));
            item.add(Utils.toString(completedOrderData.order().referenceContractId()));
            item.add(Utils.toString(completedOrderData.order().isPeggedChangeAmountDecrease()));
            item.add(Utils.toString(completedOrderData.order().peggedChangeAmount()));
            item.add(Utils.toString(completedOrderData.order().referenceChangeAmount()));
            item.add(Utils.toString(completedOrderData.order().referenceExchangeId()));
            item.add(Utils.toString(completedOrderData.order().lmtPriceOffset()));
            item.add(Utils.conditionsToString(completedOrderData.order().conditions()));
            item.add(Utils.toString(completedOrderData.order().conditionsIgnoreRth()));
            item.add(Utils.toString(completedOrderData.order().conditionsCancelOrder()));
            item.add(Utils.toString(completedOrderData.order().modelCode()));
            item.add(Utils.toString(completedOrderData.order().isOmsContainer()));
            item.add(Utils.toString(completedOrderData.order().autoCancelDate()));
            item.add(Utils.toString(completedOrderData.order().refFuturesConId()));
            item.add(Utils.toString(completedOrderData.order().autoCancelParent()));
            item.add(Utils.toString(completedOrderData.order().shareholder()));
            item.add(Utils.toString(completedOrderData.order().imbalanceOnly()));
            item.add(Utils.toString(completedOrderData.order().routeMarketableToBbo()));
            item.add(Utils.toString(completedOrderData.order().minTradeQty()));
            item.add(Utils.toString(completedOrderData.order().minCompeteSize()));
            item.add(completedOrderData.order().isCompeteAgainstBestOffsetUpToMid() ? Utils.UP_TO_MID : Utils.toString(completedOrderData.order().competeAgainstBestOffset()));
            item.add(Utils.toString(completedOrderData.order().midOffsetAtWhole()));
            item.add(Utils.toString(completedOrderData.order().midOffsetAtHalf()));
            item.add(Utils.toString(completedOrderData.order().customerAccount()));
            item.add(Utils.toString(completedOrderData.order().professionalCustomer()));
            item.add(Utils.toString(completedOrderData.order().submitter()));
        } else {
            for (int j = 0; j < 93; j++) {
                item.add(Utils.toString(""));
            }
        }
        
        return item;
    }
    
    /** Method creates single table row (array of strings) from open order */
    private static ArrayList<String> createOpenOrderTableItem(OpenOrderData openOrderData, int index) {
        ArrayList<String> item = new ArrayList<String>();
        if (openOrderData.contract() != null) {
            item.add(Utils.toString(openOrderData.contract().symbol()));
            item.add(Utils.toString(openOrderData.contract().getSecType()));
            item.add(Utils.toString(openOrderData.contract().lastTradeDateOrContractMonth()));
            item.add(Utils.toString(openOrderData.contract().strike()));
            item.add(Utils.toString(openOrderData.contract().getRight()));
            item.add(Utils.toString(openOrderData.contract().multiplier()));
            item.add(Utils.toString(openOrderData.contract().tradingClass()));
            item.add(Utils.toString(openOrderData.contract().exchange()));
            item.add(Utils.toString(openOrderData.contract().primaryExch()));
            item.add(Utils.toString(openOrderData.contract().currency()));
            item.add(Utils.toString(openOrderData.contract().localSymbol()));
            item.add(Utils.toString(openOrderData.contract().conid()));
            item.add(Utils.comboLegsListToString(openOrderData.contract().comboLegs()));
            item.add(Utils.deltaNeutralContractToString(openOrderData.contract().deltaNeutralContract()));
        } else {
            for (int j = 0; j < 14; j++) {
                item.add(Utils.toString(""));
            }
        }
        
        if (openOrderData.order() != null) {
            item.add(Utils.toString(openOrderData.order().getAction()));
            item.add(openOrderData.order().totalQuantity().toString());
            item.add(Utils.toString(openOrderData.order().getOrderType()));
            item.add(Utils.toString(openOrderData.order().lmtPrice()));
            item.add(Utils.toString(openOrderData.order().auxPrice()));
            item.add(Utils.toString(openOrderData.order().orderId()));
        } else {
            for (int j = 0; j < 6; j++) {
                item.add(Utils.toString(""));
            }
        }
         
        if (openOrderData.orderStatus() != null) {
            item.add(Utils.toString(openOrderData.orderStatus().status()));
            item.add(openOrderData.orderStatus().filled().toString());
            item.add(openOrderData.orderStatus().remaining().toString());
            item.add(Utils.toString(openOrderData.orderStatus().avgFillPrice()));
            item.add(Utils.toString(openOrderData.orderStatus().lastFillPrice()));
            item.add(Utils.toString(openOrderData.orderStatus().whyHeld()));
            item.add(Utils.toString(openOrderData.orderStatus().mktCapPrice()));
            item.add(Utils.toString(openOrderData.orderStatus().parentId()));
            item.add(Utils.toString(openOrderData.orderStatus().clientId(), "0"));
            item.add(Utils.toString(openOrderData.orderStatus().permId()));
        } else {
            for (int j = 0; j < 10; j++) {
                item.add(Utils.toString(""));
            }
        }

        if (openOrderData.order() != null) {
            item.add(Utils.toString(openOrderData.order().getTif()));
            item.add(Utils.toString(openOrderData.order().displaySize()));
            item.add(Utils.toString(openOrderData.order().settlingFirm()));
            item.add(Utils.toString(openOrderData.order().clearingAccount()));
            item.add(Utils.toString(openOrderData.order().clearingIntent()));
            item.add(Utils.toString(openOrderData.order().openClose()));
            item.add(Utils.toString(openOrderData.order().origin()));
            item.add(Utils.toString(openOrderData.order().shortSaleSlot()));
            item.add(Utils.toString(openOrderData.order().designatedLocation()));
            item.add(Utils.toString(openOrderData.order().exemptCode()));
            item.add(Utils.toString(openOrderData.order().allOrNone()));
            item.add(Utils.toString(openOrderData.order().blockOrder()));
            item.add(Utils.toString(openOrderData.order().hidden()));
            item.add(Utils.toString(openOrderData.order().outsideRth()));
            item.add(Utils.toString(openOrderData.order().sweepToFill()));
            item.add(Utils.toString(openOrderData.order().percentOffset()));
            item.add(Utils.toString(openOrderData.order().trailingPercent()));
            item.add(Utils.toString(openOrderData.order().trailStopPrice()));
            item.add(Utils.toString(openOrderData.order().minQty()));
            item.add(Utils.toString(openOrderData.order().goodAfterTime()));
            item.add(Utils.toString(openOrderData.order().goodTillDate()));
            item.add(Utils.toString(openOrderData.order().ocaGroup()));
            item.add(Utils.toString(openOrderData.order().getOcaType()));
            item.add(Utils.toString(openOrderData.order().orderRef()));
            item.add(Utils.toString(openOrderData.order().getRule80A()));
            item.add(Utils.toString(openOrderData.order().getTriggerMethod()));
            item.add(Utils.toString(openOrderData.order().activeStartTime()));
            item.add(Utils.toString(openOrderData.order().activeStopTime()));
            item.add(Utils.toString(openOrderData.order().account()));
            item.add(Utils.toString(openOrderData.order().faGroup()));
            item.add(Utils.toString(openOrderData.order().getFaMethod()));
            item.add(Utils.toString(openOrderData.order().faPercentage()));
            item.add(Utils.toString(openOrderData.order().volatility()));
            item.add(Utils.toString(openOrderData.order().getVolatilityType()));
            item.add(Utils.toString(openOrderData.order().continuousUpdate()));
            item.add(Utils.toString(openOrderData.order().getReferencePriceType()));
            item.add(Utils.toString(openOrderData.order().getDeltaNeutralOrderType()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralAuxPrice()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralConId()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralOpenClose()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralShortSale()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralShortSaleSlot()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralDesignatedLocation()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralSettlingFirm()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralClearingAccount()));
            item.add(Utils.toString(openOrderData.order().deltaNeutralClearingIntent()));
            item.add(Utils.toString(openOrderData.order().scaleInitLevelSize()));
            item.add(Utils.toString(openOrderData.order().scaleSubsLevelSize()));
            item.add(Utils.toString(openOrderData.order().scalePriceIncrement()));
            item.add(Utils.toString(openOrderData.order().scalePriceAdjustValue()));
            item.add(Utils.toString(openOrderData.order().scalePriceAdjustInterval()));
            item.add(Utils.toString(openOrderData.order().scaleProfitOffset()));
            item.add(Utils.toString(openOrderData.order().scaleAutoReset()));
            item.add(Utils.toString(openOrderData.order().scaleInitPosition()));
            item.add(Utils.toString(openOrderData.order().scaleInitFillQty()));
            item.add(Utils.toString(openOrderData.order().scaleRandomPercent()));
            item.add(Utils.toString(openOrderData.order().getHedgeType()));
            item.add(Utils.toString(openOrderData.order().hedgeParam()));
            item.add(Utils.toString(openOrderData.order().dontUseAutoPriceForHedge()));
            item.add(Utils.toString(openOrderData.order().getAlgoStrategy()));
            item.add(Utils.tagValueListToString(openOrderData.order().algoParams()));
            item.add(Utils.tagValueListToString(openOrderData.order().smartComboRoutingParams()));
            item.add(Utils.orderComboLegsListToString(openOrderData.order().orderComboLegs()));
            item.add(Utils.toString(openOrderData.order().transmit()));
            item.add(Utils.toString(openOrderData.order().parentId()));
            item.add(Utils.toString(openOrderData.order().discretionaryAmt()));
            item.add(Utils.toString(openOrderData.order().optOutSmartRouting()));
            item.add(Utils.toString(openOrderData.order().auctionStrategy()));
            item.add(Utils.toString(openOrderData.order().startingPrice()));
            item.add(Utils.toString(openOrderData.order().stockRefPrice()));
            item.add(Utils.toString(openOrderData.order().delta()));
            item.add(Utils.toString(openOrderData.order().stockRangeLower()));
            item.add(Utils.toString(openOrderData.order().stockRangeUpper()));
            item.add(Utils.toString(openOrderData.order().basisPoints()));
            item.add(Utils.toString(openOrderData.order().basisPointsType()));
            item.add(Utils.toString(openOrderData.order().notHeld()));
            item.add(Utils.toString(openOrderData.order().solicited()));
            item.add(Utils.toString(openOrderData.order().randomizeSize()));
            item.add(Utils.toString(openOrderData.order().randomizePrice()));
            item.add(Utils.toString(openOrderData.order().referenceContractId()));
            item.add(Utils.toString(openOrderData.order().adjustedOrderType() != null ? openOrderData.order().adjustedOrderType().getApiString() : ""));
            item.add(Utils.toString(openOrderData.order().triggerPrice()));
            item.add(Utils.toString(openOrderData.order().adjustedStopPrice()));
            item.add(Utils.toString(openOrderData.order().adjustedStopLimitPrice()));
            item.add(Utils.toString(openOrderData.order().adjustedTrailingAmount()));
            item.add(Utils.toString(openOrderData.order().adjustableTrailingUnit()));
            item.add(Utils.toString(openOrderData.order().lmtPriceOffset()));
            item.add(Utils.conditionsToString(openOrderData.order().conditions()));
            item.add(Utils.toString(openOrderData.order().conditionsIgnoreRth()));
            item.add(Utils.toString(openOrderData.order().conditionsCancelOrder()));
            item.add(Utils.toString(openOrderData.order().modelCode()));
            item.add(Utils.toString(openOrderData.order().softDollarTier()));
            item.add(Utils.toString(openOrderData.order().cashQty()));
            item.add(Utils.toString(openOrderData.order().isOmsContainer()));
            item.add(Utils.toString(openOrderData.order().discretionaryUpToLimitPrice()));
            item.add(Utils.toString(openOrderData.order().usePriceMgmtAlgo()));
            item.add(Utils.toString(openOrderData.order().duration()));
            item.add(Utils.toString(openOrderData.order().postToAts()));
            item.add(Utils.toString(openOrderData.order().autoCancelParent()));
            item.add(Utils.toString(openOrderData.order().minTradeQty()));
            item.add(Utils.toString(openOrderData.order().minCompeteSize()));
            item.add(openOrderData.order().isCompeteAgainstBestOffsetUpToMid() ? Utils.UP_TO_MID : Utils.toString(openOrderData.order().competeAgainstBestOffset()));
            item.add(Utils.toString(openOrderData.order().midOffsetAtWhole()));
            item.add(Utils.toString(openOrderData.order().midOffsetAtHalf()));
            item.add(Utils.toString(openOrderData.order().customerAccount()));
            item.add(Utils.toString(openOrderData.order().professionalCustomer()));
            item.add(Utils.toString(openOrderData.order().includeOvernight()));
            item.add(Utils.toString(openOrderData.order().extOperator()));
            item.add(Utils.toStringMax(openOrderData.order().manualOrderIndicator()));
            item.add(Utils.toString(openOrderData.order().submitter()));
            item.add(Utils.toString(openOrderData.order().imbalanceOnly()));
        } else {
            for (int j = 0; j < 111; j++) {
                item.add(Utils.toString(""));
            }
        }

        return item;
    }
    
    /** Methods returns orderStatus field value of particular type */
    public static String getFieldValueFromOrderStatusRequest(OrderStatusRequest orderStatusRequest, OrderStatusData orderStatus) {
        String ret = "";
        DdeRequestType requestType = DdeRequestType.getRequestType(orderStatusRequest.field()); 
        switch(requestType) {
            case STATUS:
                ret = orderStatus.status();
                break;
            case FILLED:
                ret = orderStatus.filled().toString();
                break;
            case REMAINING:
                ret = orderStatus.remaining().toString();
                break;
            case AVG_FILL_PRICE:
                ret = Utils.toString(orderStatus.avgFillPrice());
                break;
            case LAST_FILL_PRICE:
                ret = Utils.toString(orderStatus.lastFillPrice());
                break;
            case WHY_HELD:
                ret = orderStatus.whyHeld();
                break;
            case MKT_CAP_PRICE:
                ret = Utils.toString(orderStatus.mktCapPrice());
                break;
            case PARENT_ID:
                ret = Utils.toString(orderStatus.parentId());
                break;
            case CLIENT_ID:
                ret = Utils.toString(orderStatus.clientId());
                break;
            case PERM_ID:
                ret = Utils.toString(orderStatus.permId());
                break;
            case ERROR:
                ret = orderStatus.errorMessage();
                break;
            default:
                break;
        }
        return ret;
    }

    /** Methods returns whatIf field value of particular type */
    public static String getFieldValueFromWhatIfRequest(OrderStatusRequest whatIfRequest, OpenOrderData openOrderData) {
        String ret = "";
        if (whatIfRequest != null && openOrderData != null && openOrderData.orderState() != null) {
            DdeRequestType requestType = DdeRequestType.getRequestType(whatIfRequest.field()); 
            switch(requestType) {
                case WHAT_IF_COMMISSION_AND_FEES:
                    ret = Utils.toString(openOrderData.orderState().commissionAndFees());
                    break;
                case WHAT_IF_COMMISSION_AND_FEES_CURRENCY:
                    ret = openOrderData.orderState().commissionAndFeesCurrency();
                    break;
                case WHAT_IF_CURRENT_EQUITY_WITH_LOAN:
                    ret = openOrderData.orderState().equityWithLoanBefore();
                    break;
                case WHAT_IF_CURRENT_INIT_MARGIN:
                    ret = openOrderData.orderState().initMarginBefore();
                    break;
                case WHAT_IF_CURRENT_MAINT_MARGIN:
                    ret = openOrderData.orderState().maintMarginBefore();
                    break;
                case WHAT_IF_CHANGE_EQUITY_WITH_LOAN:
                    ret = openOrderData.orderState().equityWithLoanChange();
                    break;
                case WHAT_IF_CHANGE_INIT_MARGIN:
                    ret = openOrderData.orderState().initMarginChange();
                    break;
                case WHAT_IF_CHANGE_MAINT_MARGIN:
                    ret = openOrderData.orderState().maintMarginChange();
                    break;
                case WHAT_IF_POST_EQUITY_WITH_LOAN:
                    ret = openOrderData.orderState().equityWithLoanAfter();
                    break;
                case WHAT_IF_POST_INIT_MARGIN:
                    ret = openOrderData.orderState().initMarginAfter();
                    break;
                case WHAT_IF_POST_MAINT_MARGIN:
                    ret = openOrderData.orderState().maintMarginAfter();
                    break;
                case WHAT_IF_BOND_ACCRUED_INTEREST:
                    ret = openOrderData.order().bondAccruedInterest();
                    break;
                case WHAT_IF_MARGIN_CURRENCY:
                    ret = openOrderData.orderState().marginCurrency();
                    break;
                case WHAT_IF_INIT_MARGIN_BEFORE_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().initMarginBeforeOutsideRTH());
                    break;
                case WHAT_IF_MAINT_MARGIN_BEFORE_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().maintMarginBeforeOutsideRTH());
                    break;
                case WHAT_IF_EQUITY_WITH_LOAN_BEFORE_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().equityWithLoanBeforeOutsideRTH());
                    break;
                case WHAT_IF_INIT_MARGIN_CHANGE_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().initMarginChangeOutsideRTH());
                    break;
                case WHAT_IF_MAINT_MARGIN_CHANGE_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().maintMarginChangeOutsideRTH());
                    break;
                case WHAT_IF_EQUITY_WITH_LOAN_CHANGE_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().equityWithLoanChangeOutsideRTH());
                    break;
                case WHAT_IF_INIT_MARGIN_AFTER_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().initMarginAfterOutsideRTH());
                    break;
                case WHAT_IF_MAINT_MARGIN_AFTER_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().maintMarginAfterOutsideRTH());
                    break;
                case WHAT_IF_EQUITY_WITH_LOAN_AFTER_OUTSIDE_RTH:
                    ret = Utils.toString(openOrderData.orderState().equityWithLoanAfterOutsideRTH());
                    break;
                case WHAT_IF_SUGGESTED_SIZE:
                    ret = Utils.toString(openOrderData.orderState().suggestedSize());
                    break;
                case WHAT_IF_REJECT_REASON:
                    ret = openOrderData.orderState().rejectReason();
                    break;
                case WHAT_IF_ORDER_ALLOCATIONS:
                    StringBuilder sb = new StringBuilder();
                    if (openOrderData.orderState().orderAllocations().size() > 0) {
                        for (OrderAllocation orderAllocation : openOrderData.orderState().orderAllocations()) {
                            sb.append("{").append(orderAllocation.toShortString()).append("}; ");
                        }
                    }
                    ret = sb.toString();
                    break;
                default:
                    break;
            }
        }
        return ret;
    }
}
