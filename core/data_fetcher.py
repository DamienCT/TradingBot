#**1. `data_fetcher.py` (Added `clear_daily_data` method)**

import pytz
from datetime import datetime
import pandas as pd
from ibapi.contract import Contract
from ibapi.common import BarData
import math

class DataFetcher:
    def __init__(self, ib_client, config):
        self.ib_client = ib_client
        self.config = config
        self.mode = self.config.get("mode", "live").lower()
        # Initialize data storage
        self.historical_data_1m = {}
        self.historical_data_15m = {}

    # --- NEW METHOD ---
    def clear_daily_data(self):
        """Clears the stored historical data dictionaries."""
        print("[DEBUG] Clearing daily historical data dictionaries.")
        self.historical_data_1m.clear()
        self.historical_data_15m.clear()
    # --- END NEW METHOD ---

    def create_contract(self, symbol: str) -> Contract:
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract

    def request_historical_data(self, symbol: str):
        req_id = self.ib_client.get_next_req_id()
        # Ensure the list exists for the symbol before requesting
        if symbol not in self.historical_data_1m:
             self.historical_data_1m[symbol] = []
        # No need to clear here, clear_daily_data handles it per day

        self.ib_client.register_historical_data_callback(req_id, self.on_historical_data_1m, symbol)
        contract = self.create_contract(symbol)

        if self.mode == "historical":
            # Ensure historical date is available
            sim_date_str = self.config.get("historical", {}).get("start_date")
            if not sim_date_str:
                print(f"[ERROR] Historical start_date not found in config for {symbol}. Cannot request data.")
                return None # Return None or raise error

            end_time_str = f"{sim_date_str} 16:00:00 US/Eastern"
            duration = "1 D"
            bar_size_setting = self.config["historical"].get("data_frequency", "1 min")
            print(f"[REQUEST] Historical data (1m) for {symbol} from {end_time_str}, barSize={bar_size_setting}")
            self.ib_client.reqHistoricalData(
                reqId=req_id, contract=contract, endDateTime=end_time_str,
                durationStr=duration, barSizeSetting=bar_size_setting,
                whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[]
            )
            return req_id # Return req_id for tracking
        else:
            eastern = pytz.timezone("US/Eastern")
            now_eastern = datetime.now(eastern)
            end_time_str = now_eastern.strftime("%Y%m%d %H:%M:%S US/Eastern")
            duration = "1 D"
            bar_size_setting = "1 min"
            print(f"[REQUEST] Live historical data (1m) for {symbol} ending {end_time_str}")
            self.ib_client.reqHistoricalData(
                reqId=req_id, contract=contract, endDateTime=end_time_str,
                durationStr=duration, barSizeSetting=bar_size_setting,
                whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[]
            )
            return req_id # Return req_id for tracking

    def request_historical_data_15min(self, symbol: str):
        req_id = self.ib_client.get_next_req_id()
        # Ensure the list exists for the symbol before requesting
        if symbol not in self.historical_data_15m:
            self.historical_data_15m[symbol] = []
        # No need to clear here, clear_daily_data handles it per day

        self.ib_client.register_historical_data_callback(req_id, self.on_historical_data_15m, symbol)
        contract = self.create_contract(symbol)

        if self.mode == "historical":
            # Ensure historical date is available
            sim_date_str = self.config.get("historical", {}).get("start_date")
            if not sim_date_str:
                print(f"[ERROR] Historical start_date not found in config for {symbol}. Cannot request 15m data.")
                return None

            end_time_str = f"{sim_date_str} 16:00:00 US/Eastern"
            duration = "5 D" # Keep 5D to ensure enough data for trend SMA
            bar_size_setting = "15 mins"
            print(f"[REQUEST] 15-min data for {symbol} from {end_time_str}, duration={duration}")
            self.ib_client.reqHistoricalData(
                reqId=req_id, contract=contract, endDateTime=end_time_str,
                durationStr=duration, barSizeSetting=bar_size_setting,
                whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[]
            )
            return req_id
        else:
            eastern = pytz.timezone("US/Eastern")
            now_eastern = datetime.now(eastern)
            end_time_str = now_eastern.strftime("%Y%m%d %H:%M:%S US/Eastern")
            duration = "5 D"
            bar_size_setting = "15 mins"
            print(f"[REQUEST] 15-min data (live) for {symbol} ending {end_time_str}")
            self.ib_client.reqHistoricalData(
                reqId=req_id, contract=contract, endDateTime=end_time_str,
                durationStr=duration, barSizeSetting=bar_size_setting,
                whatToShow="TRADES", useRTH=1, formatDate=1, keepUpToDate=False, chartOptions=[]
            )
            return req_id

    def on_historical_data_1m(self, symbol: str, bar: BarData):
        # Add check to ensure symbol key exists before appending
        if symbol in self.historical_data_1m:
            # Basic validation (optional but good practice)
            try:
                if bar.date.startswith("finished"): return # Already handled finish state
                _ = float(bar.open) # Try converting key fields
                _ = float(bar.close)
                _ = float(bar.volume)
                self.historical_data_1m[symbol].append((
                    bar.date, float(bar.open), float(bar.high),
                    float(bar.low), float(bar.close), float(bar.volume)
                ))
            except ValueError:
                 print(f"[WARN] Invalid data format in 1m bar for {symbol}: {bar}. Skipping bar.")
            except Exception as e:
                 print(f"[ERROR] Unexpected error processing 1m bar for {symbol}: {e}. Skipping bar.")
        else:
             print(f"[WARN] Received 1m data for {symbol} but no list was initialized. Discarding.")


    def on_historical_data_15m(self, symbol: str, bar: BarData):
        # Add check to ensure symbol key exists before appending
        if symbol in self.historical_data_15m:
             try:
                if bar.date.startswith("finished"): return
                _ = float(bar.open)
                _ = float(bar.close)
                _ = float(bar.volume)
                self.historical_data_15m[symbol].append((
                    bar.date, float(bar.open), float(bar.high),
                    float(bar.low), float(bar.close), float(bar.volume)
                ))
             except ValueError:
                  print(f"[WARN] Invalid data format in 15m bar for {symbol}: {bar}. Skipping bar.")
             except Exception as e:
                  print(f"[ERROR] Unexpected error processing 15m bar for {symbol}: {e}. Skipping bar.")
        else:
             print(f"[WARN] Received 15m data for {symbol} but no list was initialized. Discarding.")


    def compute_indicators( self, symbol: str, rsi_period=14, use_rsi=True, use_macd=True,
                            use_sma20=True, use_sma50=True, use_vwap=True, use_15min_trend=True ):
        # Check if data exists for the symbol THIS time compute is called
        bars_1m = self.historical_data_1m.get(symbol, [])
        if not bars_1m:
             # print(f"[DEBUG] No 1m bars found for {symbol} when computing indicators.") # Optional debug
             return None # Return None if no data

        # --- Rest of the function remains the same ---
        closes_1m = [b[4] for b in bars_1m]
        output = {}

        if use_rsi:
            rsi_list = self.calculate_rsi(closes_1m, window=rsi_period)
        else:
            rsi_list = [50] * len(closes_1m)
        output["RSI"] = rsi_list

        if use_macd:
            macd_line, macd_signal = self.calculate_macd(closes_1m, fast=12, slow=26, signal=9)
        else:
            macd_line = [0]*len(closes_1m)
            macd_signal = [0]*len(closes_1m)
        output["MACD_LINE"] = macd_line
        output["MACD_SIGNAL"] = macd_signal

        if use_sma20:
            sma_20 = self.calculate_sma(closes_1m, window=20)
        else:
            sma_20 = [0]*len(closes_1m)
        output["SMA_20"] = sma_20

        if use_sma50:
            sma_50 = self.calculate_sma(closes_1m, window=50)
        else:
            sma_50 = [0]*len(closes_1m)
        output["SMA_50"] = sma_50

        if use_vwap:
            vwap_list = self.compute_vwap(bars_1m)
        else:
            vwap_list = list(closes_1m) # Use list copy
        output["VWAP"] = vwap_list

        if use_15min_trend:
            # Use .get() safely for 15m data as well
            bars_15m = self.historical_data_15m.get(symbol, [])
            trend_15m = self.determine_15min_trend(bars_15m)
        else:
            trend_15m = "unknown"
        output["15min_trend"] = trend_15m

        atr_1d = self.compute_atr_approx(bars_1m, window=14)
        output["ATR_1D"] = atr_1d

        return output

    def calculate_rsi(self, data, window=14):
        if len(data) < window: return [50] * len(data)
        series = pd.Series(data)
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)

        # Use exponential moving average for RSI calculation (more standard)
        avg_gain = up.ewm(com=window - 1, adjust=False).mean()
        avg_loss = down.ewm(com=window - 1, adjust=False).mean()

        # Avoid division by zero or near-zero
        avg_loss_safe = avg_loss.replace(0, 1e-9)
        rs = avg_gain / avg_loss_safe

        rsi = 100 - (100 / (1 + rs))
        # Fill initial NaNs (common at start) with 50, ensure list output
        return rsi.fillna(50).tolist()

    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        if not data or len(data) < slow: # Need enough data for slow EMA
             return [0] * len(data), [0] * len(data) # Return zero lists if not enough data
        series = pd.Series(data)
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line.fillna(0).tolist(), macd_signal.fillna(0).tolist()

    def calculate_sma(self, data, window=20):
        if not data: return [] # Handle empty list
        series = pd.Series(data, dtype=float)
        # Use min_periods=1 to get SMA even at the beginning
        sma_series = series.rolling(window=window, min_periods=1).mean()

        # Fill NaNs using the new methods: bfill() then fillna(0)
        # Apply bfill() first to fill NaNs from the end, then fill remaining NaNs (at the start if window > len) with 0
        filled_sma = sma_series.bfill().fillna(0)

        return filled_sma.tolist()


    def compute_vwap(self, bars):
        if not bars: return []
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        # Ensure numeric types, coerce errors to NaN, then handle NaNs
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce') # Needed for ATR fallback
        df['low'] = pd.to_numeric(df['low'], errors='coerce') # Needed for ATR fallback

        # Handle potential NaNs robustly BEFORE calculations
        # Forward fill first, then backward fill for any remaining at the start
        df[['close', 'high', 'low']] = df[['close', 'high', 'low']].ffill().bfill()
        # Fill volume NaNs with 0 and ensure non-negative
        df['volume'] = df['volume'].fillna(0).clip(lower=0)

        # Calculate price * volume, handling potential 0 volume
        df['price_volume'] = df['close'] * df['volume']
        df['cumulative_pv'] = df['price_volume'].cumsum()
        df['cumulative_volume'] = df['volume'].cumsum()

        # Calculate VWAP, replace 0 cumulative volume denominator with NaN temporarily
        cumulative_volume_safe = df['cumulative_volume'].replace(0, pd.NA)
        df['vwap'] = df['cumulative_pv'] / cumulative_volume_safe

        # Fill NaNs in VWAP (from 0 volume or initial bars) using the corresponding close price
        # Ensure indices align for the fillna operation - should be fine as they are from same df
        df['vwap'] = df['vwap'].fillna(df['close'])

        # Final check for any remaining non-finite values (inf, -inf) - replace with close
        df['vwap'] = df['vwap'].replace([float('inf'), -float('inf')], pd.NA).fillna(df['close'])

        return df['vwap'].tolist()


    def determine_15min_trend(self, bars_15m):
        sma_period = 20
        if len(bars_15m) < sma_period: return "unknown"

        closes_15m = [b[4] for b in bars_15m]
        sma_15m = self.calculate_sma(closes_15m, window=sma_period)
        if not sma_15m or len(sma_15m) != len(closes_15m): # Check length match
             print("[WARN] SMA calculation for 15m trend failed or returned unexpected length.")
             return "unknown"

        last_close = closes_15m[-1]
        last_sma = sma_15m[-1]

        if pd.isna(last_sma) or pd.isna(last_close): return "unknown"

        # Add a small tolerance to avoid flipping on exact equality
        tolerance = 1e-6
        if last_close > last_sma + tolerance: return "bullish"
        elif last_close < last_sma - tolerance: return "bearish"
        else: return "neutral" # Changed from unknown for equality


    def compute_atr_approx(self, bars_1m, window=14):
        # Requires 'high', 'low', 'close' columns correctly calculated in compute_vwap (or here)
        if len(bars_1m) < 2: return 1e-6 # Need at least 2 bars for prev close shift

        # Assume bars_1m is list of tuples, create DataFrame
        df = pd.DataFrame(bars_1m, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        # --- Ensure numeric types and handle NaNs (redundant if called after compute_vwap) ---
        for col in ['high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[['high', 'low', 'close']] = df[['high', 'low', 'close']].ffill().bfill()
        # --- End Ensure numeric ---

        df['high_low'] = df['high'] - df['low']
        df['high_prev_close'] = abs(df['high'] - df['close'].shift(1))
        df['low_prev_close'] = abs(df['low'] - df['close'].shift(1))

        # Calculate True Range, fill the first NaN resulting from shift(1)
        df['true_range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)
        # Use H-L for the very first bar's TR where previous close is NaN
        df['true_range'] = df['true_range'].fillna(df['high_low'])

        # --- Robust ATR calculation using EWM ---
        # Use adjust=False for standard Wilder's smoothing often used for ATR
        # Ensure enough data for the window
        if len(df) < window:
             # If not enough data, calculate mean of available TR, ensure > 0
             mean_tr = df['true_range'].mean()
             return max(float(mean_tr), 1e-6) if pd.notna(mean_tr) else 1e-6

        # Calculate ATR using Exponential Moving Average (similar to Wilder's smoothing)
        # com (center of mass) = window - 1 for standard EWM mapping
        atr = df['true_range'].ewm(com=window - 1, adjust=False, min_periods=window).mean().iloc[-1]

        # Fallback if ATR is still NaN or zero/negative (shouldn't happen with above checks)
        if pd.isna(atr) or atr <= 1e-6:
            # Use simple mean of last 'window' TRs as fallback
            mean_tr_last_window = df['true_range'].iloc[-window:].mean()
            return max(float(mean_tr_last_window), 1e-6) if pd.notna(mean_tr_last_window) else 1e-6
        # --- End Robust ATR ---

        return max(float(atr), 1e-6) # Ensure positive return