import math

class MultiIndicatorStrategy:
    def __init__(self, config, profile_name=None):
        self.config = config
        if profile_name is not None:
            self.risk_profile_name = profile_name
        else:
            self.risk_profile_name = config.get("risk_profile", "moderate")

        profiles_dict = config.get("risk_profiles", {})
        if self.risk_profile_name not in profiles_dict:
            raise ValueError(f"No risk profile named {self.risk_profile_name} in config['risk_profiles']!")

        rp = profiles_dict[self.risk_profile_name]

        indicator_switches      = rp.get("indicator_switches", {})
        self.rsi_period         = rp.get("rsi_period", 14)
        self.use_rsi            = indicator_switches.get("use_rsi", True)
        self.use_macd           = indicator_switches.get("use_macd", True)
        self.use_sma20          = indicator_switches.get("use_sma20", True)
        self.use_sma50          = indicator_switches.get("use_sma50", False) # Default False based on config
        self.use_vwap           = indicator_switches.get("use_vwap", True)
        self.use_15min_trend    = indicator_switches.get("use_15min_trend", True)

        self.rsi_overbought       = rp.get("rsi_overbought", 70)
        self.rsi_oversold         = rp.get("rsi_oversold", 30)
        self.macd_confirmation    = rp.get("macd_confirmation", False)

        self.stop_loss_pct        = rp.get("stop_loss_pct", 0.95)
        self.use_atr_stop         = rp.get("use_atr_stop", True)
        self.atr_stop_multiplier  = rp.get("atr_stop_multiplier", 1.0)
        self.atr_multiplier       = rp.get("atr_multiplier", 2.0)

        self.take_profit_base     = rp.get("take_profit_base", 1.03)
        self.take_profit_bump     = rp.get("take_profit_bump", 0.05)
        self.fast_move_threshold  = rp.get("fast_move_threshold", 0.01)

        self.min_risk_per_share   = rp.get("min_risk_per_share", 0.0)
        self.max_shares_per_trade = rp.get("max_shares_per_trade", None)
        self.max_position_value   = rp.get("max_position_value", None)

        self.risk_per_trade       = rp.get("risk_per_trade", 0.02)

        self.enable_trailing_stop = rp.get("enable_trailing_stop", True)
        self.trailing_multiplier  = rp.get("trailing_multiplier", 1.5)

        self.partial_take_profit  = rp.get("partial_take_profit", True)
        self.partial_tp_levels    = rp.get("partial_tp_levels", [])

        avg_down_config = rp.get("averaging_down", {})
        self.enable_averaging_down   = avg_down_config.get("enable", False)
        self.max_avg_down_entries  = avg_down_config.get("max_entries", 0)
        self.avg_down_rsi_offset   = avg_down_config.get("rsi_offset", 5.0)
        self.avg_down_risk_fraction = avg_down_config.get("risk_fraction", 0.5)

        self.avg_down_count = 0

    def compute_signal( self, in_position, bars, indicators, position_state=None,
                        account_balance=10000.0, high_water_mark=None,
                        current_daily_drawdown_pct=0.0, total_drawdown_pct=0.0,
                        market_regime="neutral" ):
        if not bars or not indicators:
            return (None, "NoData", {})

        last_bar = bars[-1]
        time_stamp, _, _, _, close_price, _ = last_bar

        cost_basis = None
        shares_held = 0
        initial_risk_per_share = None
        partial_tp_levels_taken = []
        shares_sold_partial_tp = 0
        initial_stop_price_trade = None

        if in_position and position_state and isinstance(position_state, dict):
            cost_basis = position_state.get("avg_price")
            shares_held = position_state.get("shares", 0)
            initial_stop_price_trade = position_state.get("initial_stop")
            initial_risk_per_share = position_state.get("initial_risk_per_share")
            partial_tp_levels_taken = position_state.get("partial_tp_levels_taken", [False]*len(self.partial_tp_levels))
            shares_sold_partial_tp = position_state.get("shares_sold_partial_tp", 0)
            if high_water_mark is None:
                high_water_mark = position_state.get("high_water_mark")
            if shares_held <= 0 or cost_basis is None:
                in_position = False

        rsi_list    = indicators.get("RSI", [])
        macd_line   = indicators.get("MACD_LINE", [])
        macd_signal = indicators.get("MACD_SIGNAL", [])
        vwap_list   = indicators.get("VWAP", [])
        trend_15m   = indicators.get("15min_trend", "unknown")
        atr_1d      = indicators.get("ATR_1D", 1e-6)

        if not rsi_list or not macd_line or not macd_signal or not vwap_list:
            return (None, "MissingIndicators", {})

        last_rsi    = rsi_list[-1] if rsi_list else 50.0
        last_macd   = macd_line[-1] if macd_line else 0.0
        last_signal = macd_signal[-1] if macd_signal else 0.0
        last_vwap   = vwap_list[-1] if vwap_list else close_price
        if atr_1d <= 1e-6: atr_1d = 1e-6

        effective_stop_mult = self.atr_stop_multiplier
        stop_price_if_buy = 0.0
        risk_per_share_if_buy = 0.0
        if self.use_atr_stop:
            stop_price_if_buy = close_price - (effective_stop_mult * atr_1d)
        else:
            stop_price_if_buy = close_price * self.stop_loss_pct

        risk_per_share_if_buy = close_price - stop_price_if_buy
        if risk_per_share_if_buy < self.min_risk_per_share:
            risk_per_share_if_buy = self.min_risk_per_share
        if risk_per_share_if_buy <= 0:
            risk_per_share_if_buy = max(0.01, close_price * (1.0 - self.stop_loss_pct))

        # Market Regime Filter Placeholder
        # if not in_position and market_regime == "bear":
        #     return (None, "MarketRegimeBear", {})

        if not in_position:
            if self.use_15min_trend and trend_15m == "bearish":
                return (None, "15minTrendBearish", {})
            if self.use_macd and self.macd_confirmation and last_macd <= last_signal:
                return (None, "MACDNotBullish", {})
            if self.use_vwap and close_price <= last_vwap:
                return (None, "PriceBelowOrAtVWAP", {})
            if self.use_rsi and last_rsi > self.rsi_oversold:
                return (None, f"RSI>Oversold({last_rsi:.2f}>{self.rsi_oversold})", {})

            if risk_per_share_if_buy <= 0:
                return (None, "InvalidRiskCalc", {})

            budget_for_trade = account_balance * self.risk_per_trade
            shares_to_buy = int(budget_for_trade / risk_per_share_if_buy)

            if self.max_shares_per_trade is not None:
                shares_to_buy = min(shares_to_buy, self.max_shares_per_trade)
            approx_value = close_price * shares_to_buy
            if self.max_position_value is not None and approx_value > self.max_position_value:
                shares_to_buy = int(self.max_position_value / close_price)
            if shares_to_buy <= 0:
                return (None, "SharesToBuy=0", {})

            self.avg_down_count = 0

            reason = f"Buy Init: RSI({last_rsi:.2f})<=OS({self.rsi_oversold}), 15mOK, >VWAP"
            trade_params = {"shares": shares_to_buy, "stop_price": stop_price_if_buy}
            return ("BUY", reason, trade_params)

        if in_position:
            if (self.enable_averaging_down and
                self.avg_down_count < self.max_avg_down_entries and
                close_price < cost_basis and
                self.use_rsi and last_rsi < (self.rsi_oversold - self.avg_down_rsi_offset)):

                if risk_per_share_if_buy <= 0:
                    return (None, "AvgDownInvalidRisk", {})

                addon_budget = account_balance * self.risk_per_trade * self.avg_down_risk_fraction
                additional_shares = int(addon_budget / risk_per_share_if_buy)

                total_shares_if_add = shares_held + additional_shares
                if self.max_shares_per_trade is not None and total_shares_if_add > self.max_shares_per_trade:
                    additional_shares = max(0, self.max_shares_per_trade - shares_held)

                total_value_if_add = (shares_held * cost_basis) + (additional_shares * close_price)
                if self.max_position_value is not None and total_value_if_add > self.max_position_value:
                    remaining_value_allowance = self.max_position_value - (shares_held * cost_basis)
                    additional_shares_by_value = int(remaining_value_allowance / close_price) if remaining_value_allowance > 0 else 0
                    additional_shares = min(additional_shares, additional_shares_by_value)


                if additional_shares > 0:
                    self.avg_down_count += 1
                    reason = f"AvgDown({self.avg_down_count}): RSI({last_rsi:.2f})<<OS({self.rsi_oversold})"
                    trade_params = {"shares": additional_shares, "stop_price": stop_price_if_buy}
                    return ("BUY", reason, trade_params)
                else:
                    return (None, "AvgDownShares=0", {})

            effective_stop_price = 0.0
            stop_reason = "StopLossHit"
            initial_calc_stop = 0.0

            if self.use_atr_stop:
                if initial_stop_price_trade is not None:
                    initial_calc_stop = initial_stop_price_trade
                else:
                    initial_calc_stop = cost_basis - (effective_stop_mult * atr_1d)
            else:
                initial_calc_stop = cost_basis * self.stop_loss_pct

            effective_stop_price = initial_calc_stop

            if self.enable_trailing_stop and high_water_mark is not None and high_water_mark > cost_basis:
                trailing_stop_atr_amount = self.trailing_multiplier * atr_1d
                calculated_trailing_stop = high_water_mark - trailing_stop_atr_amount
                if calculated_trailing_stop > effective_stop_price:
                    effective_stop_price = calculated_trailing_stop
                    stop_reason = "TrailingStopHit"

            if effective_stop_price < 0: effective_stop_price = 0.0

            stop_condition_met = (close_price <= effective_stop_price)
            if stop_condition_met:
                trade_params = {"shares_to_sell": shares_held, "stop_price_triggered": effective_stop_price}
                return ("SELL", f"{stop_reason}({effective_stop_price:.3f})", trade_params)

            if self.partial_take_profit and initial_risk_per_share is not None and initial_risk_per_share > 0:
                initial_shares = shares_held + shares_sold_partial_tp
                if initial_shares <= 0: initial_shares = shares_held

                for idx, level in enumerate(self.partial_tp_levels):
                    if idx < len(partial_tp_levels_taken) and not partial_tp_levels_taken[idx]:
                        target_multiple = level.get("multiple_of_risk", 0)
                        sell_fraction = level.get("sell_fraction", 0)

                        if target_multiple > 0 and sell_fraction > 0:
                            target_price = cost_basis + (target_multiple * initial_risk_per_share)
                            if close_price >= target_price:
                                shares_for_this_level = math.floor(initial_shares * sell_fraction)
                                shares_to_actually_sell = min(shares_for_this_level, shares_held)

                                if shares_to_actually_sell >= 0:
                                    reason = f"PartialTP {idx+1} ({target_multiple:.1f}R @{target_price:.3f})"
                                    trade_params = { "shares_to_sell": shares_to_actually_sell, "partial_tp_level_index": idx }
                                    return ("SELL", reason, trade_params)

            if self.use_rsi and last_rsi >= self.rsi_overbought:
                return ("SELL", f"RSIOverbought({last_rsi:.2f}>={self.rsi_overbought})", {"shares_to_sell": shares_held})

            if self.use_15min_trend and trend_15m == "bearish":
                if not (self.use_rsi and last_rsi < self.rsi_oversold):
                    return ("SELL", "TrendTurnedBearish", {"shares_to_sell": shares_held})

            return (None, "Hold", {})

        return (None, "NoSignal", {})