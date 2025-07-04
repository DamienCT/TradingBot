/* Copyright (C) 2025 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 * and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable. */
using System;
using IBApi;
using System.Threading;
using IBSamples;
using System.Collections.Generic;

namespace Samples
{
    public class Sample
    {
        /* IMPORTANT: always use your paper trading account. The code below will submit orders as part of the demonstration. */
        /* IB will not be responsible for accidental executions on your live account. */
        /* Any stock or option symbols displayed are for illustrative purposes only and are not intended to portray a recommendation. */
        /* Before contacting our API support team please refer to the available documentation. */
        public static int Main(string[] args)
        {
            testImpl = new EWrapperImpl();

            EClientSocket clientSocket = testImpl.ClientSocket;
            EReaderSignal readerSignal = testImpl.Signal;

            clientSocket.SetConnectOptions("+PACEAPI");

            //! [connect]
            clientSocket.eConnect("127.0.0.1", 7497, 0);
            //! [connect]
            //! [ereader]
            //Create a reader to consume messages from the TWS. The EReader will consume the incoming messages and put them in a queue
            var reader = new EReader(clientSocket, readerSignal);
            reader.Start();
            //Once the messages are in the queue, an additional thread can be created to fetch them
            new Thread(() => { while (clientSocket.IsConnected()) { readerSignal.waitForSignal(); reader.processMsgs(); } }) { IsBackground = true }.Start();
            //! [ereader]
            /*************************************************************************************************************************************************/
            /* One (although primitive) way of knowing if we can proceed is by monitoring the order's nextValidId reception which comes down automatically after connecting. */
            /*************************************************************************************************************************************************/
            while (testImpl.NextOrderId <= 0) { }            
            testIBMethods(clientSocket, testImpl.NextOrderId);            
            Console.WriteLine("Disconnecting...");
            clientSocket.eDisconnect();
            return 0;
        }

        static EWrapperImpl testImpl;

        /*****************************************************************/
        /* Below are few quick-to-test examples on the IB API functions grouped by functionality. Uncomment the relevant methods. */
        /*****************************************************************/
        private static void testIBMethods(EClientSocket client, int nextValidId)
        {
            /**************************************************************/
            /*** Options operations                                     ***/
            /**************************************************************/
            //optionsOperations(client);

            /**************************************************************/
            /*** Real time market data operations  - Streamed or Frozen ***/
            /**************************************************************/
            //marketDataType(client);

            /***************************************************/
            /*** Real time market data operations  - Tickers ***/
            /***************************************************/
            //tickDataOperations(client);

            /***************************************************/
            /*** Option computation operations  - Tickers    ***/
            /***************************************************/
            //tickOptionComputationOperations(client);

            /********************************************************/
            /*** Real time market data operations  - Market Depth ***/
            /********************************************************/
            //marketDepthOperations(client);

            /**********************************************************/
            /*** Real time market data operations  - Real Time Bars ***/
            /**********************************************************/
            //realTimeBars(client);

            /**************************************************************************************/
            /*** Real time market data operations  - Streamed, Frozen, Delayed or Delayed-Frozen***/
            /**************************************************************************************/
            //marketDataType(client);

            /**********************************/
            /*** Historical Data operations ***/
            /**********************************/
            //historicalDataRequests(client);

            /*************************/
            /*** Options Specifics ***/
            /*************************/
            //optionsOperations(client);

            /****************************/
            /*** Contract information ***/
            /****************************/
            //contractOperations(client);

            /***********************/
            /*** Market Scanners ***/
            /***********************/
            //marketScanners(client);

            /*****************************/
            /*** Reuter's Fundamentals ***/
            /*****************************/
            //fundamentals(client);

            /***********************/
            /*** IB's Bulletins ***/
            /***********************/
            //bulletins(client);

            /**************************/
            /*** Account Management ***/
            /**************************/
            //accountOperations(client);

            /**********************/
            /*** Order handling ***/
            /**********************/
            orderOperations(client, nextValidId);

            /************************************/
            /*** Financial Advisor Exclusive Operations ***/
            /************************************/
            //financialAdvisorOperations(client);

            /********************/
            /*** Miscellaneous ***/
            /********************/
            //miscellaneous(client);

            /********************/
            /*** Linking ***/
            /********************/
            //linkingOperations(client);

            /***********************/
            /*** News operations ***/
            /***********************/
            //newsOperations(client);

            /***********************/
            /*** Smart components ***/
            /***********************/
            //smartComponents(client);

            /***********************/
            /*** Head time stamp ***/
            /***********************/
            //headTimestamp(client);

            /***********************/
            /*** Histogram data  ***/
            /***********************/
            //histogramData(client);

            /***********************/
            /*** CFD re-route    ***/
            /***********************/
            //rerouteCFDOperations(client);

            /***********************/
            /*** Market rule     ***/
            /***********************/
            //marketRuleOperations(client);

            //pnl(client);

            //pnlSingle(client);

            /**************************/
            /*** Algo Orders ***/
            /**************************/
            //TestAlgoSamples(client, nextValidId);

            /**************************/
            /*** Continuous futures ***/
            /**************************/
            //continuousFuturesOperations(client);

            //historicalTicks(client);

            /**************************/
            /*** Tick-By-Tick       ***/
            /**************************/
            //tickByTickOperations(client);

            /***********************/
            /*** What-If samples ***/
            /***********************/
            //whatIfSamples(client, nextValidId);

            /***********************/
            /*** WSHE Calendar API samples ***/
            /***********************/
            //wshCalendarOperations(client);

            Thread.Sleep(3000);
            Console.WriteLine("Done");
            Thread.Sleep(500000);
        }


        private static void wshCalendarOperations(EClientSocket client)
        {
			//! [reqmetadata]
            client.reqWshMetaData(1100);
			//! [reqmetadata]

            Thread.Sleep(1000);

            client.cancelWshMetaData(1100);

			//! [reqeventdata]
            client.reqWshEventData(1101, new WshEventData(8314, false, false, false, "20220511", "", 5));
            //! [reqeventdata]

            Thread.Sleep(3000);

            //! [reqeventdata]
            client.reqWshEventData(1102, new WshEventData("{\"watchlist\":[\"8314\"]}", false, false, false, "", "20220512", int.MaxValue));
            //! [reqeventdata]

            Thread.Sleep(1000);

            client.cancelWshEventData(1101);
            client.cancelWshEventData(1102);
        }

        private static void tickByTickOperations(EClientSocket client)
        {

            /*** Requesting tick-by-tick data (only refresh) ***/
            //! [reqtickbytick]
            client.reqTickByTickData(19001, ContractSamples.USStockAtSmart(), "Last", 0, false);
            client.reqTickByTickData(19002, ContractSamples.USStockAtSmart(), "AllLast", 0, false);
            client.reqTickByTickData(19003, ContractSamples.USStockAtSmart(), "BidAsk", 0, true);
            client.reqTickByTickData(19004, ContractSamples.EurGbpFx(), "MidPoint", 0, false);
            //! [reqtickbytick]

            Thread.Sleep(10000);

            //! [canceltickbytick]
            client.cancelTickByTickData(19001);
            client.cancelTickByTickData(19002);
            client.cancelTickByTickData(19003);
            client.cancelTickByTickData(19004);
            //! [canceltickbytick]

            Thread.Sleep(5000);

            /*** Requesting tick-by-tick data (historical + refresh) ***/
            //! [reqtickbytick]
            client.reqTickByTickData(19005, ContractSamples.EuropeanStock(), "Last", 10, false);
            client.reqTickByTickData(19006, ContractSamples.EuropeanStock(), "AllLast", 10, false);
            client.reqTickByTickData(19007, ContractSamples.EuropeanStock(), "BidAsk", 10, false);
            client.reqTickByTickData(19008, ContractSamples.EurGbpFx(), "MidPoint", 10, true);
            //! [reqtickbytick]

            Thread.Sleep(10000);

            //! [canceltickbytick]
            client.cancelTickByTickData(19005);
            client.cancelTickByTickData(19006);
            client.cancelTickByTickData(19007);
            client.cancelTickByTickData(19008);
            //! [canceltickbytick]
        }


        private static void historicalTicks(EClientSocket client)
        {
			//! [reqhistoricalticks]
            client.reqHistoricalTicks(18001, ContractSamples.USStockAtSmart(), "20170712 21:39:33 US/Eastern", null, 10, "TRADES", 1, true, null);
            client.reqHistoricalTicks(18002, ContractSamples.USStockAtSmart(), "20170712 21:39:33 US/Eastern", null, 10, "BID_ASK", 1, true, null);
            client.reqHistoricalTicks(18003, ContractSamples.USStockAtSmart(), "20170712 21:39:33 US/Eastern", null, 10, "MIDPOINT", 1, true, null);
			//! [reqhistoricalticks]
        }

        private static void pnl(EClientSocket client)
        {
			//! [reqpnl]
            client.reqPnL(17001, "DUD00029", "");
			//! [reqpnl]
            Thread.Sleep(1000);
			//! [cancelpnl]
            client.cancelPnL(17001);
			//! [cancelpnl]
        }

        private static void pnlSingle(EClientSocket client)
        {
			//! [reqpnlsingle]
            client.reqPnLSingle(17001, "DUD00029", "", 268084);
			//! [reqpnlsingle]
            Thread.Sleep(1000);
			//! [cancelpnlsingle]
            client.cancelPnLSingle(17001);
			//! [cancelpnlsingle]
			
        }

        private static void rerouteCFDOperations(EClientSocket client)
        {
            //! [reqmktdatacfd]
            client.reqMktData(16001, ContractSamples.USStockCFD(), string.Empty, false, false, null);
            Thread.Sleep(1000);
            client.reqMktData(16002, ContractSamples.EuropeanStockCFD(), string.Empty, false, false, null);
            Thread.Sleep(1000);
            client.reqMktData(16003, ContractSamples.CashCFD(), string.Empty, false, false, null);
            Thread.Sleep(1000);
            //! [reqmktdatacfd]

            //! [reqmktdepthcfd]
            client.reqMarketDepth(16004, ContractSamples.USStockCFD(), 10, false, null);
            Thread.Sleep(1000);
            client.reqMarketDepth(16005, ContractSamples.EuropeanStockCFD(), 10, false, null);
            Thread.Sleep(1000);
            client.reqMarketDepth(16006, ContractSamples.CashCFD(), 10, false, null);
            Thread.Sleep(1000);
            //! [reqmktdepthcfd]
        }

        private static void histogramData(EClientSocket client)
        {
			//! [reqHistogramData]
			client.reqHistogramData(15001, ContractSamples.USStockWithPrimaryExch(), false, "1 week");
            //! [reqHistogramData]
			Thread.Sleep(2000);
            //! [cancelHistogramData]
			client.cancelHistogramData(15001);
			//! [cancelHistogramData]
		}

        private static void headTimestamp(EClientSocket client)
        {
			//! [reqHeadTimeStamp]
            client.reqHeadTimestamp(14001, ContractSamples.USStock(), "TRADES", 1, 1);
            //! [reqHeadTimeStamp]
            Thread.Sleep(1000);
            //! [cancelHeadTimestamp]
            client.cancelHeadTimestamp(14001);
			//! [cancelHeadTimestamp]
	
	}

        private static void smartComponents(EClientSocket client)
        {
            client.reqMktData(13001, ContractSamples.USStockAtSmart(), "", false, false, null);

            while (string.IsNullOrWhiteSpace(testImpl.BboExchange))
            {
                Thread.Sleep(1000);
            }

            client.cancelMktData(13001);
		//! [reqsmartcomponents]
            client.reqSmartComponents(13002, testImpl.BboExchange);
		//! [reqsmartcomponents]
        }

        private static void tickDataOperations(EClientSocket client)
        {
            //! [reqmarketdatatype]
            client.reqMarketDataType(4);
            //! [reqmarketdatatype]

            /*** Requesting real time market data ***/
            //Thread.Sleep(1000);
            //! [reqmktdata]
            client.reqMktData(1001, ContractSamples.StockComboContract(), string.Empty, false, false, null);
            //! [reqmktdata]
            //! [reqmktdata_snapshot]
            client.reqMktData(1003, ContractSamples.FutureComboContract(), string.Empty, true, false, null);
            //! [reqmktdata_snapshot]

			/*
			//! [regulatorysnapshot]
			// Each regulatory snapshot incurs a 0.01 USD fee
			client.reqMktData(1005, ContractSamples.USStock(), "", false, true, null);
			//! [regulatorysnapshot]
			*/
			
            //! [reqmktdata_genticks]
            //Requesting RTVolume (Time & Sales) and shortable generic ticks
            client.reqMktData(1004, ContractSamples.USStockAtSmart(), "233,236", false, false, null);
            //! [reqmktdata_genticks]

            //! [reqmktdata_contractnews]
			// Without the API news subscription this will generate an "invalid tick type" error
            client.reqMktData(1005, ContractSamples.USStock(), "mdoff,292:BZ", false, false, null);
            client.reqMktData(1006, ContractSamples.USStock(), "mdoff,292:BT", false, false, null);
            client.reqMktData(1007, ContractSamples.USStock(), "mdoff,292:FLY", false, false, null);
            client.reqMktData(1008, ContractSamples.USStock(), "mdoff,292:DJ-RT", false, false, null);
            //! [reqmktdata_contractnews]
            //! [reqmktdata_broadtapenews]
            client.reqMktData(1009, ContractSamples.BTbroadtapeNewsFeed(), "mdoff,292", false, false, null);
            client.reqMktData(1010, ContractSamples.BZbroadtapeNewsFeed(), "mdoff,292", false, false, null);
            client.reqMktData(1011, ContractSamples.FLYbroadtapeNewsFeed(), "mdoff,292", false, false, null);
            //! [reqmktdata_broadtapenews]

            //! [reqoptiondatagenticks]
            //Requesting data for an option contract will return the greek values
            client.reqMktData(1002, ContractSamples.OptionWithLocalSymbol(), string.Empty, false, false, null);
            //! [reqoptiondatagenticks]
            
            //! [reqfuturesopeninterest]
            //Requesting data for a futures contract will return the futures open interest
            client.reqMktData(1014, ContractSamples.SimpleFuture(), "mdoff,588", false, false, null);
            //! [reqfuturesopeninterest]

            //! [reqmktdatapreopenbidask]
            //Requesting data for a futures contract will return the pre-open bid/ask flag
            client.reqMktData(1015, ContractSamples.SimpleFuture(), "", false, false, null);
            //! [reqmktDatapreopenbidask]

            //! [reqavgoptvolume]
            //Requesting data for a stock will return the average option volume
            client.reqMktData(1016, ContractSamples.USStockAtSmart(), "mdoff,105", false, false, null);
            //! [reqavgoptvolume]

            //! [reqetfticks]
            client.reqMktData(1017, ContractSamples.etf(), "mdoff,577,623,614", false, false, null);
            //! [reqetfticks]

            //! [IPO_price]
            client.reqMktData(1018, ContractSamples.StockWithIPOPrice(), "mdoff,586", false, false, null);
            //! [IPO_price]

            //! [yieldbidask]
            client.reqMktData(1019, ContractSamples.Bond(), "", false, false, null);
            //! [yieldbidask]

            Thread.Sleep(10000);
            /*** Canceling the market data subscription ***/
            //! [cancelmktdata]
            client.cancelMktData(1001);
            client.cancelMktData(1002);
            client.cancelMktData(1003);
            client.cancelMktData(1014);
            client.cancelMktData(1015);
            client.cancelMktData(1016);
            client.cancelMktData(1017);
            client.cancelMktData(1018);
            client.cancelMktData(1019);
            //! [cancelmktdata]
        }

        private static void tickOptionComputationOperations(EClientSocket client)
        {
            /*** Requesting real time market data ***/
            client.reqMarketDataType(4);

            //! [reqmktdata]
            client.reqMktData(2001, ContractSamples.OptionWithLocalSymbol(), string.Empty, false, false, null);
            //! [reqmktdata]

            Thread.Sleep(10000);

            /*** Canceling the market data subscription ***/
            //! [cancelmktdata]
            client.cancelMktData(2001);
            //! [cancelmktdata]
        }

        private static void marketDepthOperations(EClientSocket client)
        {
            /*** Requesting the Deep Book ***/
            //! [reqmarketdepth]
            client.reqMarketDepth(2001, ContractSamples.EurGbpFx(), 5, false, null);
            //! [reqmarketdepth]
            Thread.Sleep(2000);
            /*** Canceling the Deep Book request ***/
            //! [cancelmktdepth]
            client.cancelMktDepth(2001, false);
            //! [cancelmktdepth]

            /*** Requesting the Deep Book ***/
            //! [reqmarketdepth]
            client.reqMarketDepth(2002, ContractSamples.EuropeanStock(), 5, true, null);
            //! [reqmarketdepth]
            Thread.Sleep(5000);
            /*** Canceling the Deep Book request ***/
            //! [cancelmktdepth]
            client.cancelMktDepth(2002, true);
            //! [cancelmktdepth]

            /*** Requesting Market Depth Exchanges ***/
            Thread.Sleep(2000);
            //! [reqMktDepthExchanges]
            client.reqMktDepthExchanges();
            //! [reqMktDepthExchanges]
        }

        private static void realTimeBars(EClientSocket client)
        {
            /*** Requesting real time bars ***/
            //! [reqrealtimebars]
            client.reqRealTimeBars(3001, ContractSamples.EurGbpFx(), 5, "MIDPOINT", true, null);
            //! [reqrealtimebars]
            Thread.Sleep(2000);
            /*** Canceling real time bars ***/
            //! [cancelrealtimebars]
            client.cancelRealTimeBars(3001);
            //! [cancelrealtimebars]
        }

        private static void marketDataType(EClientSocket client)
        {
            //! [reqmarketdatatype]
            /*** Switch to live (1) frozen (2) delayed (3) or delayed frozen (4)***/
            client.reqMarketDataType(2);
            //! [reqmarketdatatype]
        }

        private static void historicalDataRequests(EClientSocket client)
        {
            /*** Requesting historical data ***/
            //! [reqhistoricaldata]
            String queryTime = DateTime.Now.ToUniversalTime().AddMonths(-6).ToString("yyyyMMdd-HH:mm:ss");
            client.reqHistoricalData(4001, ContractSamples.EurGbpFx(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, false, null);
            client.reqHistoricalData(4002, ContractSamples.EuropeanStock(), queryTime, "10 D", "1 min", "TRADES", 1, 1, false, null);
            client.reqHistoricalData(4003, ContractSamples.USStockAtSmart(), queryTime, "1 M", "1 day", "SCHEDULE", 1, 1, false, null);
            //! [reqhistoricaldata]
            Thread.Sleep(2000);
            /*** Canceling historical data requests ***/
            client.cancelHistoricalData(4001);
            client.cancelHistoricalData(4002);
            client.cancelHistoricalData(4003);
        }

        private static void optionsOperations(EClientSocket client)
        {
            //! [reqsecdefoptparams]
            client.reqSecDefOptParams(0, "IBM", "", "STK", 8314);
            //! [reqsecdefoptparams]

            /*** Calculating implied volatility ***/
            //! [calculateimpliedvolatility]
            client.calculateImpliedVolatility(5001, ContractSamples.OptionWithLocalSymbol(), 0.5, 55, null);
            //! [calculateimpliedvolatility]
            /*** Canceling implied volatility ***/
            client.cancelCalculateImpliedVolatility(5001);
            /*** Calculating option's price ***/
            //! [calculateoptionprice]
            client.calculateOptionPrice(5002, ContractSamples.OptionWithLocalSymbol(), 0.6, 55, null);
            //! [calculateoptionprice]
            /*** Canceling option's price calculation ***/
            client.cancelCalculateOptionPrice(5002);
            /*** Exercising options ***/
            //! [exercise_options]
            client.exerciseOptions(5003, ContractSamples.OptionWithTradingClass(), 1, 1, null, 1, "20231018-12:00:00", "CustAcct", true);
            //! [exercise_options]
        }

        private static void contractOperations(EClientSocket client)
        {
            //! [reqcontractdetails]
            client.reqContractDetails(209, ContractSamples.OptionForQuery());
            client.reqContractDetails(210, ContractSamples.EurGbpFx());
            client.reqContractDetails(211, ContractSamples.Bond());
            client.reqContractDetails(212, ContractSamples.FuturesOnOptions());
            client.reqContractDetails(213, ContractSamples.SimpleFuture());
            client.reqContractDetails(214, ContractSamples.USStockAtSmart());
            client.reqContractDetails(215, ContractSamples.CryptoContract());
            client.reqContractDetails(216, ContractSamples.ByIssuerId()); 
            client.reqContractDetails(217, ContractSamples.Fund());
            client.reqContractDetails(218, ContractSamples.USStock());
            client.reqContractDetails(219, ContractSamples.USStockAtSmart());
            //! [reqcontractdetails]

            Thread.Sleep(2000);
            //! [reqmatchingsymbols]
            client.reqMatchingSymbols(211, "IBM");
            //! [reqmatchingsymbols]
        }

        private static void contractNewsFeed(EClientSocket client)
        {
            //! [reqcontractdetailsnews]
            client.reqContractDetails(211, ContractSamples.NewsFeedForQuery());
            //! [reqcontractdetailsnews]
        }

        private static void marketScanners(EClientSocket client)
        {
            /*** Requesting all available parameters which can be used to build a scanner request ***/
            //! [reqscannerparameters]
            client.reqScannerParameters();
            //! [reqscannerparameters]
            Thread.Sleep(2000);

            /*** Triggering a scanner subscription ***/
            //! [reqscannersubscription]
            client.reqScannerSubscription(7001, ScannerSubscriptionSamples.HighOptVolumePCRatioUSIndexes(), "", null);
			
			TagValue t1 = new TagValue("usdMarketCapAbove", "10000");
			TagValue t2 = new TagValue("optVolumeAbove", "1000");
			TagValue t3 = new TagValue("avgVolumeAbove", "100000000");

			List<TagValue> TagValues = new List<TagValue>{t1, t2, t3};
			client.reqScannerSubscription(7002, ScannerSubscriptionSamples.HotUSStkByVolume(), null, TagValues); // requires TWS v973+
			
            //! [reqscannersubscription]

			//! [reqcomplexscanner]
			
			TagValue t = new TagValue("underConID", "265598");
			List<TagValue> AAPLConIDTag = new List<TagValue>{t};
			client.reqScannerSubscription(7003, ScannerSubscriptionSamples.ComplexOrdersAndTrades(), null, AAPLConIDTag); // requires TWS v975+
			
			//! [reqcomplexscanner]
			
            Thread.Sleep(2000);
            /*** Canceling the scanner subscription ***/
            //! [cancelscannersubscription]
            client.cancelScannerSubscription(7001);
			client.cancelScannerSubscription(7002);
			client.cancelScannerSubscription(7003);

            //! [cancelscannersubscription]
        }

        private static void fundamentals(EClientSocket client)
        {
            /*** Requesting Fundamentals ***/
            //! [reqfundamentaldata]
            client.reqFundamentalData(8001, ContractSamples.USStock(), "ReportsFinSummary", null);
            //! [reqfundamentaldata]
            Thread.Sleep(2000);
            /*** Canceling fundamentals request ***/
            //! [cancelfundamentaldata]
            client.cancelFundamentalData(8001);
            //! [cancelfundamentaldata]
        }

        private static void bulletins(EClientSocket client)
        {
            /*** Requesting Interactive Broker's news bulletins */
            //! [reqnewsbulletins]
            client.reqNewsBulletins(true);
            //! [reqnewsbulletins]
            Thread.Sleep(2000);
            /*** Canceling IB's news bulletins ***/
            //! [cancelnewsbulletins]
            client.cancelNewsBulletin();
            //! [cancelnewsbulletins]
        }

        private static void accountOperations(EClientSocket client)
        {
            /*** Requesting managed accounts***/
            //! [reqmanagedaccts]
            client.reqManagedAccts();
            //! [reqmanagedaccts]
            /*** Requesting accounts' summary ***/
            Thread.Sleep(2000);
            //! [reqaaccountsummary]
            client.reqAccountSummary(9001, "All", AccountSummaryTags.GetAllTags());
            //! [reqaaccountsummary]

            //! [reqaaccountsummaryledger]
            client.reqAccountSummary(9002, "All", "$LEDGER");
            //! [reqaaccountsummaryledger]
            Thread.Sleep(2000);
            //! [reqaaccountsummaryledgercurrency]
            client.reqAccountSummary(9003, "All", "$LEDGER:EUR");
            //! [reqaaccountsummaryledgercurrency]
            Thread.Sleep(2000);
            //! [reqaaccountsummaryledgerall]
            client.reqAccountSummary(9004, "All", "$LEDGER:ALL");
            //! [reqaaccountsummaryledgerall]

            //! [cancelaaccountsummary]
            client.cancelAccountSummary(9001);
            client.cancelAccountSummary(9002);
            client.cancelAccountSummary(9003);
            client.cancelAccountSummary(9004);
            //! [cancelaaccountsummary]

            /*** Subscribing to an account's information. Only one at a time! ***/
            Thread.Sleep(2000);
            //! [reqaaccountupdates]
            client.reqAccountUpdates(true, "U150462");
            //! [reqaaccountupdates]
            Thread.Sleep(2000);
            //! [cancelaaccountupdates]
            client.reqAccountUpdates(false, "U150462");
            //! [cancelaaccountupdates]

            //! [reqaaccountupdatesmulti]
            client.reqAccountUpdatesMulti(9002, "U150462", "EUstocks", true);
            //! [reqaaccountupdatesmulti]

            Thread.Sleep(2000);
            /*** Requesting all accounts' positions. ***/
            //! [reqpositions]
            client.reqPositions();
            //! [reqpositions]
            Thread.Sleep(2000);
            //! [cancelpositions]
            client.cancelPositions();
            //! [cancelpositions]

            //! [reqpositionsmulti]
            client.reqPositionsMulti(9003, "DU74649", "EUstocks");
            //! [reqpositionsmulti]

            //! [reqfamilycodes]
            client.reqFamilyCodes();
            //! [reqfamilycodes]

            //! [requserinfo]
            client.reqUserInfo(0);
            //! [requserinfo]

        }

        private static void orderOperations(EClientSocket client, int nextOrderId)
        {
            /*** Requesting the next valid id ***/
            //! [reqids]
            //The parameter is always ignored.
            client.reqIds(-1);
            //! [reqids]
            //Thread.Sleep(1000);
            /*** Requesting all open orders ***/
            //! [reqallopenorders]
            client.reqAllOpenOrders();
            //! [reqallopenorders]
            //Thread.Sleep(1000);
            /*** Taking over orders to be submitted via TWS ***/
            //! [reqautoopenorders]
            client.reqAutoOpenOrders(true);
            //! [reqautoopenorders]
            //Thread.Sleep(1000);
            /*** Requesting this API client's orders ***/
            //! [reqopenorders]
            client.reqOpenOrders();
            //! [reqopenorders]
            //Thread.Sleep(1000);
            //BracketSample(client, nextOrderId);

            /*** Placing/modifying an order - remember to ALWAYS increment the nextValidId after placing an order so it can be used for the next one! 
			Note if there are multiple clients connected to an account, the order ID must also be greater than all order IDs returned for orders to orderStatus and openOrder to this client.
			***/
            //! [order_submission]
            client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.TrailingStopLimit("BUY", 1, 5, 5, 110));
            //! [order_submission]

            //! [place_midprice]
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), OrderSamples.Midprice("BUY", 1, 150));
            //! [place_midprice]

            //! [faorderoneaccount]
            Order faOrderOneAccount = OrderSamples.MarketOrder("BUY", 100);
            // Specify the Account Number directly
            faOrderOneAccount.Account = "DU119915";
            client.placeOrder(nextOrderId++, ContractSamples.USStock(), faOrderOneAccount);
            //! [faorderoneaccount]

            //! [faordergroup]
            Order faOrderGroup = OrderSamples.LimitOrder("BUY", 200, 10);
            faOrderGroup.FaGroup = "MyTestGroup1";
            faOrderGroup.FaMethod = "AvailableEquity";
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), faOrderGroup);
            //! [faordergroup]

            //! [faorderuserdefinedgroup]
            Order faOrderUserDefinedGroup = OrderSamples.LimitOrder("BUY", 200, 10);
            faOrderUserDefinedGroup.FaGroup = "MyTestProfile1";
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), faOrderUserDefinedGroup);
            //! [faorderuserdefinedgroup]

            //! [modelorder]
            Order modelOrder = OrderSamples.LimitOrder("BUY", 200, 100);
            modelOrder.Account = "DF12345";  // master FA account number
            modelOrder.ModelCode = "Technology"; // model for tech stocks first created in TWS
            client.placeOrder(nextOrderId++, ContractSamples.USStock(), modelOrder);
            //! [modelorder]

            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtBOX(), OrderSamples.Block("BUY", 50, 20));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtBOX(), OrderSamples.BoxTop("SELL", 10));
            //client.placeOrder(nextOrderId++, ContractSamples.FutureComboContract(), OrderSamples.ComboLimitOrder("SELL", 1, 1, false));
            //client.placeOrder(nextOrderId++, ContractSamples.StockComboContract(), OrderSamples.ComboMarketOrder("BUY", 1, true));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionComboContract(), OrderSamples.ComboMarketOrder("BUY", 1, false));
            //client.placeOrder(nextOrderId++, ContractSamples.StockComboContract(), OrderSamples.LimitOrderForComboWithLegPrices("BUY", 1, new double[]{10, 5}, true));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.Discretionary("SELL", 1, 45, 0.5));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtBOX(), OrderSamples.LimitIfTouched("BUY", 1, 30, 34));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.LimitOnClose("SELL", 1, 34));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.LimitOnOpen("BUY", 1, 35));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.MarketIfTouched("BUY", 1, 30));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.MarketOnClose("SELL", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.MarketOnOpen("BUY", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.MarketOrder("SELL", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.MarketToLimit("BUY", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtIse(), OrderSamples.MidpointMatch("BUY", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.MarketToLimit("BUY", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.Stop("SELL", 1, 34.4));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.StopLimit("BUY", 1, 35, 33));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.StopWithProtection("SELL", 1, 45));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.SweepToFill("BUY", 1, 35));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.TrailingStop("SELL", 1, 0.5, 30));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.TrailingStopLimit("BUY", 1, 2, 5, 50));
            //client.placeOrder(nextOrderId++, ContractSamples.NormalOption(), OrderSamples.Volatility("SELL", 1, 5, 2));

            

            //NOTE: the following orders are not supported for Paper Trading
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.AtAuction("BUY", 100, 30.0));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtBOX(), OrderSamples.AuctionLimit("SELL", 10, 30.0, 2));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtBOX(), OrderSamples.AuctionPeggedToStock("BUY", 10, 30, 0.5));
            //client.placeOrder(nextOrderId++, ContractSamples.OptionAtBOX(), OrderSamples.AuctionRelative("SELL", 10, 0.6));
            //client.placeOrder(nextOrderId++, ContractSamples.SimpleFuture(), OrderSamples.MarketWithProtection("BUY", 1));
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(), OrderSamples.PassiveRelative("BUY", 1, 0.5));

            //208813720 (GOOG)
            //client.placeOrder(nextOrderId++, ContractSamples.USStock(),
            //    OrderSamples.PeggedToBenchmark("SELL", 100, 33, true, 0.1, 1, 208813720, "ARCA", 750, 650, 800));

            //STOP ADJUSTABLE ORDERS
            //Order stpParent = OrderSamples.Stop("SELL", 100, 30);
            //stpParent.OrderId = nextOrderId++;
            //client.placeOrder(stpParent.OrderId, ContractSamples.EuropeanStock(), stpParent);
            //client.placeOrder(nextOrderId++, ContractSamples.EuropeanStock(), OrderSamples.AttachAdjustableToStop(stpParent, 35, 32, 33));
            //client.placeOrder(nextOrderId++, ContractSamples.EuropeanStock(), OrderSamples.AttachAdjustableToStopLimit(stpParent, 35, 33, 32, 33));
            //client.placeOrder(nextOrderId++, ContractSamples.EuropeanStock(), OrderSamples.AttachAdjustableToTrail(stpParent, 35, 32, 32, 1, 0));

            //Order lmtParent = OrderSamples.LimitOrder("BUY", 100, 30);
            //lmtParent.OrderId = nextOrderId++;
            //client.placeOrder(lmtParent.OrderId, ContractSamples.EuropeanStock(), lmtParent);
            //Attached TRAIL adjusted can only be attached to LMT parent orders.
            //client.placeOrder(nextOrderId++, ContractSamples.EuropeanStock(), OrderSamples.AttachAdjustableToTrailAmount(lmtParent, 34, 32, 33, 0.008));
            //TestAlgoSamples(client, nextOrderId);
            //Thread.Sleep(30000);
            //! [cancelorder]
            client.cancelOrder(nextOrderId - 1, OrderSamples.OrderCancelEmpty());
            //! [cancelorder]
            /*** Cancel all orders for all accounts ***/
            //! [reqglobalcancel]
            client.reqGlobalCancel(OrderSamples.OrderCancelEmpty());
            //! [reqglobalcancel]
            /*** Request the day's executions ***/
            //! [reqexecutions]
            client.reqExecutions(10001, new ExecutionFilter());
            //! [reqexecutions]

            /*** Requesting completed orders ***/
            //! [reqcompletedorders]
            client.reqCompletedOrders(false);
            //! [reqcompletedorders]

            //! [crypto_order_submission]
            client.placeOrder(nextOrderId++, ContractSamples.CryptoContract(), OrderSamples.LimitOrder("BUY", Util.StringToDecimal("0.00001234"), 3370));
            //! [crypto_order_submission]

            //! [order_submission_with_manual_order_time]
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), OrderSamples.LimitOrderWithManualOrderTime("BUY", Util.StringToDecimal("100"), 111.11, "20220314-13:00:00"));
            //! [order_submission_with_manual_order_time]

            Thread.Sleep(3000);

            //! [cancel_order_with_manual_order_cancel_time]
            client.cancelOrder(nextOrderId - 1, OrderSamples.OrderCancelWithManualTime("20240614-00:00:08"));
            //! [cancel_order_with_manual_order_cancel_time]

            //! [pegbest_up_to_mid_order_submission]
            client.placeOrder(nextOrderId++, ContractSamples.IBKRATSContract(), OrderSamples.PegBestUpToMidOrder("BUY", Util.StringToDecimal("100"), 111.11, 100, 200, 0.02, 0.025));
            //! [pegbest_up_to_mid_order_submission]

            //! [pegbest_order_submission]
            client.placeOrder(nextOrderId++, ContractSamples.IBKRATSContract(), OrderSamples.PegBestOrder("BUY", Util.StringToDecimal("100"), 111.11, 100, 200, 0.03));
            //! [pegbest_order_submission]

            //! [pegmid_order_submission]
            client.placeOrder(nextOrderId++, ContractSamples.IBKRATSContract(), OrderSamples.PegMidOrder("BUY", Util.StringToDecimal("100"), 111.11, 100, 0.02, 0.025));
            //! [pegmid_order_submission]

            //! [order_submission_with_customer_account]
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), OrderSamples.LimitOrderWithCustomerAccount("BUY", Util.StringToDecimal("100"), 111.11, "CustAcct"));
            //! [order_submission_with_customer_account]

            //! [order_submission_with_include_overnight]
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), OrderSamples.LimitOrderWithIncludeOvernight("BUY", Util.StringToDecimal("100"), 111.11));
            //! [order_submission_with_include_overnight]

            //! [cme_tagging_fields]
            client.placeOrder(nextOrderId++, ContractSamples.SimpleFuture(), OrderSamples.LimitOrderWithCmeTaggingFields("BUY", Util.StringToDecimal("1"), 5333, "ABCD", 1));
            Thread.Sleep(5000);
            client.cancelOrder(nextOrderId - 1, OrderSamples.OrderCancelWithCmeTaggingFields("BCDE", 0));
            Thread.Sleep(2000);
            client.placeOrder(nextOrderId++, ContractSamples.SimpleFuture(), OrderSamples.LimitOrderWithCmeTaggingFields("BUY", Util.StringToDecimal("1"), 5444, "CDEF", 0));
            Thread.Sleep(5000);
            client.reqGlobalCancel(OrderSamples.OrderCancelWithCmeTaggingFields("DEFG", 1));
            //! [cme_tagging_fields]

            //! [order_submission_with_imbalance_only]
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), OrderSamples.LimitOnCloseOrderWithImbalanceOnly("BUY", Util.StringToDecimal("100"), 44.44));
            //! [order_submission_with_imbalance_only]
        }

        private static void newsOperations(EClientSocket client)
        {
            /*** Requesting news ticks ***/
            //! [reqNewsTicks]
            client.reqMktData(12001, ContractSamples.USStockAtSmart(), "mdoff,292", false, false, null);
            //! [reqNewsTicks]

            Thread.Sleep(5000);

            /*** Canceling news ticks ***/
            //! [cancelNewsTicks]
            client.cancelMktData(12001);
            //! [cancelNewsTicks]

            // Requesting news providers
            Thread.Sleep(2000);
            //! [reqNewsProviders]
            client.reqNewsProviders();
            //! [reqNewsProviders]

            // Requesting news article
            Thread.Sleep(2000);
            //! [reqNewsArticle]
            client.reqNewsArticle(12002, "BZ", "BZ$04507322", null);
            //! [reqNewsArticle]

            // Requesting historical news
            Thread.Sleep(2000);
            //! [reqHistoricalNews]
            client.reqHistoricalNews(12003, 8314, "BZ+FLY", "", "", 10, null);
            //! [reqHistoricalNews]

        }

        private static void OcaSample(EClientSocket client, int nextOrderId)
        {
            //OCA ORDER
            //! [ocasubmit]
            List<Order> ocaOrders = new List<Order>();
            ocaOrders.Add(OrderSamples.LimitOrder("BUY", 1, 10));
            ocaOrders.Add(OrderSamples.LimitOrder("BUY", 1, 11));
            ocaOrders.Add(OrderSamples.LimitOrder("BUY", 1, 12));
            OrderSamples.OneCancelsAll("TestOCA_" + nextOrderId, ocaOrders, 2);
            foreach (Order o in ocaOrders)
                client.placeOrder(nextOrderId++, ContractSamples.USStock(), o);
            //! [ocasubmit]
        }

        private static void ConditionSamples(EClientSocket client, int nextOrderId)
        {
            //! [order_conditioning_activate]
            Order mkt = OrderSamples.MarketOrder("BUY", 100);
            //Order will become active if conditioning criteria is met
            mkt.Conditions.Add(OrderSamples.PriceCondition(208813720, "SMART", 600, false, false));
            mkt.Conditions.Add(OrderSamples.ExecutionCondition("EUR.USD", "CASH", "IDEALPRO", true));
            mkt.Conditions.Add(OrderSamples.MarginCondition(30, true, false));
            mkt.Conditions.Add(OrderSamples.PercentageChangeCondition(15.0, 208813720, "SMART", true, true));
            mkt.Conditions.Add(OrderSamples.TimeCondition("20160118 23:59:59 US/Eastern", true, false));
            mkt.Conditions.Add(OrderSamples.VolumeCondition(208813720, "SMART", false, 100, true));
            client.placeOrder(nextOrderId++, ContractSamples.EuropeanStock(), mkt);
            //! [order_conditioning_activate]

            //Conditions can make the order active or cancel it. Only LMT orders can be conditionally canceled.
            //! [order_conditioning_cancel]
            Order lmt = OrderSamples.LimitOrder("BUY", 100, 20);
            //The active order will be cancelled if conditioning criteria is met
            lmt.ConditionsCancelOrder = true;
            lmt.Conditions.Add(OrderSamples.PriceCondition(208813720, "SMART", 600, false, false));
            client.placeOrder(nextOrderId++, ContractSamples.EuropeanStock(), lmt);
            //! [order_conditioning_cancel]
        }

        private static void BracketSample(EClientSocket client, int nextOrderId)
        {
            //BRACKET ORDER
            //! [bracketsubmit]
            List<Order> bracket = OrderSamples.BracketOrder(nextOrderId++, "BUY", 100, 30, 40, 20);
            foreach (Order o in bracket)
                client.placeOrder(o.OrderId, ContractSamples.EuropeanStock(), o);
            //! [bracketsubmit]
        }

        private static void HedgeSample(EClientSocket client, int nextOrderId)
        {
            //F Hedge order
            //! [hedgesubmit]
            //Parent order on a contract which currency differs from your base currency
            Order parent = OrderSamples.LimitOrder("BUY", 100, 10);
            parent.OrderId = nextOrderId++;
            parent.Transmit = false;
            //Hedge on the currency conversion
            Order hedge = OrderSamples.MarketFHedge(parent.OrderId, "BUY");
            //Place the parent first...
            client.placeOrder(parent.OrderId, ContractSamples.EuropeanStock(), parent);
            //Then the hedge order
            client.placeOrder(nextOrderId++, ContractSamples.EurGbpFx(), hedge);
            //! [hedgesubmit]
        }

        private static void TestAlgoSamples(EClientSocket client, int nextOrderId)
        {
            //! [algo_base_order]
            Order baseOrder = OrderSamples.LimitOrder("BUY", 1000, 1);
            //! [algo_base_order]

            //! [arrivalpx]
            AvailableAlgoParams.FillArrivalPriceParams(baseOrder, 0.1, "Aggressive", "09:00:00 US/Eastern", "16:00:00 US/Eastern", true, true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [arrivalpx]

            Thread.Sleep(500);

            //! [darkice]
            AvailableAlgoParams.FillDarkIceParams(baseOrder, 10, "09:00:00 US/Eastern", "16:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [darkice]

            Thread.Sleep(500);

            //! [ad]
			// The Time Zone in "startTime" and "endTime" attributes is ignored and always defaulted to GMT
            AvailableAlgoParams.FillAccumulateDistributeParams(baseOrder, 10, 60, true, true, 1, true, true, "12:00:00", "16:00:00");
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [ad]

            Thread.Sleep(500);

            //! [twap]
            AvailableAlgoParams.FillTwapParams(baseOrder, "Marketable", "09:00:00 US/Eastern", "16:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [twap]

            Thread.Sleep(500);

            //! [vwap]
            AvailableAlgoParams.FillVwapParams(baseOrder, 0.2, "09:00:00 US/Eastern", "16:00:00 US/Eastern", true, true, true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [vwap]

            Thread.Sleep(500);

            //! [balanceimpactrisk]
            AvailableAlgoParams.FillBalanceImpactRiskParams(baseOrder, 0.1, "Aggressive", true);
            client.placeOrder(nextOrderId++, ContractSamples.USOptionContract(), baseOrder);
            //! [balanceimpactrisk]

            Thread.Sleep(500);

            //! [minimpact]
            AvailableAlgoParams.FillMinImpactParams(baseOrder, 0.3);
            client.placeOrder(nextOrderId++, ContractSamples.USOptionContract(), baseOrder);
            //! [minimpact]

            //! [adaptive]
            AvailableAlgoParams.FillAdaptiveParams(baseOrder, "Normal");
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [adaptive]

            //! [closepx]
            AvailableAlgoParams.FillClosePriceParams(baseOrder, 0.5, "Neutral", "12:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [closepx]

            //! [pctvol]
            AvailableAlgoParams.FillPctVolParams(baseOrder, 0.5, "12:00:00 US/Eastern", "14:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [pctvol]               

            //! [pctvolpx]
            AvailableAlgoParams.FillPriceVariantPctVolParams(baseOrder, 0.1, 0.05, 0.01, 0.2, "12:00:00 US/Eastern", "14:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [pctvolpx]

            //! [pctvolsz]
            AvailableAlgoParams.FillSizeVariantPctVolParams(baseOrder, 0.2, 0.4, "12:00:00 US/Eastern", "14:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [pctvolsz]

            //! [pctvoltm]
            AvailableAlgoParams.FillTimeVariantPctVolParams(baseOrder, 0.2, 0.4, "12:00:00 US/Eastern", "14:00:00 US/Eastern", true);
            client.placeOrder(nextOrderId++, ContractSamples.USStockAtSmart(), baseOrder);
            //! [pctvoltm]
		
            //! [jeff_vwap_algo]
            AvailableAlgoParams.FillJefferiesVWAPParams(baseOrder, "10:00:00 US/Eastern", "16:00:00 US/Eastern", 10, 10, "Exclude_Both", 130, 135, 1, 10, "Patience", false, "Midpoint");
            client.placeOrder(nextOrderId++, ContractSamples.JefferiesContract(), baseOrder);
            //! [jeff_vwap_algo]

            //! [csfb_inline_algo]
            AvailableAlgoParams.FillCSFBInlineParams(baseOrder, "10:00:00 US/Eastern", "16:00:00 US/Eastern", "Patient", 10, 20, 100, "Default", false, 40, 100, 100, 35);
            client.placeOrder(nextOrderId++, ContractSamples.CSFBContract(), baseOrder);
            //! [csfb_inline_algo]
        }

        private static void financialAdvisorOperations(EClientSocket client)
        {
            /*** Requesting FA information ***/
            //! [requestfaaliases]
            client.requestFA(Constants.FaAliases);
            //! [requestfaaliases]

            //! [requestfagroups]
            client.requestFA(Constants.FaGroups);
            //! [requestfagroups]

            /*** Replacing FA information - Fill in with the appropriate XML string. ***/
            //! [replacefaupdatedgroup]
            client.replaceFA(1000, Constants.FaGroups, FaAllocationSamples.FaUpdatedGroup);
            //! [replacefaupdatedgroup]

            //! [reqSoftDollarTiers]
            client.reqSoftDollarTiers(4001);
            //! [reqSoftDollarTiers]
        }

        private static void miscellaneous(EClientSocket client)
        {
            /*** Request TWS' current time ***/
            client.reqCurrentTime();
            /*** Setting TWS logging level  ***/
            client.setServerLogLevel(1);

            Thread.Sleep(3000);

            /*** Request TWS' current time in millis ***/
            client.reqCurrentTimeInMillis();
        }

        private static void linkingOperations(EClientSocket client)
        {
            client.verifyRequest("a name", "9.71");
            client.verifyMessage("apiData");

            //! [querydisplaygroups]
            client.queryDisplayGroups(9001);
            //! [querydisplaygroups]

            //! [subscribetogroupevents]
            client.subscribeToGroupEvents(9002, 1);
            //! [subscribetogroupevents]

            //! [updatedisplaygroup]
            client.updateDisplayGroup(9002, "8314@SMART");
            //! [updatedisplaygroup]

            //! [subscribefromgroupevents]
            client.unsubscribeFromGroupEvents(9002);
            //! [subscribefromgroupevents]
        }

        private static void marketRuleOperations(EClientSocket client) 
        {
            client.reqContractDetails(17001, ContractSamples.USStock());
            client.reqContractDetails(17002, ContractSamples.Bond());

            Thread.Sleep(2000);

            //! [reqmarketrule]
            client.reqMarketRule(26);
            client.reqMarketRule(240);
            //! [reqmarketrule]
        }

        private static void continuousFuturesOperations(EClientSocket client) 
        {
            client.reqContractDetails(18001, ContractSamples.ContFut());

            //! [reqhistoricaldatacontfut]
            client.reqHistoricalData(18002, ContractSamples.ContFut(), "", "1 Y", "1 month", "TRADES", 0, 1, false, null);
            Thread.Sleep(10000);
            client.cancelHistoricalData(18002);
            //! [reqhistoricaldatacontfut]
        }

        private static void whatIfSamples(EClientSocket client, int nextOrderId)
        {
            /*** Placing what-if order ***/
            //! [whatiforder]
            client.placeOrder(nextOrderId++, ContractSamples.BondWithCusip(), OrderSamples.WhatIfLimitOrder("BUY", 100, 20));
            //! [whatiforder]
        }
		
		private static void ibkratsSample(EClientSocket client, int nextOrderId)
        {
            //! [ibkratssubmit]
            Order ibkratsOrder = OrderSamples.LimitIBKRATS("BUY", 100, 330);
            client.placeOrder(nextOrderId++, ContractSamples.IBKRATSContract(), ibkratsOrder);
            //! [ibkratssubmit]
        }
    }
}
