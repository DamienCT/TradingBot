#**3. `workflow_manager.py` (Clear data, refine `max_len`, adjust logging)**

import time
import pytz
import math
import pandas as pd
from datetime import datetime, timedelta, time as dt_time
import sys
import traceback
import threading # Import threading for event-based wait (if implemented)

from core.trade_logger import TradeLogger
from core.scanner import Scanner
from core.multiIndicatorStrategy import MultiIndicatorStrategy


class WorkflowManager:
    def __init__(self, config, ib_client, data_fetcher):
        self.config = config
        self.ib_client = ib_client
        self.data_fetcher = data_fetcher
        self.scanner = Scanner(config, ib_client)
        self.profile_strategies = {}
        self.backtest_portfolios = {}
        self.trade_loggers = {}

        for rp_name in config["risk_profiles"].keys():
            self.profile_strategies[rp_name] = MultiIndicatorStrategy(config, profile_name=rp_name)
            self.backtest_portfolios[rp_name] = {
                "cash": config["account"]["initial_capital"],
                "positions": {}, "equity_curve": [], "trades": [] # Add trades list if needed
            }
            logger_instance = TradeLogger(config)
            logger_instance.set_profile_name(rp_name)
            self.trade_loggers[rp_name] = logger_instance

        self.symbols_for_day = []
        self.starting_value = config["account"]["initial_capital"]
        self.max_equity_dict = {rp: self.starting_value for rp in config["risk_profiles"]}
        self.max_drawdown_dict = {rp: 0.0 for rp in config["risk_profiles"]}
        self.real_portfolio = {} # For live mode state
        # Add daily state tracking
        self.reset_daily_state()
        # Add total state tracking (persists unless reset)
        self.total_trading_halted = {rp: False for rp in self.profile_strategies}


    def run_daily_workflow(self):
        # Initialize all loggers at the start
        for rp_name in self.trade_loggers:
            self.trade_loggers[rp_name].init_csv_logger()

        mode = self.config.get("mode", "live").lower()
        use_range = self.config.get("backtesting", {}).get("use_date_range", False)

        if mode == "historical" and use_range:
            self.run_backtest_for_date_range()
        elif mode == "historical":
            self.run_single_day_backtest()
        else:
            # Live mode setup
            print("[INFO] Starting Live Mode Workflow...")
            self.init_live_positions() # Fetch initial positions
            self.run_live_workflow() # Start the main live loop


    def finalize(self):
        """Closes loggers and performs final cleanup."""
        print("[INFO] Finalizing workflow...")
        for rp_name, logger in self.trade_loggers.items():
            try:
                logger.close_csv_logger()
                # Don't print inside the loop
            except Exception as e:
                 print(f"[ERROR] Error closing logger for {rp_name}: {e}")
        # Print closing message ONCE after the loop
        print("[LOGGER] All CSV log files closed.")


    def run_backtest_for_date_range(self):
        """Runs backtest simulation over a specified date range."""
        start_str = self.config["backtesting"]["start_date"]
        end_str = self.config["backtesting"]["end_date"]
        try:
            start_dt = datetime.strptime(start_str, "%Y%m%d")
            end_dt = datetime.strptime(end_str, "%Y%m%d")
        except ValueError:
            print("[ERROR] Invalid date format in backtesting config. Use YYYYMMDD.")
            return

        current_dt = start_dt
        while current_dt <= end_dt:
            # Check if it's a weekday (0=Monday, 6=Sunday)
            if current_dt.weekday() < 5: # Monday to Friday
                date_str = current_dt.strftime("%Y%m%d")
                # Set the current simulation date in the config for DataFetcher
                if "historical" not in self.config: self.config["historical"] = {}
                self.config["historical"]["start_date"] = date_str

                print(f"\n[BACKTEST] ---- Day {date_str} ----")

                # --- Clear previous day's data and reset daily state ---
                self.data_fetcher.clear_daily_data()
                self.reset_daily_state()
                # --- End Clearing ---

                self.step_1_check_portfolio_and_scan()
                data_req_ids = self.step_2_prepare_logs() # Get requested IDs

                # --- Wait for data ---
                if data_req_ids:
                    print(f"[INFO] Waiting for {len(data_req_ids)} data requests to complete...")
                    # Use the wait method from TradeExecutionApp
                    data_ready = self.ib_client.wait_for_historical_data(data_req_ids, timeout=45.0) # Increased timeout
                    if data_ready:
                        print("[INFO] All historical data requests completed or timed out.")
                        self.simulate_historical_day(date_str) # Pass date for context
                    else:
                        print("[WARN] Data fetch timed out for some symbols. Proceeding with available data.")
                        # Simulation will run only on symbols that returned data
                        self.simulate_historical_day(date_str)
                else:
                     print("[INFO] No data requests were made. Skipping simulation for the day.")
                # --- End Wait for data ---

            else:
                print(f"[BACKTEST] Skipping weekend: {current_dt.strftime('%Y-%m-%d')}")

            current_dt += timedelta(days=1) # Move to the next day

        self.step_6_end_of_day_summary() # Final summary after the loop


    def run_single_day_backtest(self):
        """Runs backtest simulation for a single day specified in config."""
        date_str = self.config.get("historical", {}).get("start_date")
        if not date_str:
             print("[ERROR] Historical start_date not set in config for single day backtest.")
             return

        try:
            # Validate date format
            _ = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            print("[ERROR] Invalid date format for historical start_date. Use YYYYMMDD.")
            return

        print(f"\n[BACKTEST] ---- Day {date_str} ----")

        # --- Clear previous day's data and reset daily state ---
        self.data_fetcher.clear_daily_data()
        self.reset_daily_state()
        # --- End Clearing ---

        self.step_1_check_portfolio_and_scan()
        data_req_ids = self.step_2_prepare_logs()

        if data_req_ids:
             print(f"[INFO] Waiting for {len(data_req_ids)} data requests to complete...")
             data_ready = self.ib_client.wait_for_historical_data(data_req_ids, timeout=45.0)
             if data_ready:
                 print("[INFO] All historical data requests completed or timed out.")
                 self.simulate_historical_day(date_str)
             else:
                 print("[WARN] Data fetch timed out. Proceeding with available data.")
                 self.simulate_historical_day(date_str)
        else:
             print("[INFO] No data requests made. Skipping simulation.")

        self.step_6_end_of_day_summary()


    def reset_daily_state(self):
        """Resets states that should be cleared at the start of each day."""
        # Called at the start of each new day in backtest range
        self.daily_trading_halted = {rp: False for rp in self.profile_strategies}
        # Reset any other daily counters (e.g., daily trade limits if implemented)
        print("[INFO] Daily trading state reset.")


    def step_1_check_portfolio_and_scan(self):
        """Selects symbols for the day based on existing positions and scanner results."""
        # In this backtest version, assumes starting fresh each day
        # Modify here to carry over positions if needed
        current_holdings = [] # Assume no overnight holdings for simplicity
        print(f"[STEP 1] Current Holdings (Simulated EOD): {current_holdings}")

        max_total = self.config["scanner"]["max_total_symbols"]
        needed_symbols = max_total - len(current_holdings)
        scanned_symbols = []

        if needed_symbols > 0:
            max_new = self.config["scanner"]["max_new_symbols"]
            limit = min(needed_symbols, max_new)
            if limit > 0:
                print(f"[SCANNER] Need {needed_symbols} symbols, scanning for top {limit} new symbols.")
                try:
                    # Scanner now expects limit argument
                    scanned_symbols = self.scanner.run_market_scanner(limit=limit)
                except Exception as e:
                     print(f"[ERROR] Market scanner failed: {e}")
                     traceback.print_exc() # Show details
                     scanned_symbols = [] # Proceed without new symbols
            else:
                 print("[SCANNER] No new symbols needed based on limits.")

        # Combine existing (none in this case) and scanned, ensure unique, limit total
        combined = list(dict.fromkeys(current_holdings + scanned_symbols))
        self.symbols_for_day = combined[: max_total]
        print(f"[STEP 1] Symbols selected for day trading: {self.symbols_for_day}")


    def step_2_prepare_logs(self):
        """Requests necessary historical data for the selected symbols."""
        if not self.symbols_for_day:
             print("[STEP 2] No symbols selected, skipping data fetch.")
             return [] # Return empty list of req_ids

        print("[STEP 2] Requesting data for selected symbols...")
        request_ids = [] # Store request IDs to wait for them later
        needs_15m = any(s.use_15min_trend for s in self.profile_strategies.values())

        for sym in self.symbols_for_day:
            try:
                # Request 1-minute data
                req_1m_id = self.data_fetcher.request_historical_data(sym)
                if req_1m_id: request_ids.append(req_1m_id)
                time.sleep(0.11) # IBKR pacing recommendation: ~50 messages/sec

                # Request 15-minute data only if needed by any strategy
                if needs_15m:
                    req_15m_id = self.data_fetcher.request_historical_data_15min(sym)
                    if req_15m_id: request_ids.append(req_15m_id)
                    time.sleep(0.11) # Pacing

            except Exception as e:
                 print(f"[ERROR] Failed requesting data for {sym}: {e}")
                 traceback.print_exc() # Show details

        print(f"[STEP 2] {len(request_ids)} data requests submitted.")
        return request_ids # Return the list of submitted request IDs


    def display_progress_bar(self, current, total, bar_length=40):
        """Displays a simple progress bar to stderr."""
        if total <= 0: return # Avoid division by zero
        progress = float(current) / float(total)
        # Ensure progress doesn't exceed 1.0 due to float issues
        progress = min(progress, 1.0)
        filled = int(round(bar_length * progress))
        # Ensure filled length doesn't exceed bar_length
        filled = min(filled, bar_length)
        bar_str = "#" * filled + "-" * (bar_length - filled)
        percent_str = f"{progress * 100:.1f}"
        # Use stderr for progress bar to avoid interfering with stdout logging
        # '\r' moves cursor to beginning of line, '\033[K' clears the line (for terminals supporting ANSI escape codes)
        sys.stderr.write(f"\rProgress: [{bar_str}] {percent_str}% \033[K")
        sys.stderr.flush()
        if current >= total: # Print newline when done
            sys.stderr.write("\n")
            sys.stderr.flush()


    def simulate_historical_day(self, date_str):
        """Simulates trading activity bar-by-bar for a single historical day."""

        # --- Refined max_len calculation ---
        symbols_with_data = []
        max_len = 0
        for sym in self.symbols_for_day:
            bars_1m = self.data_fetcher.historical_data_1m.get(sym, [])
            if bars_1m: # Only consider symbols that actually got data
                symbols_with_data.append(sym)
                max_len = max(max_len, len(bars_1m))
            else:
                print(f"[WARN] No 1-minute data found for {sym} on {date_str} after waiting.")

        if max_len == 0 or not symbols_with_data:
            print(f"[WARN] No usable historical 1m bar data found for any selected symbol on {date_str}. Skipping simulation.")
            # Record zero equity change for the day if needed
            for rp_name in self.profile_strategies:
                portfolio = self.backtest_portfolios[rp_name]
                eq_now = self.calculate_backtest_portfolio_value(rp_name) # Should be just cash if no positions
                # Use a placeholder time for the equity point
                placeholder_dt = datetime.strptime(date_str, "%Y%m%d").replace(hour=16)
                portfolio["equity_curve"].append((placeholder_dt, eq_now))
            return
        # --- End refined max_len ---

        print(f"[INFO] Simulating {max_len} bars for the day across {len(symbols_with_data)} symbols...")

        # Initialize daily state (redundant if called from range loop, safe otherwise)
        self.reset_daily_state()
        #start_of_day_equity = {rp: self.calculate_backtest_portfolio_value(rp, 0) for rp in self.profile_strategies} # Pass bar_index 0
        start_of_day_equity = {rp: self.calculate_backtest_portfolio_value(rp, 0) for rp in self.profile_strategies} # Pass bar_index 0
        eod_exit_triggered_today = False # Flag to ensure EOD logic runs only once

        # Market exit time (e.g., 5 minutes before close)
        market_exit_time = dt_time(15, 55, 0)
        eastern = pytz.timezone("US/Eastern")

        # --- Determine Indicator Params Once ---
        indicator_params = {}
        if self.profile_strategies:
            try:
                # Get params from the first profile (assuming they are consistent or not used if strategy disabled)
                # A more robust approach might pass profile-specific params if they differ
                temp_strategy = next(iter(self.profile_strategies.values()))
                indicator_params = {
                    "rsi_period": temp_strategy.rsi_period, "use_rsi": temp_strategy.use_rsi,
                    "use_macd": temp_strategy.use_macd, "use_sma20": temp_strategy.use_sma20,
                    "use_sma50": temp_strategy.use_sma50, "use_vwap": temp_strategy.use_vwap,
                    "use_15min_trend": temp_strategy.use_15min_trend
                }
            except StopIteration:
                print("[ERROR] No strategy profiles found for indicator parameters.")
                indicator_params = {}
        # --- End Indicator Params ---

        last_equity_log_time = None

        for i in range(max_len):
            self.display_progress_bar(i + 1, max_len)
            current_bar_timestamp_str = None # Store timestamp from first valid bar
            current_bar_time_obj = None

            # --- Iterate through SYMBOLS THAT HAVE DATA ---
            for sym in symbols_with_data:
                # --- Get Bars and Indicators ---
                full_bars = self.data_fetcher.historical_data_1m.get(sym, [])
                if len(full_bars) <= i: continue # Skip if this symbol has fewer bars than max_len

                # Use data up to the current bar index 'i'
                partial_bars = full_bars[: i + 1]
                if not partial_bars: continue # Should not happen if max_len > 0

                last_bar = partial_bars[-1]
                time_str, _, _, _, close_price, _ = last_bar

                # Try to parse the timestamp for EOD check and equity curve
                                # Try to parse the timestamp for EOD check and equity curve
                if current_bar_timestamp_str is None: current_bar_timestamp_str = time_str
                try:
                    # --- Explicit Parsing for 'YYYYMMDD HH:MM:SS TZ' format ---
                    # Split the string into datetime part and timezone part
                    parts = time_str.rsplit(' ', 1)
                    if len(parts) == 2:
                        datetime_part, timezone_part = parts
                        # Parse the datetime part using the known format
                        current_dt_naive = datetime.strptime(datetime_part, '%Y%m%d %H:%M:%S')
                        # Get the timezone object
                        tz_object = pytz.timezone(timezone_part)
                        # Localize the naive datetime
                        current_dt_obj = tz_object.localize(current_dt_naive)
                        current_bar_time_obj = current_dt_obj.time()
                    else:
                        # Fallback or raise error if format is unexpected
                        raise ValueError(f"Timestamp format incorrect: '{time_str}'")
                    # --- End Explicit Parsing ---

                except (ValueError, pytz.UnknownTimeZoneError) as e:
                    # Log parsing error ONLY if it's the first symbol failing for this bar index
                    if current_bar_timestamp_str is None or current_bar_time_obj is None:
                        print(f"\n[WARN] Could not parse timestamp '{time_str}' at bar index {i}: {e}")
                    current_dt_obj = None # Ensure obj is None
                    current_bar_time_obj = None # Ensure time is None
                except Exception as e: # Catch other unexpected errors
                     if current_bar_timestamp_str is None or current_bar_time_obj is None:
                          print(f"\n[WARN] Generic error parsing timestamp '{time_str}' at bar index {i}: {e}")
                     current_dt_obj = None
                     current_bar_time_obj = None

                # Calculate indicators using only data up to the current bar
                indicators = None
                if indicator_params:
                    # --- Temporarily replace data, compute, restore ---
                    original_bars_1m = self.data_fetcher.historical_data_1m.get(sym)
                    original_bars_15m = self.data_fetcher.historical_data_15m.get(sym) # Save 15m too if used
                    self.data_fetcher.historical_data_1m[sym] = partial_bars
                    # Slice 15m data relevant to current time if needed (complex)
                    # For simplicity, compute_indicators uses whatever 15m data is present

                    try:
                        indicators = self.data_fetcher.compute_indicators(sym, **indicator_params)
                    except Exception as e:
                         print(f"\n[ERROR] Indicator calculation failed for {sym} at bar {i}: {e}")
                         traceback.print_exc()
                    finally:
                        # Restore original data
                        if original_bars_1m is not None: self.data_fetcher.historical_data_1m[sym] = original_bars_1m
                        else: self.data_fetcher.historical_data_1m.pop(sym, None) # Should not happen
                        if original_bars_15m is not None: self.data_fetcher.historical_data_15m[sym] = original_bars_15m
                        # No else needed for 15m, it might not have existed
                    # --- End temporary replacement ---

                if not indicators:
                    # print(f"[DEBUG] No indicators computed for {sym} at bar {i}") # Optional
                    continue # Skip strategy logic if indicators failed

                # --- Iterate through Risk Profiles ---
                for rp_name, strategy in self.profile_strategies.items():
                    portfolio = self.backtest_portfolios[rp_name]
                    logger = self.trade_loggers[rp_name]
                    risk_profile_config = self.config["risk_profiles"][rp_name]
                    drawdown_config = risk_profile_config.get("drawdown_protection", {})

                    # Check position state
                    pos = portfolio["positions"].get(sym, None)
                    in_position = (pos is not None and isinstance(pos, dict) and pos.get("shares", 0) > 0)
                    cost_basis, shares_held, high_water_mark = None, 0, None
                    if in_position:
                        cost_basis = pos.get("avg_price")
                        shares_held = pos.get("shares", 0)
                        # Update High Water Mark for the position
                        current_hwm = pos.get("high_water_mark", 0.0)
                        pos["high_water_mark"] = max(current_hwm, close_price)
                        high_water_mark = pos["high_water_mark"]

                    # --- Check Drawdown Limits ---
                    current_equity = self.calculate_backtest_portfolio_value(rp_name, i) # Pass index 'i'
                    sod_equity = start_of_day_equity[rp_name]
                    current_daily_drawdown_pct = (max(0, sod_equity - current_equity) / sod_equity * 100.0) if sod_equity > 0 else 0.0

                    # Check and set daily halt flag
                    if (not self.daily_trading_halted[rp_name] and
                        drawdown_config.get("enable_daily_drawdown_limit", False) and
                        current_daily_drawdown_pct >= drawdown_config.get("daily_drawdown_limit_pct", 100.0)):
                            print(f"\n[{rp_name}] DAILY DRAWDOWN LIMIT HIT ({current_daily_drawdown_pct:.2f}% >= {drawdown_config['daily_drawdown_limit_pct']:.1f}%). Halting new BUYs for the day.")
                            self.daily_trading_halted[rp_name] = True

                    # Update total equity high water mark and max drawdown
                    if current_equity > self.max_equity_dict[rp_name]: self.max_equity_dict[rp_name] = current_equity
                    hwm_equity = self.max_equity_dict[rp_name]
                    current_total_drawdown_pct = (max(0, hwm_equity - current_equity) / hwm_equity * 100.0) if hwm_equity > 0 else 0.0
                    self.max_drawdown_dict[rp_name] = max(self.max_drawdown_dict[rp_name], current_total_drawdown_pct)

                    # Check and set total halt flag (persists across days)
                    if (not self.total_trading_halted.get(rp_name, False) and
                        drawdown_config.get("enable_total_drawdown_limit", False) and
                        current_total_drawdown_pct >= drawdown_config.get("total_drawdown_limit_pct", 100.0)):
                            print(f"\n[{rp_name}] TOTAL DRAWDOWN LIMIT HIT ({current_total_drawdown_pct:.2f}% >= {drawdown_config['total_drawdown_limit_pct']:.1f}%). Halting new BUYs permanently (until reset).")
                            self.total_trading_halted[rp_name] = True
                    # --- End Drawdown Checks ---

                    # Determine if new BUY signals should be ignored
                    allow_buy_signal = not self.daily_trading_halted.get(rp_name, False) and not self.total_trading_halted.get(rp_name, False)

                    # --- Compute Signal ---
                    signal, reason, trade_params = None, "Halted", {}
                    if in_position or allow_buy_signal: # Only compute if holding or buys allowed
                        try:
                            signal, reason, trade_params = strategy.compute_signal(
                                in_position=in_position, bars=partial_bars, indicators=indicators,
                                position_state=pos, account_balance=portfolio["cash"],
                                high_water_mark=high_water_mark, # Pass updated HWM
                                current_daily_drawdown_pct=current_daily_drawdown_pct,
                                total_drawdown_pct=current_total_drawdown_pct,
                                market_regime="neutral" # Placeholder for market regime input
                            )
                        except Exception as e:
                            print(f"\n[ERROR] Strategy compute_signal failed for {sym}_{rp_name}: {e}")
                            traceback.print_exc()
                            signal, reason, trade_params = None, f"StrategyError: {e}", {}
                    # --- End Compute Signal ---

                    # --- Execute Simulated Trade ---
                    if signal == "BUY":
                        if allow_buy_signal: # Double check halt status
                            stop_px = trade_params.get("stop_price")
                            shares_to_buy = trade_params.get("shares", 0)
                            if shares_to_buy > 0:
                                # Pass index 'i' to simulate_buy
                                self.simulate_buy(rp_name, sym, partial_bars, indicators, reason, shares_to_buy, stop_px, i)
                        else:
                             # Log ignored buy signal if needed
                             # print(f"[{rp_name}/{sym}] BUY Signal ignored due to trading halt.")
                             pass # Skip BUY if halted

                    elif signal == "SELL" and in_position:
                        shares_to_sell = trade_params.get("shares_to_sell", 0)
                        # Handle partial TP marker where shares_to_sell might be 0
                        is_partial_tp_marker = shares_to_sell == 0 and trade_params.get("partial_tp_level_index") is not None
                        current_shares_before_sell = pos.get("shares", 0) if pos else 0

                        # Proceed if selling actual shares OR just marking a TP level
                        if current_shares_before_sell > 0 and (shares_to_sell >= 0): # Allow 0 shares for TP marker
                            if shares_to_sell > 0 or is_partial_tp_marker:
                                 # Pass index 'i' to simulate_sell
                                 self.simulate_sell(rp_name, sym, partial_bars, indicators, reason, shares_to_sell, trade_params, i)
                        elif shares_to_sell < 0:
                             print(f"\n[WARN] {sym}_{rp_name}: SELL signal negative shares {shares_to_sell}.")

                    # --- Log No Action (Optional) ---
                    # Uncomment if you want to log every single bar even if no trade
                    # else: # NO ACTION or HOLD
                    #     log_rsi = indicators.get("RSI", [50])[-1]
                    #     # ... get other indicator values ...
                    #     logger.log_transaction(
                    #         time_str=time_str, symbol=f"{sym}_{rp_name}", trade_type="NO ACTION", shares=0,
                    #         # ... other params ...
                    #         reason=reason or "Hold/NoCondition", stop_price=None, trailing_stop=None
                    #     )
                    # --- End Log No Action ---
                # --- End Profile Loop ---
            # --- End Symbol Loop ---

            # --- Check for End-of-Day Exit ---
                    # --- Check for End-of-Day Exit ---
        # Check if current time is past exit time AND we haven't triggered EOD logic yet today
        if not eod_exit_triggered_today and current_bar_time_obj is not None and current_bar_time_obj >= market_exit_time:
            # --- Trigger EOD Exit Logic ONCE ---
            print(f"\n[INFO] Market exit time ({market_exit_time.strftime('%H:%M:%S')}) reached at bar {i}. Closing open positions.")
            eod_exit_triggered_today = True # Set the flag so this block doesn't run again today

            # Loop through profiles and their positions to close them
            for rp_name_exit, strategy_exit in self.profile_strategies.items():
                portfolio_exit = self.backtest_portfolios[rp_name_exit]
                symbols_in_portfolio = list(portfolio_exit["positions"].keys()) # Copy keys

                for sym_exit in symbols_in_portfolio:
                    pos_exit = portfolio_exit["positions"].get(sym_exit)
                    if pos_exit and isinstance(pos_exit, dict) and pos_exit.get("shares", 0) > 0:
                        # Get the bars and indicators *for this symbol* at the current index 'i'
                        exit_bars_data = self.data_fetcher.historical_data_1m.get(sym_exit, [])
                        if len(exit_bars_data) > i:
                            partial_exit_bars = exit_bars_data[:i+1]
                            exit_indicators = {} # Recalculate indicators

                            # --- Temp replace, compute, restore ---
                            original_exit_1m = self.data_fetcher.historical_data_1m.get(sym_exit)
                            original_exit_15m = self.data_fetcher.historical_data_15m.get(sym_exit)
                            self.data_fetcher.historical_data_1m[sym_exit] = partial_exit_bars
                            try:
                                if indicator_params: exit_indicators = self.data_fetcher.compute_indicators(sym_exit, **indicator_params)
                            except Exception as e_ind: print(f"\n[WARN] Indicator recalc failed for EOD exit {sym_exit}: {e_ind}")
                            finally:
                                if original_exit_1m is not None: self.data_fetcher.historical_data_1m[sym_exit] = original_exit_1m
                                if original_exit_15m is not None: self.data_fetcher.historical_data_15m[sym_exit] = original_exit_15m
                            # --- End Temp replace ---

                            shares_to_exit = pos_exit["shares"]
                            print(f"[{rp_name_exit}/{sym_exit}] EOD Exit: Selling {shares_to_exit} shares.")
                            self.simulate_sell(
                                rp_name=rp_name_exit, symbol=sym_exit, bars=partial_exit_bars,
                                indicators=exit_indicators or {}, reason="EndOfDayExit",
                                shares_to_sell=shares_to_exit, trade_params={}, bar_index=i
                            )
                        else:
                            print(f"\n[WARN] {rp_name_exit}/{sym_exit}: Cannot EOD exit, missing bar data at index {i}")
            # --- End Trigger EOD Exit Logic ONCE ---

        # --- End EOD Exit Check ---

            # --- Log Equity Curve ---
            # Use the timestamp parsed earlier
            log_time = current_dt_obj if current_bar_time_obj else None
            # Log equity only once per unique timestamp (or maybe every N bars)
            if log_time and (last_equity_log_time is None or log_time > last_equity_log_time):
                 for rp_name_eq in self.profile_strategies.keys():
                      portfolio_eq = self.backtest_portfolios[rp_name_eq]
                      # Pass index 'i' to valuation function
                      eq_now = self.calculate_backtest_portfolio_value(rp_name_eq, i)
                      portfolio_eq["equity_curve"].append((log_time, eq_now))
                 last_equity_log_time = log_time
            # --- End Equity Logging ---

        # Final progress bar update to 100%
        self.display_progress_bar(max_len, max_len)
        print("\n[INFO] Simulation loop completed for the day.")


    def simulate_buy(self, rp_name, symbol, bars, indicators, reason, shares, stop_price, bar_index):
        """Simulates a buy transaction and updates backtest portfolio state."""
        portfolio = self.backtest_portfolios[rp_name]
        logger = self.trade_loggers[rp_name]
        strategy = self.profile_strategies[rp_name]

        if not bars or bar_index >= len(bars):
             print(f"[ERROR] simulate_buy: Invalid bars or bar_index for {symbol}")
             return
        # Use the price from the current bar_index
        last_bar = bars[bar_index]
        time_str, _, _, _, close_price, _ = last_bar
        cost = close_price * shares

        # Check available cash
        if cost > portfolio["cash"]:
            # print(f"[{rp_name}/{symbol}] Insufficient cash for BUY. Need {cost:.2f}, Have {portfolio['cash']:.2f}") # Optional log
            return # Cannot afford trade

        existing_position = portfolio["positions"].get(symbol)

        # Calculate initial risk *before* potentially modifying position dict
        initial_risk_per_share = None
        if stop_price is not None and close_price > stop_price:
            initial_risk_per_share = close_price - stop_price
            if strategy.min_risk_per_share > 0 and initial_risk_per_share < strategy.min_risk_per_share:
                 # Adjust stop slightly lower to meet min risk if needed (or reject trade)
                 stop_price = close_price - strategy.min_risk_per_share
                 initial_risk_per_share = strategy.min_risk_per_share
                 # print(f"[{rp_name}/{symbol}] Adjusted stop to {stop_price:.3f} to meet min risk {strategy.min_risk_per_share:.3f}") # Optional
            elif initial_risk_per_share <= 0: # Should not happen if close > stop
                 print(f"[WARN] {rp_name}/{symbol}: Calculated risk <= 0 ({initial_risk_per_share:.3f}). Setting risk to None.")
                 initial_risk_per_share = None # Mark as invalid risk

        # --- Format for printing ---
        init_risk_str = f"{initial_risk_per_share:.3f}" if initial_risk_per_share is not None else 'N/A'
        stop_price_str = f"{stop_price:.3f}" if stop_price is not None else 'N/A'

        # Handle averaging down or initial entry
        if existing_position and isinstance(existing_position, dict): # Averaging down
            # --- Averaging Down Logic ---
            old_shares = existing_position.get("shares", 0)
            old_avg_price = existing_position.get("avg_price", 0.0)
            old_cost = old_shares * old_avg_price

            new_shares = old_shares + shares
            new_total_cost = old_cost + cost
            new_avg_price = new_total_cost / new_shares if new_shares > 0 else 0

            portfolio["cash"] -= cost
            existing_position["shares"] = new_shares
            existing_position["avg_price"] = new_avg_price
            # Update HWM, but initial stop/risk typically remains from the first entry for R-multiple calcs
            existing_position["high_water_mark"] = max(existing_position.get("high_water_mark", 0.0), close_price)
            # Keep initial_risk_per_share, partial_tp_levels_taken, shares_sold_partial_tp from first entry
            # Optionally add logic to adjust overall stop based on new average price if needed

            print(f"[{rp_name}/{symbol}] Averaged Down: Add {shares} @ {close_price:.2f}. New Pos: {new_shares} @ {new_avg_price:.3f}, HWM: {existing_position['high_water_mark']:.2f}")
            # --- End Averaging Down ---
        else: # Initial Buy
            # --- Initial Buy Logic ---
            portfolio["cash"] -= cost
            portfolio["positions"][symbol] = {
                "shares": shares,
                "avg_price": close_price, # Average price is just the entry price
                "buy_time": time_str,
                "initial_stop": stop_price, # Store the calculated initial stop
                "high_water_mark": close_price, # Initial HWM is entry price
                "initial_risk_per_share": initial_risk_per_share, # Store calculated risk
                "partial_tp_levels_taken": [False] * len(strategy.partial_tp_levels), # Init TP flags
                "shares_sold_partial_tp": 0 # Init shares sold for TP
            }
            print(f"[{rp_name}/{symbol}] Initial Buy: {shares} @ {close_price:.2f}, HWM: {close_price:.2f}, Stop: {stop_price_str}, InitRisk: {init_risk_str}")
            # --- End Initial Buy ---

                # --- Log the Transaction ---
        current_pos_data = portfolio["positions"].get(symbol, {}) # Get updated data
        log_cost_basis = current_pos_data.get("avg_price", close_price) # Use avg price for logging basis
        # Use the risk calculated for *this specific entry* for logging this transaction's risk context
        risk_this_entry = (close_price - stop_price) if stop_price is not None and close_price > stop_price else None

        logger.log_transaction(
            time_str=time_str,
            symbol_profile=f"{symbol}_{rp_name}", # Corrected: symbol_profile
            trade_type="BUY", shares=shares,
            price=close_price, # Corrected: price
            cost_basis=log_cost_basis,
            rsi=indicators.get("RSI", [50])[-1], macd_line=indicators.get("MACD_LINE", [0])[-1],
            macd_signal=indicators.get("MACD_SIGNAL", [0])[-1], vwap=indicators.get("VWAP", [close_price])[-1],
            sma20=indicators.get("SMA_20", [close_price])[-1], sma50=indicators.get("SMA_50", [close_price])[-1],
            trend_15m=indicators.get("15min_trend", "unknown"), atr=indicators.get("ATR_1D", 0.0),
            risk_per_share=risk_this_entry,
            pnl=None, pnl_pct=None,
            cash_balance=portfolio["cash"], # Corrected: cash_balance
            reason=reason,
            stop_price_triggered=stop_price_str if stop_price is not None else None, # Corrected: stop_price_triggered
            trailing_stop_triggered=None # Corrected: trailing_stop_triggered
        )
        # --- End Logging ---


    def simulate_sell(self, rp_name, symbol, bars, indicators, reason, shares_to_sell, trade_params, bar_index):
        """Simulates a sell transaction and updates backtest portfolio state."""
        portfolio = self.backtest_portfolios[rp_name]
        logger = self.trade_loggers[rp_name]

        if not bars or bar_index >= len(bars):
             print(f"[ERROR] simulate_sell: Invalid bars or bar_index for {symbol}")
             return

        last_bar = bars[bar_index]
        time_str, _, _, _, close_price, _ = last_bar
        pos = portfolio["positions"].get(symbol)
        trade_params = trade_params or {} # Ensure trade_params is a dict

        # Check if position exists
        if not pos or not isinstance(pos, dict) or pos.get("shares", 0) <= 0:
             # print(f"[{rp_name}/{symbol}] Sell signal received but no position found.") # Optional log
             return # No position to sell

        current_shares = pos.get("shares", 0)
        purchase_price = pos.get("avg_price", 0.0) # Use average price as cost basis

        # Handle partial TP marker (shares_to_sell == 0) vs actual sell
        partial_tp_level_index = trade_params.get("partial_tp_level_index", None)
        is_partial_tp = partial_tp_level_index is not None
        is_partial_tp_marker_only = is_partial_tp and shares_to_sell == 0

        if is_partial_tp_marker_only:
            # --- Logic just to mark TP level as taken ---
            tp_levels_taken = pos.get("partial_tp_levels_taken")
            if tp_levels_taken is not None and partial_tp_level_index < len(tp_levels_taken):
                 if not tp_levels_taken[partial_tp_level_index]: # Mark only if not already marked
                      tp_levels_taken[partial_tp_level_index] = True
                      # shares_sold_partial_tp is updated only when shares are actually sold
                      print(f"[{rp_name}/{symbol}] Marked Partial TP Level {partial_tp_level_index + 1} as taken (no shares sold this time). Total sold for TP: {pos.get('shares_sold_partial_tp', 0)}")
                 # else: # Optional: log if trying to mark an already taken level
                 #      print(f"[{rp_name}/{symbol}] Partial TP Level {partial_tp_level_index + 1} was already marked.")
            else: print(f"[ERROR] {symbol}_{rp_name}: Invalid partial_tp_level_index {partial_tp_level_index} or state missing for marker.")
            # Do not proceed with sell logic if it's just a marker
            return
            # --- End TP Marker Logic ---

        # --- Actual Sell Logic ---
        if shares_to_sell < 0: return # Cannot sell negative shares
        if shares_to_sell > current_shares:
            # print(f"[{rp_name}/{symbol}] Warning: Attempting to sell {shares_to_sell} but only hold {current_shares}. Selling all.") # Optional
            shares_to_sell = current_shares
        if shares_to_sell == 0: return # Nothing to sell

        proceeds = close_price * shares_to_sell
        portfolio["cash"] += proceeds

        # Calculate PnL for this specific transaction
        trade_pnl = (close_price - purchase_price) * shares_to_sell
        cost_of_shares_sold = purchase_price * shares_to_sell
        pnl_percent = (trade_pnl / cost_of_shares_sold * 100.0) if cost_of_shares_sold != 0 else 0.0

        remaining_shares = current_shares - shares_to_sell

        # Update position state or remove if fully closed
        if remaining_shares <= 0:
            print(f"[{rp_name}/{symbol}] Closed Position: Sold {shares_to_sell} @ {close_price:.2f}. Reason: {reason}. PnL: {trade_pnl:.2f}")
            # Optionally store final trade details before deleting
            # portfolio['trades'].append({...})
            del portfolio["positions"][symbol] # Remove position from portfolio
        else:
            pos["shares"] = remaining_shares
            print(f"[{rp_name}/{symbol}] Partial Sell: Sold {shares_to_sell} @ {close_price:.2f}. Remaining: {remaining_shares}. Reason: {reason}. PnL: {trade_pnl:.2f}")
            # Update shares sold for TP if this was a partial TP sell
            if is_partial_tp:
                 pos["shares_sold_partial_tp"] = pos.get("shares_sold_partial_tp", 0) + shares_to_sell
                 # Mark the level as taken (might be redundant if marker logic used, but safe)
                 tp_levels_taken = pos.get("partial_tp_levels_taken")
                 if tp_levels_taken is not None and partial_tp_level_index < len(tp_levels_taken):
                      if not tp_levels_taken[partial_tp_level_index]:
                          tp_levels_taken[partial_tp_level_index] = True
                          print(f"[{rp_name}/{symbol}] Marked Partial TP Level {partial_tp_level_index + 1} as taken after selling {shares_to_sell}. Total sold for TP: {pos['shares_sold_partial_tp']}")


        # --- Log the Sell Transaction ---
        stop_price_triggered = trade_params.get("stop_price_triggered") # Get potential stop trigger value
        is_trailing_stop_hit = "TrailingStopHit" in reason
        is_fixed_stop_hit = "StopLossHit" in reason
        log_stop_price_val, log_trailing_stop_val = None, None
        if is_trailing_stop_hit and stop_price_triggered is not None:
             log_trailing_stop_val = f"{stop_price_triggered:.3f}"
        elif is_fixed_stop_hit and stop_price_triggered is not None:
             log_stop_price_val = f"{stop_price_triggered:.3f}"

        # Log transaction details
        logger.log_transaction(
            time_str=time_str,
            symbol_profile=f"{symbol}_{rp_name}", # Corrected: symbol_profile
            trade_type="SELL", shares=shares_to_sell,
            price=close_price, # Corrected: price
            cost_basis=purchase_price,
            rsi=indicators.get("RSI", [50])[-1], macd_line=indicators.get("MACD_LINE", [0])[-1],
            macd_signal=indicators.get("MACD_SIGNAL", [0])[-1], vwap=indicators.get("VWAP", [close_price])[-1],
            sma20=indicators.get("SMA_20", [close_price])[-1], sma50=indicators.get("SMA_50", [close_price])[-1],
            trend_15m=indicators.get("15min_trend", "unknown"), atr=indicators.get("ATR_1D", 0.0),
            risk_per_share=pos.get("initial_risk_per_share") if pos else None,
            pnl=trade_pnl, pnl_pct=pnl_percent,
            cash_balance=portfolio["cash"], # Corrected: cash_balance
            reason=reason,
            stop_price_triggered=log_stop_price_val, # Corrected: stop_price_triggered
            trailing_stop_triggered=log_trailing_stop_val # Corrected: trailing_stop_triggered
        )
        # --- End Logging ---


    def step_6_end_of_day_summary(self):
        """Prints a summary of performance at the end of the simulation or day."""
        mode = self.config.get("mode", "live").lower()
        print("\n--- End of Run Summary ---") # Changed title slightly
        if mode == "historical":
            results = []
            total_final_value = 0
            profile_count = 0
            for rp_name in self.profile_strategies:
                profile_count += 1
                portfolio = self.backtest_portfolios[rp_name]
                # Calculate final value based on cash and *final* price of any remaining positions
                # (Should be 0 if EOD exit works)
                final_value = self.calculate_backtest_portfolio_value(rp_name, -1) # Use -1 to signal EOD valuation
                total_final_value += final_value
                pnl = final_value - self.starting_value
                pnl_pct = (pnl / self.starting_value * 100.0) if self.starting_value else 0.0
                dd_str = f"Max drawdown: {self.max_drawdown_dict[rp_name]:.2f}%"
                summary_text = (
                    f"[Profile: {rp_name}]\n"
                    f"  Starting capital: {self.starting_value:.2f}\n"
                    f"  Final portfolio value: {final_value:.2f}\n"
                    f"  Net PnL: {pnl:.2f} ({pnl_pct:.2f}%)\n"
                    f"  {dd_str}"
                    # TODO: Add trade count, win rate etc. by analyzing portfolio['trades']
                )
                results.append(summary_text)

            if profile_count > 0:
                 avg_final_value = total_final_value / profile_count
                 avg_pnl = avg_final_value - self.starting_value
                 avg_pnl_pct = (avg_pnl / self.starting_value * 100.0) if self.starting_value else 0.0
                 print("\n".join(results))
                 print(f"\nAverage Final Value: {avg_final_value:.2f}")
                 print(f"Average Net PnL: {avg_pnl:.2f} ({avg_pnl_pct:.2f}%)")
            else:
                 print("No risk profiles were simulated.")

        else: # Live Mode Summary
            try:
                # Fetch final live values
                final_cash = self.get_portfolio_cash()
                final_net_liq = self.get_portfolio_value()
                print(f"Live Mode EOD:")
                print(f"  Final Cash: {final_cash:.2f}")
                # Calculate live position value (requires fetching prices or using NetLiq)
                # position_value = final_net_liq - final_cash
                # print(f"  Final Position Value: {position_value:.2f}") # Approximate
                print(f"  Final Net Liquidation: {final_net_liq:.2f}")
                # Compare to starting capital if tracked for live mode
                # live_pnl = final_net_liq - self.starting_value_live # Need starting_value_live
                # print(f"  Approx Net PnL: {live_pnl:.2f}")
            except Exception as e:
                print(f"[ERROR] Could not fetch live portfolio value at end of day: {e}")


    def calculate_backtest_portfolio_value(self, rp_name, bar_index):
        """Calculates portfolio value at a specific bar index using that bar's close price."""
        portfolio = self.backtest_portfolios[rp_name]
        total_cash = portfolio["cash"]
        total_positions_value = 0.0

        for sym, pos_data in portfolio["positions"].items():
            shares = pos_data.get("shares", 0)
            if shares > 0:
                # Get the historical data for the symbol
                bars_1m = self.data_fetcher.historical_data_1m.get(sym, [])
                current_close = 0.0

                if bars_1m:
                    if bar_index == -1: # Use last available bar for EOD valuation
                         if bars_1m: current_close = bars_1m[-1][4]
                    elif 0 <= bar_index < len(bars_1m):
                        # Use the close price from the specified bar index
                        current_close = bars_1m[bar_index][4]
                    # else: # Index out of bounds, use average price as fallback (less accurate)
                    #      current_close = pos_data.get("avg_price", 0.0)
                    #      print(f"[WARN] Using avg_price for {sym} value at index {bar_index} (out of bounds)")

                else: # No bars found for symbol, use avg price (less accurate)
                    current_close = pos_data.get("avg_price", 0.0)
                    # print(f"[WARN] Using avg_price for {sym} value at index {bar_index} (no bars)")


                total_positions_value += shares * current_close

        return total_cash + total_positions_value


    # --- Live Mode Methods (Keep structure, needs fleshing out for real execution) ---

    def run_live_workflow(self):
        """Main loop for live trading mode."""
        self.step_1_check_portfolio_and_scan() # Select symbols
        _ = self.step_2_prepare_logs() # Request initial data (req_ids not used here)
        print("[INFO] Waiting for initial data fetch...")
        time.sleep(10) # Simple wait for initial data in live mode
        print("[INFO] Starting live trading loop...")
        self.step_3_buy_sell_modes_loop() # Enter the main live processing loop
        # EOD Summary is called within step_3 loop's finally block or after market close


    def step_3_buy_sell_modes_loop(self):
        """The core loop for live trading during market hours."""
        try:
            market_open_time = dt_time(9, 30, 0)
            market_close_time = dt_time(16, 0, 0) # Standard market close
            exit_signal_time = dt_time(15, 55, 0) # Time to start checking for exit signals
        except Exception as e:
             print(f"[ERROR] Could not define market times: {e}. Using defaults.")
             market_open_time = dt_time(9, 30, 0)
             market_close_time = dt_time(16, 0, 0)
             exit_signal_time = dt_time(15, 55, 0)

        freq_seconds = 60 # Check every minute
        eastern = pytz.timezone("US/Eastern")
        active_profile_name = self.config.get("risk_profile", "moderate") # Live mode uses one profile
        active_strategy = self.profile_strategies.get(active_profile_name)
        active_logger = self.trade_loggers.get(active_profile_name)

        if not active_strategy or not active_logger:
             print(f"[ERROR] Active strategy '{active_profile_name}' or logger not found. Exiting live mode.")
             return

        print(f"[INFO] Live mode active for profile: {active_profile_name}")

        try:
            while True:
                now_et = datetime.now(eastern)
                now_time = now_et.time()

                # Check market hours
                if now_et.weekday() >= 5: # Skip weekends
                     print("[INFO] Weekend. Sleeping until Monday market open...")
                     # Calculate time until next Monday open (complex, simplified sleep)
                     time.sleep(3600 * 12) # Sleep for 12 hours
                     continue
                if now_time < market_open_time or now_time >= market_close_time:
                     print(f"[INFO] Outside market hours ({market_open_time}-{market_close_time} ET). Sleeping...")
                     time.sleep(60 * 15) # Sleep for 15 mins
                     continue

                # --- Main Live Logic ---
                start_loop_time = time.time()

                # Periodically update live positions and cash (e.g., every 5 mins)
                if now_et.minute % 5 == 0 and now_et.second < 10: # Approx start of the 5th minute
                     print("[INFO] Refreshing live positions and cash...")
                     self.init_live_positions()
                     # Fetch cash less often if needed
                     # live_cash = self.get_portfolio_cash()

                # Fetch latest data and indicators for each symbol
                needs_15m = active_strategy.use_15min_trend
                live_indicator_params = {
                    "rsi_period": active_strategy.rsi_period, "use_rsi": active_strategy.use_rsi,
                    "use_macd": active_strategy.use_macd, "use_sma20": active_strategy.use_sma20,
                    "use_sma50": active_strategy.use_sma50, "use_vwap": active_strategy.use_vwap,
                    "use_15min_trend": active_strategy.use_15min_trend
                }

                for symbol in self.symbols_for_day:
                    # --- Fetch Live/Recent Data ---
                    # Use reqHistoricalData to get the most recent full day as an approximation
                    # A true live system would use reqMktData for real-time ticks/bars
                    print(f"[DEBUG] Requesting recent data for {symbol}...")
                    self.data_fetcher.request_historical_data(symbol)
                    time.sleep(0.2) # Pacing + wait
                    if needs_15m:
                         self.data_fetcher.request_historical_data_15min(symbol)
                         time.sleep(0.2)

                    bars = self.data_fetcher.historical_data_1m.get(symbol, [])
                    if not bars:
                         print(f"[WARN] No recent 1m data fetched for {symbol}. Skipping.")
                         continue

                    # --- Calculate Indicators ---
                    # Use temporary data replacement method for indicators
                    original_bars_live = self.data_fetcher.historical_data_1m.get(symbol)
                    original_15m_live = self.data_fetcher.historical_data_15m.get(symbol)
                    self.data_fetcher.historical_data_1m[symbol] = bars # Use fetched bars
                    indicators = self.data_fetcher.compute_indicators(symbol, **live_indicator_params)
                    # Restore original data immediately after computation
                    if original_bars_live: self.data_fetcher.historical_data_1m[symbol] = original_bars_live
                    if original_15m_live: self.data_fetcher.historical_data_15m[symbol] = original_15m_live

                    if not indicators:
                         print(f"[WARN] Failed to compute indicators for {symbol}. Skipping.")
                         continue

                    # --- Get Live Position and Compute Signal ---
                    pos_state = self.real_portfolio.get(symbol, None)
                    in_position = pos_state is not None and pos_state.get("shares", 0) > 0

                    # Fetch live cash value (can be slow, consider caching/periodic update)
                    current_cash = self.get_portfolio_cash()

                    # Compute signal using the single active strategy
                    signal, reason, trade_params = active_strategy.compute_signal(
                        in_position=in_position, bars=bars, indicators=indicators,
                        position_state=pos_state,
                        account_balance=current_cash,
                        # Live HWM/Drawdown tracking would need persistent state
                        high_water_mark=pos_state.get("high_water_mark") if pos_state else None, # Example
                        current_daily_drawdown_pct=0.0, # Placeholder - requires tracking
                        total_drawdown_pct=0.0, # Placeholder - requires tracking
                        market_regime="neutral" # Placeholder
                    )

                    # --- Execute Live Trades ---
                    if signal == "BUY" and not in_position:
                        shares_to_buy = trade_params.get("shares", 0)
                        if shares_to_buy > 0:
                            stop_px = trade_params.get("stop_price")
                            # Pass logger instance
                            self.execute_buy(symbol, bars, indicators, reason, shares_to_buy, stop_px, active_logger)
                            time.sleep(0.5) # Small pause after placing order

                    elif signal == "SELL" and in_position:
                        # Default to selling all shares if not specified
                        shares_to_sell = trade_params.get("shares_to_sell", pos_state.get("shares", 0))
                        if shares_to_sell > 0:
                            # Pass logger instance and trade_params
                            self.execute_sell(symbol, bars, indicators, reason, shares_to_sell, active_logger, trade_params)
                            time.sleep(0.5) # Small pause after placing order

                    # --- Check for EOD Exit Signal ---
                    if now_time >= exit_signal_time and in_position:
                        print(f"[{active_profile_name}/{symbol}] EOD Exit Time reached. Selling remaining {pos_state['shares']} shares.")
                        self.execute_sell(symbol, bars, indicators, "EndOfDayExit", pos_state['shares'], active_logger, {})
                        time.sleep(0.5)

                # --- End Symbol Loop ---

                # Calculate time elapsed and sleep until next interval
                end_loop_time = time.time()
                elapsed = end_loop_time - start_loop_time
                sleep_time = max(0, freq_seconds - elapsed)
                print(f"[INFO] Live loop iteration took {elapsed:.2f}s. Sleeping for {sleep_time:.2f}s...")
                time.sleep(sleep_time)
                # --- End Main Live Logic ---

        except KeyboardInterrupt:
            print("\n[LIVE] Ctrl+C caught, stopping live trading loop.")
        except Exception as e:
             print(f"[ERROR] Unhandled exception in live loop: {e}")
             traceback.print_exc()
        finally:
             # Ensure EOD summary runs when loop terminates
             print("[INFO] Live trading loop finished.")
             self.step_6_end_of_day_summary()


    # Keep execute_buy, execute_sell, init_live_positions, get_portfolio_value, get_portfolio_cash, get_current_portfolio_symbols, calculate_market_close_datetime
    # mostly the same as in the previous version, ensure they use the active logger correctly.

    def execute_buy(self, symbol, bars, indicators, reason, shares, stop_price, logger):
        """Places a live BUY order and logs it."""
        # Ensure logger is valid
        if not logger:
             print("[ERROR] execute_buy: Logger not provided.")
             return

        last_bar = bars[-1] # Use the most recent bar data available
        time_str, _, _, _, last_close, _ = last_bar
        print(f"[LIVE EXECUTE] Attempting BUY {shares} {symbol} @ approx {last_close:.2f}. Reason: {reason}")

        try:
            # --- Place Actual Order ---
            order_id = self.ib_client.place_market_order(symbol, "BUY", shares)

            if order_id: # Check if order placement was successful (returned an ID)
                 print(f"[LIVE EXECUTE] BUY Order ID {order_id} placed for {symbol}.")
                 # --- Update Internal Live Portfolio State (Optimistic) ---
                 # NOTE: Assumes immediate fill at last_close. Real fill needed via orderStatus.
                 pos = self.real_portfolio.get(symbol)
                 if not pos:
                      self.real_portfolio[symbol] = {
                          "shares": shares, "avg_price": last_close,
                          "initial_stop": stop_price,
                          "high_water_mark": last_close, # Initial HWM
                          # Add other state needed by strategy if any
                      }
                 else: # Averaging down in live mode (if strategy allows)
                      old_shares = pos.get("shares", 0)
                      old_price = pos.get("avg_price", 0.0)
                      new_shares = old_shares + shares
                      new_avg = ((old_shares * old_price) + (shares * last_close)) / new_shares if new_shares > 0 else last_close
                      pos["shares"] = new_shares
                      pos["avg_price"] = new_avg
                      pos["high_water_mark"] = max(pos.get("high_water_mark", 0.0), last_close)

                 # Log optimistic execution immediately
                 log_cost_basis = self.real_portfolio[symbol]["avg_price"]
                 risk_this_entry = (last_close - stop_price) if stop_price is not None else None
                 logger.log_transaction(
                     time_str=datetime.now(pytz.timezone("US/Eastern")).strftime("%Y%m%d %H:%M:%S"), # Use current time for live log
                     symbol=symbol, # Log just the symbol for live
                     trade_type="BUY", shares=shares, close_price=last_close,
                     cost_basis=log_cost_basis,
                     rsi=indicators.get("RSI", [50])[-1], macd_line=indicators.get("MACD_LINE", [0])[-1], macd_signal=indicators.get("MACD_SIGNAL", [0])[-1],
                     vwap=indicators.get("VWAP", [last_close])[-1], sma20=indicators.get("SMA_20", [last_close])[-1], sma50=indicators.get("SMA_50", [last_close])[-1],
                     trend_15m=indicators.get("15min_trend", "unknown"), atr=indicators.get("ATR_1D", 0.0),
                     risk_per_share=risk_this_entry, pnl=None, pnl_pct=None,
                     running_balance=self.get_portfolio_cash(), # Fetch potentially slightly delayed cash
                     reason=reason,
                     stop_price=f"{stop_price:.3f}" if stop_price is not None else None,
                     trailing_stop=None
                 )
            else:
                 print(f"[ERROR] Failed to place BUY order for {symbol} (No Order ID returned).")

        except Exception as e:
            print(f"[ERROR] Exception during execute BUY order for {symbol}: {e}")
            traceback.print_exc()


    def execute_sell(self, symbol, bars, indicators, reason, shares_to_sell, logger, trade_params=None):
        """Places a live SELL order and logs it."""
        if not logger:
             print("[ERROR] execute_sell: Logger not provided.")
             return

        last_bar = bars[-1]
        time_str, _, _, _, last_close, _ = last_bar
        pos = self.real_portfolio.get(symbol)

        if not pos or pos.get("shares", 0) <= 0:
             print(f"[WARN] execute_sell called for {symbol} but no position found in internal state.")
             return

        current_shares = pos.get("shares", 0)
        if shares_to_sell > current_shares: shares_to_sell = current_shares
        if shares_to_sell <= 0: return # Nothing to sell

        cost_basis = pos.get("avg_price", 0.0)
        print(f"[LIVE EXECUTE] Attempting SELL {shares_to_sell} {symbol} @ approx {last_close:.2f}. Reason: {reason}")

        try:
            # --- Place Actual Order ---
            order_id = self.ib_client.place_market_order(symbol, "SELL", shares_to_sell)

            if order_id:
                 print(f"[LIVE EXECUTE] SELL Order ID {order_id} placed for {symbol}.")
                 # --- Update Internal Live Portfolio State (Optimistic) ---
                 remaining_shares = current_shares - shares_to_sell
                 if remaining_shares <= 0:
                      print(f"[INFO] Position {symbol} closed in internal state.")
                      del self.real_portfolio[symbol]
                 else:
                      pos["shares"] = remaining_shares
                      print(f"[INFO] Position {symbol} reduced to {remaining_shares} shares in internal state.")

                 # Log optimistic execution
                 trade_pnl = (last_close - cost_basis) * shares_to_sell
                 cost_of_pos = cost_basis * shares_to_sell
                 pnl_percent = (trade_pnl / cost_of_pos * 100.0) if cost_of_pos else 0.0

                 # Determine stop type for logging
                 stop_price_triggered = trade_params.get("stop_price_triggered") if trade_params else None
                 is_trailing_stop_hit = "TrailingStopHit" in reason
                 is_fixed_stop_hit = "StopLossHit" in reason
                 log_stop_price_val, log_trailing_stop_val = None, None
                 if is_trailing_stop_hit and stop_price_triggered is not None: log_trailing_stop_val = f"{stop_price_triggered:.3f}"
                 elif is_fixed_stop_hit and stop_price_triggered is not None: log_stop_price_val = f"{stop_price_triggered:.3f}"

                 logger.log_transaction(
                     time_str=datetime.now(pytz.timezone("US/Eastern")).strftime("%Y%m%d %H:%M:%S"),
                     symbol=symbol, trade_type="SELL", shares=shares_to_sell,
                     close_price=last_close, cost_basis=cost_basis,
                     rsi=indicators.get("RSI", [50])[-1], macd_line=indicators.get("MACD_LINE", [0])[-1], macd_signal=indicators.get("MACD_SIGNAL", [0])[-1],
                     vwap=indicators.get("VWAP", [last_close])[-1], sma20=indicators.get("SMA_20", [last_close])[-1], sma50=indicators.get("SMA_50", [last_close])[-1],
                     trend_15m=indicators.get("15min_trend", "unknown"), atr=indicators.get("ATR_1D", 0.0),
                     risk_per_share=pos.get("initial_risk_per_share") if pos else None, # From original entry
                     pnl=trade_pnl, pnl_pct=pnl_percent,
                     running_balance=self.get_portfolio_cash(),
                     reason=reason,
                     stop_price=log_stop_price_val, trailing_stop=log_trailing_stop_val
                 )
            else:
                 print(f"[ERROR] Failed to place SELL order for {symbol} (No Order ID returned).")

        except Exception as e:
             print(f"[ERROR] Exception during execute SELL order for {symbol}: {e}")
             traceback.print_exc()


    def init_live_positions(self):
        """Fetches current positions from IBKR and updates internal state."""
        print("[INFO] Fetching live positions from IBKR...")
        try:
            # Fetch positions (returns dict like {'AAPL': {'shares': 100, 'avg_cost': 150.0}, ...})
            positions_from_ibkr = self.ib_client.fetch_positions()

            # Create a new portfolio state based on fetched data
            updated_portfolio = {}
            for sym, data in positions_from_ibkr.items():
                 shares = data.get('shares', 0)
                 avg_cost = data.get('avg_cost', 0.0)
                 if shares != 0: # Only include actual positions
                      # Check if we have existing state for this symbol to preserve HWM etc.
                      existing_state = self.real_portfolio.get(sym)
                      updated_portfolio[sym] = {
                          "shares": int(shares),
                          "avg_price": float(avg_cost),
                          # Carry over other state if it exists, otherwise initialize
                          "initial_stop": existing_state.get("initial_stop") if existing_state else None,
                          "high_water_mark": existing_state.get("high_water_mark", float(avg_cost)) if existing_state else float(avg_cost),
                          # Add other fields as needed
                      }

            # Atomically update the portfolio state
            self.real_portfolio = updated_portfolio
            print(f"[INFO] Updated live portfolio state. Holdings: {list(self.real_portfolio.keys())}")

        except Exception as e:
            print(f"[ERROR] Failed to fetch or initialize live positions: {e}")
            traceback.print_exc()


    def get_portfolio_value(self):
        """Fetches Net Liquidation value from IBKR."""
        try:
            acct_data = self.ib_client.fetch_account_summary("NetLiquidation")
            net_liq = acct_data.get("NetLiquidation", 0.0)
            # print(f"[DEBUG] Fetched Net Liq: {net_liq}") # Optional debug
            return float(net_liq) # Ensure float
        except Exception as e:
            print(f"[ERROR] Failed to fetch NetLiquidation: {e}")
            return 0.0 # Return default/error value


    def get_portfolio_cash(self):
        """Fetches Total Cash Value from IBKR."""
        try:
            acct_data = self.ib_client.fetch_account_summary("TotalCashValue")
            cash = acct_data.get("TotalCashValue", 0.0)
            # print(f"[DEBUG] Fetched Cash: {cash}") # Optional debug
            return float(cash) # Ensure float
        except Exception as e:
            print(f"[ERROR] Failed to fetch TotalCashValue: {e}")
            return 0.0


    def get_current_portfolio_symbols(self):
        """Returns symbols currently held (for live mode)."""
        # For backtesting, this remains empty assuming no overnight holds
        # For live mode, it should reflect actual holdings
        mode = self.config.get("mode", "live").lower()
        if mode == "live":
             return list(self.real_portfolio.keys())
        else: # Backtest mode
             return []


    def calculate_market_close_datetime(self):
        """Calculates the market close datetime for today in US/Eastern."""
        eastern = pytz.timezone("US/Eastern")
        now_et = datetime.now(eastern)
        # Create datetime object for 4 PM ET today
        # Use localize to make it timezone-aware
        close_dt = eastern.localize(datetime(now_et.year, now_et.month, now_et.day, 16, 0, 0))
        return close_dt

