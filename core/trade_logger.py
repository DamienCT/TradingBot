#**4. `trade_logger.py` (Minor adjustment for clarity)**

import os
import csv
import sys
from datetime import datetime

# --- PrintLogger Class (Keep as is) ---
class PrintLogger:
    # ... (no changes needed here) ...
    def __init__(self, file_handle):
        self.original_stdout = sys.stdout
        self.file_handle = file_handle
        sys.stdout = self # Redirect stdout

    def write(self, text):
        # Write to original stdout (console)
        if self.original_stdout is not None:
            try:
                self.original_stdout.write(text)
            except Exception as e:
                # Handle cases where original stdout might be closed (rare)
                # print(f"Error writing to original stdout: {e}", file=sys.__stderr__) # Use stderr
                pass # Avoid error propagation

        # Write to the log file
        if self.file_handle is not None and not self.file_handle.closed:
            try:
                self.file_handle.write(text)
            except Exception as e:
                # Log error writing to file, maybe revert stdout
                print(f"Error writing to log file handle: {e}", file=sys.__stderr__)
                self.close() # Attempt to clean up redirection on error

    def flush(self):
        if self.original_stdout is not None:
            try:
                self.original_stdout.flush()
            except Exception:
                pass
        if self.file_handle is not None and not self.file_handle.closed:
            try:
                self.file_handle.flush()
            except Exception:
                pass

    def close(self):
        # Ensure we restore stdout only once and correctly
        if sys.stdout is self: # Check if we are the current stdout
            sys.stdout = self.original_stdout # Restore original
        self.original_stdout = None # Prevent further use

        # Close the file handle if it's open
        if self.file_handle and not self.file_handle.closed:
            try:
                self.file_handle.close()
            except Exception as e:
                 print(f"Error closing log file handle: {e}", file=sys.__stderr__)
        self.file_handle = None # Mark as closed

# --- TradeLogger Class ---
class TradeLogger:
    def __init__(self, config):
        self.config = config
        self.csv_writer = None
        self.csv_file = None
        self.csv_filename = None
        self.print_logger = None # Handles stdout redirection
        self.full_log_file = None # File handle for the full text log
        self.profile_name = "default" # Profile name for potential log separation
        self._is_initialized = False # Flag to prevent multiple initializations

    def set_profile_name(self, name):
        self.profile_name = name

    def init_csv_logger(self):
        """Initializes both CSV and full text loggers."""
        if self._is_initialized:
             # print(f"[DEBUG] Logger for profile {self.profile_name} already initialized.") # Optional
             return # Avoid re-initialization

        paths_cfg = self.config.get("paths", {})
        trans_folder = paths_cfg.get("transactions_folder", "./logs/transactions")
        full_folder = paths_cfg.get("full_folder", "./logs/full")

        # Create directories if they don't exist
        try:
            os.makedirs(trans_folder, exist_ok=True)
            os.makedirs(full_folder, exist_ok=True)
        except OSError as e:
             print(f"[ERROR] Failed to create log directories: {e}")
             # Decide how to handle this - maybe exit or log to current dir?
             trans_folder = "."
             full_folder = "."

        today_str = datetime.now().strftime("%Y-%m-%d") # Use standard date format
        # Include profile name in log filenames for clarity when running multiple profiles
        filename_suffix = f"_{self.profile_name}" # Always add profile name

        # --- CSV Logger Setup ---
        self.csv_filename = os.path.join(trans_folder, f"transactions_{today_str}{filename_suffix}.csv")
        file_exists = os.path.isfile(self.csv_filename)
        try:
            # Open in append mode ('a+') creates if not exists, allows reading (though not used here)
            # newline='' prevents extra blank rows in CSV
            self.csv_file = open(self.csv_filename, mode="a+", newline="", encoding="utf-8")
            self.csv_writer = csv.writer(self.csv_file)

            # Write header only if the file is newly created or empty
            if not file_exists or self.csv_file.tell() == 0: # Check position for emptiness
                header = [
                    "timestamp", "symbol_profile", "trade_type", "shares", "price",
                    "avg_cost_basis", "rsi", "macd_line", "macd_signal", "vwap",
                    "sma20", "sma50", "trend_15m", "atr", "risk_per_share",
                    "pnl", "pnl_pct", "cash_balance", "reason",
                    "stop_price_triggered", "trailing_stop_triggered" # More specific column names
                ]
                self.csv_writer.writerow(header)
                self.csv_file.flush() # Ensure header is written immediately
            print(f"[INFO] CSV logger initialized for {self.profile_name}. File: {self.csv_filename}")
        except IOError as e:
             print(f"[ERROR] Failed to open or write header to CSV '{self.csv_filename}': {e}")
             self.csv_file = None
             self.csv_writer = None # Ensure writer is None if file failed

        # --- Full Text Log Setup (Redirect stdout) ---
        full_log_filename = os.path.join(full_folder, f"full_log_{today_str}{filename_suffix}.txt")
        try:
            # Open full log in append mode
            self.full_log_file = open(full_log_filename, mode="a", encoding="utf-8")
            # Redirect stdout *only if* not already redirected by another logger instance
            # This assumes a shared stdout resource. If truly separate logs per profile
            # are needed, redirection needs careful management. For now, assume one active redirection.
            if self.print_logger is None and sys.stdout is sys.__stdout__: # Check if stdout is original
                 self.print_logger = PrintLogger(self.full_log_file)
                 print(f"[INFO] Full text logger initialized. Output redirected to: {full_log_filename}")
            elif self.print_logger: # If already exists, ensure file handle is updated (e.g., after close/reinit)
                 self.print_logger.file_handle = self.full_log_file
                 print(f"[INFO] Updated file handle for existing PrintLogger: {full_log_filename}")
            else:
                 print("[WARN] Stdout appears to be already redirected. Full log might not capture all output.")
                 # Still try to write directly if needed, but redirection won't work as expected

        except IOError as e:
             print(f"[ERROR] Failed to open full log file '{full_log_filename}': {e}")
             self.full_log_file = None
             # Do not redirect stdout if file failed to open

        self._is_initialized = True # Mark as initialized


    def close_csv_logger(self):
        """Closes log file handles."""
        if not self._is_initialized:
             return # Nothing to close if not initialized

        print(f"[INFO] Closing logger for profile: {self.profile_name}")

        # Close stdout redirection first (restores original stdout)
        # Only the instance that created PrintLogger should close it ideally.
        # However, shared state makes this tricky. Let's assume closing is safe.
        if self.print_logger:
            # Check if the print_logger's handle matches this instance's handle
            # to avoid closing a file potentially used by another logger instance
            # (This check is imperfect if filenames are the same but handles differ)
            # A better approach might involve a central log manager.
            # For simplicity now, assume closing is okay.
            try:
                 # self.print_logger.close() # This restores stdout
                 # print(f"[DEBUG] PrintLogger closed by {self.profile_name}") # Log which profile closed it
                 # Set to None to indicate it's closed for this instance
                 # self.print_logger = None # Problem: This affects other instances if shared
                 # ===> Simpler approach: Just close the file handle directly <===
                 if self.full_log_file and not self.full_log_file.closed:
                     self.full_log_file.close()
                     # print(f"[DEBUG] Full log file closed by {self.profile_name}")
                 self.full_log_file = None

            except Exception as e:
                 print(f"[ERROR] Exception closing print logger/full log file for {self.profile_name}: {e}")


        # Close the CSV file
        if self.csv_file and not self.csv_file.closed:
            try:
                self.csv_file.close()
                # Use original stdout now if redirection was closed
                print(f"[LOGGER] CSV file closed for {self.profile_name}: {self.csv_filename}")
            except Exception as e:
                 print(f"[ERROR] Exception closing CSV file for {self.profile_name}: {e}", file=sys.__stderr__)
        self.csv_file = None
        self.csv_writer = None

        self._is_initialized = False # Mark as closed/uninitialized


    def log_transaction(
        self, time_str, symbol_profile, trade_type, shares, price, cost_basis, # Renamed price/cost_basis
        rsi, macd_line, macd_signal, vwap, sma20, sma50, trend_15m, atr,
        risk_per_share=None, pnl=None, pnl_pct=None, cash_balance=0.0, # Renamed running_balance
        reason="", stop_price_triggered=None, trailing_stop_triggered=None ): # Renamed stop columns

        # Check if logger is ready
        if self.csv_writer is None or self.csv_file is None or self.csv_file.closed:
            print(f"[WARN] CSV Logger not ready for {self.profile_name}. Attempting re-init...")
            self.init_csv_logger() # Try to initialize if not ready
            if self.csv_writer is None: # Check again after trying init
                print(f"[ERROR] Failed to initialize CSV Logger for {self.profile_name}. Cannot log transaction.")
                return # Stop if still not working

        # --- Prepare data for CSV row ---
        # Use consistent formatting, handle None values gracefully
        display_price = f"{float(price):.4f}" if price is not None else ""
        display_cost_basis = f"{float(cost_basis):.4f}" if cost_basis is not None else ""
        display_rsi = f"{float(rsi):.2f}" if rsi is not None else ""
        display_macd_line = f"{float(macd_line):.4f}" if macd_line is not None else ""
        display_macd_signal = f"{float(macd_signal):.4f}" if macd_signal is not None else ""
        display_vwap = f"{float(vwap):.4f}" if vwap is not None else ""
        display_sma20 = f"{float(sma20):.4f}" if sma20 is not None else ""
        display_sma50 = f"{float(sma50):.4f}" if sma50 is not None else ""
        display_trend = str(trend_15m) if trend_15m is not None else "unknown"
        display_atr = f"{float(atr):.4f}" if atr is not None else ""
        display_risk_per_share = f"{float(risk_per_share):.4f}" if risk_per_share is not None else ""
        display_pnl = f"{float(pnl):.3f}" if pnl is not None else ""
        display_pnl_pct = f"{float(pnl_pct):.3f}" if pnl_pct is not None else ""
        display_cash = f"{float(cash_balance):.2f}" if cash_balance is not None else ""
        display_stop_trig = str(stop_price_triggered) if stop_price_triggered is not None else ""
        display_trail_trig = str(trailing_stop_triggered) if trailing_stop_triggered is not None else ""
        # --- End Prepare data ---

        row = [
            time_str, symbol_profile, trade_type.upper(), shares, display_price,
            display_cost_basis, display_rsi, display_macd_line, display_macd_signal, display_vwap,
            display_sma20, display_sma50, display_trend, display_atr,
            display_risk_per_share, display_pnl, display_pnl_pct,
            display_cash, reason, display_stop_trig, display_trail_trig
        ]

        try:
            self.csv_writer.writerow(row)
            # Flush occasionally, not necessarily every row for performance
            # self.csv_file.flush() # Consider flushing less often if performance is critical
        except Exception as e:
            print(f"[ERROR] Failed to write row to CSV log for {self.profile_name}: {e}")
            # Maybe attempt to close/reopen the file?
            try:
                 self.close_csv_logger()
                 self.init_csv_logger()
            except Exception as reinit_e:
                 print(f"[ERROR] Failed to re-initialize logger after write error: {reinit_e}")


    # --- Placeholder methods (keep as is) ---
    def create_symbol_log(self, symbol, is_existing):
        pass

    def log_symbol_news(self, symbol, headlines, sentiment):
        pass

    def create_trade_file(self, symbol, side, ranking_score, sentiment_score):
        pass

    def finalize_trade_file(self, symbol, reason):
        pass

    def compile_daily_logs(self):
        return "Daily logs summary..."