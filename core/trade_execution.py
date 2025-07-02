#**2. `trade_execution.py` (Added disconnect check)**

import time
import threading
import traceback
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import BarData, TickAttrib # Import TickAttrib
from ibapi.scanner import ScannerSubscription
from ibapi.ticktype import TickTypeEnum # Import TickTypeEnum


# Keep IBKRWrapper mostly the same, just ensure callbacks exist
class IBKRWrapper(EWrapper):
    def __init__(self):
        super().__init__()
        self._historical_data_callbacks = {}
        self._scanner_data_callbacks = {}
        self._historical_news_storage = {}
        self.contract_details = []
        self.available_news_providers = []
        self._account_summary_data = {}
        self._account_summary_done = set()
        self._positions_data = {}
        self._positions_req_active = False
        # Add structure for storing completion of historical data requests
        self.historical_data_completed_reqs = set()

    def nextValidId(self, order_id: int):
        print(f"[DEBUG] nextValidId CALLED. order_id = {order_id}")
        super().nextValidId(order_id)
        # The connection_ready_event is now managed within TradeExecutionApp instance
        # Check if the attribute exists on the *instance* which inherits this
        if hasattr(self, 'connection_ready_event') and isinstance(self.connection_ready_event, threading.Event):
            if not self.connection_ready_event.is_set(): # Avoid setting multiple times
                print(f"[DEBUG] Attempting to set connection_ready_event (event found on self)...")
                self.connection_ready_event.set()
                print(f"[DEBUG] connection_ready_event SET.")
        else:
            # This might happen if called before TradeExecutionApp fully initializes, less likely
            print(f"[WARN] nextValidId called, but self.connection_ready_event not found or not an Event.")

    def error(self, *args):
        reqId = -1
        errorCode = -1
        errorString = ""
        advancedOrderRejectJson = ""
        num_args = len(args)

        # --- Keep your existing robust error parsing ---
        if num_args == 0:
             print(f"[API ERROR RECEIVED] - No arguments received?")
             return
        elif num_args == 3:
             reqId, errorCode, errorString = args
             print(f"[API ERROR RECEIVED] reqId={reqId}, code={errorCode}, msg='{errorString}' (3 args received)")
        elif num_args == 4:
             reqId, errorCode, errorString, advancedOrderRejectJson = args
             print(f"[API ERROR RECEIVED] reqId={reqId}, code={errorCode}, msg='{errorString}', advanced='{advancedOrderRejectJson}' (4 args received)")
        elif num_args == 5:
             # print(f"[API ERROR RECEIVED] (5 args received): {args}") # Can be verbose
             try:
                 # TWS API error often sends: reqId, timestamp, errorCode, errorMsg, advancedOrderRejectJson
                 reqId = args[0]
                 # timestamp = args[1] # We don't use timestamp here
                 errorCode = args[2]
                 errorString = args[3]
                 advancedOrderRejectJson = args[4] if len(args) > 4 else ""
                 print(f"[API ERROR INTERPRETED] reqId={reqId}, code={errorCode}, msg='{errorString}', advanced='{advancedOrderRejectJson}' (interpreted from 5 args)")
             except IndexError:
                  print("[ERROR] Could not interpret 5 args for error callback.")
                  print(f"[ERROR DETAILS] Args received: {args}")
                  return # Cannot proceed if interpretation fails
        else:
            print(f"[API ERROR RECEIVED] - Unexpected number of arguments ({num_args}): {args}")
            # Attempt basic mapping
            if num_args > 0: reqId = args[0]
            if num_args > 1: errorCode = args[1] # Usually code is 2nd or 3rd
            if num_args > 2: errorString = args[2] # Msg usually 3rd or 4th

        # --- Call super().error safely ---
        # It expects error(self, reqId: TickerId, errorCode: int, errorString: str, advancedOrderRejectJson="")
        try:
             # Ensure reqId, errorCode are ints and errorString is str
             safe_reqId = int(reqId) if reqId is not None else -1
             safe_errorCode = int(errorCode) if errorCode is not None else -1
             safe_errorString = str(errorString) if errorString is not None else ""
             safe_advanced = str(advancedOrderRejectJson) if advancedOrderRejectJson is not None else ""
             super().error(safe_reqId, safe_errorCode, safe_errorString, safe_advanced)
        except TypeError as te:
             # Fallback for older versions or different signatures
             try:
                  print(f"[WARN] super().error() with 4 args failed ({te}), trying 3 args...")
                  super().error(safe_reqId, safe_errorCode, safe_errorString)
             except Exception as e_fallback:
                  print(f"[ERROR] Failed to call super().error() even with fallback: {e_fallback}")
        except Exception as e_super:
             print(f"[ERROR] Exception calling super().error(): {e_super}")

        # Print specific formatted error for easier debugging
        print(f"ERROR {reqId} {errorCode} {errorString} {advancedOrderRejectJson}")


    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice,
                            permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        # Optional: Add more logic here to track order fills for live trading state
        print(f"[ORDER STATUS] ID={orderId}, Status={status}, Filled={filled}, Remaining={remaining}, AvgPrice={avgFillPrice}")

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        super().scannerData(reqId, rank, contractDetails, distance, benchmark, projection, legsStr)
        if reqId in self._scanner_data_callbacks:
            try:
                data_cb, _ = self._scanner_data_callbacks[reqId]
                data_cb(rank, contractDetails, distance, benchmark, projection, legsStr)
            except Exception as e:
                 print(f"[ERROR] Exception in scannerData data_cb for reqId={reqId}: {e}")

    def scannerDataEnd(self, reqId):
        super().scannerDataEnd(reqId)
        print(f"[INFO] Scanner data end for reqId={reqId}")
        if reqId in self._scanner_data_callbacks:
            try:
                _, end_cb = self._scanner_data_callbacks[reqId]
                end_cb()
                # Clean up callback to prevent memory leaks if scanner is run multiple times
                # del self._scanner_data_callbacks[reqId] # Consider if needed based on usage
            except Exception as e:
                print(f"[ERROR] Exception in scannerData end_cb for reqId={reqId}: {e}")
            finally:
                 # Ensure cleanup even if callback fails
                 self._scanner_data_callbacks.pop(reqId, None)


    def scannerParameters(self, xml):
        # print(f"ScannerParameters: {xml}\n") # Usually verbose, uncomment if needed
        super().scannerParameters(xml)


    def historicalData(self, reqId: int, bar: BarData):
        # Do not call super().historicalData(reqId, bar) if you override it
        # unless you need its base functionality (which is likely none).
        if reqId in self._historical_data_callbacks:
            try:
                callback_fn, symbol = self._historical_data_callbacks[reqId]
                # Pass the actual bar object to the callback
                callback_fn(symbol, bar)
            except Exception as e:
                 print(f"[ERROR] Exception in historicalData callback for reqId={reqId}, symbol={symbol}: {e}")
        # else: # Log if data received for unexpected reqId
        #    print(f"[WARN] Received historicalData for un-registered reqId: {reqId}")

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print(f"[INFO] Historical data end for reqId={reqId}. Start: {start}, End: {end}")
        # Mark this request ID as completed
        self.historical_data_completed_reqs.add(reqId)
        # Clean up the callback reference for this reqId
        if reqId in self._historical_data_callbacks:
            del self._historical_data_callbacks[reqId]

    # --- Keep other callbacks as they are unless issues arise ---
    def historicalNews(self, reqId, time_stamp, providerCode, articleId, headline):
        super().historicalNews(reqId, time_stamp, providerCode, articleId, headline)
        if reqId not in self._historical_news_storage:
            self._historical_news_storage[reqId] = []
        self._historical_news_storage[reqId].append(headline)

    def historicalNewsEnd(self, reqId, hasMore):
        super().historicalNewsEnd(reqId, hasMore)
        print(f"[NEWS] Historical news ended for reqId={reqId}, hasMore={hasMore}")

    def newsProviders(self, newsProviders):
        super().newsProviders(newsProviders)
        self.available_news_providers = newsProviders
        print("[NEWS] Providers available:")
        for p in newsProviders:
            print(f"  - {p.providerCode} : {p.providerName}")

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)
        # It's safer to store details in a dictionary keyed by reqId if multiple requests can run concurrently
        # For simplicity, assuming only one reqContractDetails runs at a time for now
        self.contract_details.append(contractDetails)


    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)
        print(f"[CONTRACT] contractDetailsEnd for reqId={reqId}")
        # Signal completion if waiting for this specific request

    def accountSummary(self, reqId, account, tag, value, currency):
        super().accountSummary(reqId, account, tag, value, currency)
        if reqId not in self._account_summary_data:
            self._account_summary_data[reqId] = {}
        self._account_summary_data[reqId][tag] = (value, currency)

    def accountSummaryEnd(self, reqId):
        super().accountSummaryEnd(reqId)
        print(f"[INFO] accountSummaryEnd for reqId={reqId}")
        self._account_summary_done.add(reqId)
        # Clean up data for completed request ID
        # self._account_summary_data.pop(reqId, None) # Optional: Remove data after processing

    def position(self, account, contract, pos, avgCost):
        super().position(account, contract, pos, avgCost)
        symbol = contract.symbol
        # Store even if pos is 0 to correctly reflect no position
        # Store as dict for easier extension later
        self._positions_data[symbol] = {"shares": pos, "avg_cost": avgCost}

    def positionEnd(self):
        super().positionEnd()
        print("[INFO] positionEnd received.")
        self._positions_req_active = False


# Keep IBKRClient simple
class IBKRClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TradeExecutionApp(IBKRWrapper, IBKRClient):
    def __init__(self, config_dict):
        IBKRWrapper.__init__(self) # Initialize wrapper part first
        IBKRClient.__init__(self, wrapper=self) # Then client part, passing self (which is also the wrapper)

        self.config = config_dict
        self.host = self.config["ibkr"]["host"]
        self.port = self.config["ibkr"]["port"]
        self.client_id = self.config["ibkr"]["client_id"]
        self.next_order_id = None
        self.req_id_counter = 500 # Base for non-order requests
        self.connection_ready_event = threading.Event() # Event to signal connection readiness
        self._disconnect_called = False # Flag to prevent multiple disconnect logic runs
        self._lock = threading.Lock() # Lock for thread-safe access to shared resources like req_id_counter
        print("[DEBUG] TradeExecutionApp initialized, connection_ready_event created.")

    # Override nextValidId from EWrapper to capture the first valid order ID
    # and signal that the connection is ready.
    def nextValidId(self, order_id: int):
        # This method is called by EWrapper -> EClient infrastructure
        # We capture the order_id provided by TWS/Gateway
        print(f"[DEBUG] TradeExecutionApp.nextValidId CALLED. order_id = {order_id}")
        # Call the EWrapper's implementation if it has any logic (optional but safe)
        super().nextValidId(order_id)
        # Store the next valid order ID
        self.next_order_id = order_id
        print(f"[INFO] Connection ready. Next Valid Order ID: {order_id}")
        # Signal that the connection is established and ready for requests
        if not self.connection_ready_event.is_set():
             print("[DEBUG] Attempting to set connection_ready_event...")
             self.connection_ready_event.set()
             print("[DEBUG] connection_ready_event SET.")


    def connect_to_ib(self):
        """Initiates connection to TWS/Gateway."""
        if self.isConnected():
            print("[WARN] Already connected.")
            return
        self._disconnect_called = False # Reset disconnect flag on new connection attempt
        print(f"[DEBUG] Attempting to connect to {self.host}:{self.port} with clientId={self.client_id}...")
        try:
            self.connect(self.host, self.port, self.client_id)
            print(f"[DEBUG] self.connect() method called.")
            # Start the message processing loop in a separate thread
            # Daemon=True allows the main program to exit even if this thread is running
            api_thread = threading.Thread(target=self.run_loop, daemon=True, name="IBAPIThread")
            api_thread.start()
            print(f"[DEBUG] API thread started ({api_thread.name}).")

        except Exception as e:
            print(f"[ERROR] EXCEPTION during self.connect() or thread start: {e}")
            print("[ERROR] Connection likely failed immediately.")

    def run_loop(self):
        """Runs the EClient message processing loop."""
        print("[DEBUG] API thread: Entered run_loop.")
        # self.run() is blocking and processes messages from TWS/Gateway
        # It will exit automatically if disconnect() is called or connection drops
        try:
            print("[DEBUG] API thread: Calling self.run() (blocking)...")
            self.run() # Start the message loop
            print("[DEBUG] API thread: self.run() EXITED.")
        except OSError as e:
             # Common errors during disconnect: "socket closed", "connection reset"
             if not self._disconnect_called: # Only log error if disconnect wasn't intentional
                 print(f"[WARN] OSError in API run_loop (likely connection issue/disconnect): {e}")
        except Exception as e:
            if not self._disconnect_called: # Only log if unexpected
                print(f"[ERROR] EXCEPTION in API run_loop (self.run()): {e}")
                traceback.print_exc() # Print stack trace for unexpected errors
        finally:
             # This block runs when self.run() exits
             print(f"[DEBUG] API thread: Exiting run_loop. Final self.isConnected(): {self.isConnected()}")
             # Ensure disconnected state if loop exits unexpectedly
             if self.isConnected():
                  print("[DEBUG] API thread: Still connected after run() exit, attempting internal disconnect.")
                  # Use the internal disconnect method
                  self._internal_disconnect()


    def disconnect(self):
        """Requests disconnection from TWS/Gateway."""
        print("[DEBUG] ***** disconnect() CALLED *****")
        # Print stack trace to see who called disconnect
        # print("Call stack leading to disconnect():")
        # traceback.print_stack()
        # print("--- End of stack ---")

        with self._lock: # Ensure disconnect logic is atomic
            if self._disconnect_called or not self.isConnected():
                print("[DEBUG] Disconnect already called or not connected. Ignoring.")
                return
            self._disconnect_called = True # Set flag immediately

        print("[DEBUG] Initiating disconnection process...")
        self._internal_disconnect()


    def _internal_disconnect(self):
         """Handles the actual disconnection call."""
         # This should only be called from disconnect() or run_loop() finally block
         if self.isConnected():
             try:
                 print("[DEBUG] Calling EClient.disconnect()...")
                 # EClient.disconnect() signals the run() loop to stop and closes the socket
                 super().disconnect()
                 print("[DEBUG] EClient.disconnect() finished.")
             except Exception as e:
                 print(f"[ERROR] Exception during EClient.disconnect(): {e}")
         else:
             print("[DEBUG] Already disconnected in _internal_disconnect.")


    def get_next_req_id(self):
        """Generates the next request ID for non-order requests."""
        with self._lock: # Protect access to the counter
            self.req_id_counter += 1
            return self.req_id_counter

    # --- Callback Registration Methods ---
    def register_historical_data_callback(self, req_id: int, callback_fn, symbol: str):
        """Registers a function to call when historical data arrives for a reqId."""
        if req_id in self._historical_data_callbacks:
             print(f"[WARN] Overwriting historical data callback for reqId {req_id}")
        self._historical_data_callbacks[req_id] = (callback_fn, symbol)
        # Reset completion status for this req_id when registering
        self.historical_data_completed_reqs.discard(req_id)


    def register_scanner_data_callback(self, req_id: int, on_data, on_done):
        """Registers functions for scanner data and completion."""
        if req_id in self._scanner_data_callbacks:
            print(f"[WARN] Overwriting scanner data callback for reqId {req_id}")
        self._scanner_data_callbacks[req_id] = (on_data, on_done)


    # --- Data Fetching Methods ---

    def get_conid_for_symbol(self, symbol: str):
        """Fetches the primary conId for a given stock symbol."""
        # This needs proper synchronization if called concurrently
        # For now, assumes sequential calls
        self.contract_details = [] # Clear previous results for this simple implementation
        req_id = self.get_next_req_id()
        contract = self.create_contract(symbol)
        print(f"[DEBUG] Requesting contract details for {symbol} (reqId={req_id})...")

        # --- Event-based waiting (Conceptual - requires modification in callbacks) ---
        # details_event = threading.Event()
        # self.register_contract_details_end_callback(req_id, details_event.set) # Need this callback registration
        self.reqContractDetails(req_id, contract)
        # success = details_event.wait(timeout=5.0) # Wait for contractDetailsEnd
        # self.unregister_contract_details_end_callback(req_id) # Cleanup
        # if not success: print(f"[WARN] Timeout waiting for contract details for {symbol}")
        # --- End Event-based waiting ---

        # Using simple sleep for now as event handling isn't fully implemented
        time.sleep(2.0) # Reduced sleep, but still unreliable

        if self.contract_details:
            # Find the primary listing or the first one returned
            primary_details = None
            for details in self.contract_details:
                 # Look for primary exchange hint or just take the first valid one
                 if details.contract.primaryExchange: # Check if primaryExchange is set
                      # Add specific exchange checks if needed (e.g., NYSE, NASDAQ)
                      primary_details = details
                      break
            if not primary_details and self.contract_details:
                 primary_details = self.contract_details[0] # Fallback to first result

            if primary_details:
                 con_id = primary_details.contract.conId
                 print(f"[CONTRACT] Found conId={con_id} for symbol={symbol}")
                 return con_id
            else:
                 print(f"[CONTRACT] No suitable contract details found for {symbol}.")
                 return None
        else:
            print(f"[CONTRACT] No contract details received for {symbol} after wait.")
            return None

    def create_contract(self, symbol: str) -> Contract:
        """Creates a standard US stock contract object."""
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART" # SMART routing
        contract.currency = "USD"
        # Optional: Specify primary exchange if needed for disambiguation
        # contract.primaryExchange = "NASDAQ" # e.g., ARCA, NYSE, NASDAQ, BATS
        return contract

    def place_market_order(self, symbol: str, action: str, quantity: int):
        """Places a simple market order."""
        with self._lock: # Protect order ID usage
            if self.next_order_id is None:
                print("[ERROR] Cannot place order: No valid order ID received yet.")
                return None # Indicate failure
            if quantity <= 0:
                print(f"[WARN] Attempted to place order for {symbol} with invalid quantity {quantity}. Skipping.")
                return None

            current_order_id = self.next_order_id
            self.next_order_id += 1 # Increment for the next order

        contract = self.create_contract(symbol)
        order = Order()
        order.action = action.upper() # BUY or SELL
        order.orderType = "MKT"
        order.totalQuantity = abs(quantity) # Use absolute value
        order.transmit = True # Transmit the order immediately

        print(f"[ORDER] Placing {order.action} {order.totalQuantity} shares of {symbol} (OrderId: {current_order_id})")
        try:
            self.placeOrder(current_order_id, contract, order)
            return current_order_id # Return ID of placed order
        except Exception as e:
            print(f"[ERROR] Exception calling placeOrder for {symbol}: {e}")
            # Roll back order ID if placement failed? Complex, maybe just log error.
            return None


    def fetch_historical_news(self, symbol: str, start_time: str, end_time: str):
        """Fetches historical news headlines for a symbol."""
        # Ensure storage exists
        if not hasattr(self, '_historical_news_storage'): self._historical_news_storage = {}

        req_id = self.get_next_req_id()
        self._historical_news_storage[req_id] = [] # Initialize list for this request

        con_id = self.get_conid_for_symbol(symbol)
        if not con_id:
            print(f"[NEWS] No conId for {symbol}, cannot fetch news.")
            return []

        # Ensure provider list is populated
        if not self.available_news_providers:
            print("[NEWS] Requesting available news providers...")
            self.reqNewsProviders()
            time.sleep(2.0) # Wait for providers (could use event)
            if not self.available_news_providers:
                print("[NEWS] No news providers available after request.")
                return []

        # Join available provider codes
        provider_codes = ",".join([p.providerCode for p in self.available_news_providers])
        print(f"[NEWS] Requesting news for {symbol} (conId={con_id}) from {start_time} to {end_time} using providers: {provider_codes}")

        self.reqHistoricalNews(
            reqId=req_id, conId=con_id, providerCodes=provider_codes,
            startDateTime=start_time, endDateTime=end_time,
            totalResults=100, # Increase results limit if needed
            historicalNewsOptions=[] # No specific options for now
        )

        # --- Use Event-based wait (Conceptual) ---
        # news_event = threading.Event()
        # register_news_end_callback(req_id, news_event.set) # Need callback mechanism
        # success = news_event.wait(timeout=10.0)
        # if not success: print(f"[WARN] Timeout waiting for historical news for {symbol}")
        # --- End Event wait ---

        time.sleep(3.0) # Using sleep as placeholder

        # Return the collected headlines for this request ID
        return self._historical_news_storage.pop(req_id, []) # Use pop to get and remove data


    def fetch_account_summary(self, tags="TotalCashValue,NetLiquidation"):
        """Fetches specified account summary tags."""
        req_id = self.get_next_req_id()
        # Initialize data storage and completion status for this request
        self._account_summary_data[req_id] = {}
        self._account_summary_done.discard(req_id) # Remove if exists from previous runs

        print(f"[DEBUG] Requesting account summary (reqId={req_id}, tags={tags})")
        # Use "All" for group, could specify account ID if needed
        self.reqAccountSummary(req_id, "All", tags)

        # Wait for accountSummaryEnd callback
        t0 = time.time()
        timeout = 7.0
        while req_id not in self._account_summary_done:
            if time.time() - t0 > timeout:
                print(f"[WARN] Timeout ({timeout}s) waiting for accountSummaryEnd (reqId={req_id}).")
                self.cancelAccountSummary(req_id)
                print(f"[DEBUG] Cancelled account summary request {req_id} due to timeout.")
                # Clean up potentially partial data
                self._account_summary_data.pop(req_id, None)
                self._account_summary_done.discard(req_id)
                return {} # Return empty on timeout
            time.sleep(0.1) # Short sleep while waiting

        # Process the received data
        data = self._account_summary_data.pop(req_id, {}) # Get and remove data for req_id
        results = {}
        tag_list = tags.split(",")
        for tag in tag_list:
            tag_data = data.get(tag)
            if tag_data:
                val_str, _ = tag_data # Ignore currency for now
                try:
                    results[tag] = float(val_str)
                except (ValueError, TypeError):
                    print(f"[WARN] Could not convert account summary value '{val_str}' for tag '{tag}' to float.")
                    results[tag] = 0.0 # Default to 0 on conversion error
            else:
                results[tag] = 0.0 # Default to 0 if tag not found

        return results

    def fetch_positions(self):
        """Fetches current account positions."""
        # Reset state for this request
        self._positions_data = {}
        self._positions_req_active = True # Flag that a request is in progress

        print("[DEBUG] Requesting current positions...")
        self.reqPositions()

        # Wait for positionEnd callback
        t0 = time.time()
        timeout = 7.0
        while self._positions_req_active:
            if time.time() - t0 > timeout:
                print(f"[WARN] Timeout ({timeout}s) waiting for positionEnd.")
                self.cancelPositions() # Cancel the request
                print("[DEBUG] Cancelled positions request due to timeout.")
                # Return whatever data might have been received before timeout
                return dict(self._positions_data)
            time.sleep(0.1)

        print("[DEBUG] positionEnd received.")
        # Return a copy of the positions data
        return dict(self._positions_data)

    def wait_for_historical_data(self, req_ids, timeout=30.0):
         """Waits for historicalDataEnd for all specified req_ids."""
         start_time = time.time()
         pending_reqs = set(req_ids)
         print(f"[DEBUG] Waiting for historical data completion for {len(pending_reqs)} requests...")

         while pending_reqs:
             elapsed = time.time() - start_time
             if elapsed > timeout:
                 print(f"[WARN] Timeout ({timeout}s) waiting for historical data. Missing: {pending_reqs}")
                 # Optionally, remove the missing req_ids from the internal callback dicts
                 for req_id in pending_reqs:
                      self._historical_data_callbacks.pop(req_id, None)
                 return False # Indicate timeout

             # Check which requests are completed
             completed_now = pending_reqs.intersection(self.historical_data_completed_reqs)
             if completed_now:
                  # print(f"[DEBUG] Completed requests found: {completed_now}") # Optional Verbose
                  pending_reqs.difference_update(completed_now) # Remove completed ones

             if not pending_reqs:
                  print(f"[DEBUG] All {len(req_ids)} historical data requests completed.")
                  return True # All done

             time.sleep(0.2) # Small sleep to avoid busy-waiting

         # Should not be reached if loop condition is correct, but added for safety
         print("[DEBUG] Exited wait loop unexpectedly.")
         return True