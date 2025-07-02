from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue # <--- Import TagValue
import time
import threading # <--- Import threading

class Scanner:
    def __init__(self, config, ib_client):
        self.config = config
        self.ib_client = ib_client
        # Removed req_id_base, use main counter

    def run_market_scanner(self, limit):
        settings = self.config["scanner"]["settings"]
        sub = ScannerSubscription()
        sub.scanCode = settings.get("scanCode", "TOP_PERC_GAIN")
        sub.instrument = settings.get("instrument", "STK")
        sub.locationCode = settings.get("locationCode", "STK.US")
        # sub.scanSubscriptionFilterOptions = [] # Not needed, pass list directly

        # --- Convert filters to TagValue list ---
        tag_value_list = []
        if "abovePrice" in settings: tag_value_list.append(TagValue("priceAbove", str(settings["abovePrice"])))
        if "belowPrice" in settings: tag_value_list.append(TagValue("priceBelow", str(settings["belowPrice"])))
        if "aboveVolume" in settings: tag_value_list.append(TagValue("volumeAbove", str(settings["aboveVolume"])))
        # Add other filters similarly, ensuring values are strings
        # if "marketCapAbove" in settings: tag_value_list.append(TagValue("marketCapAbove", str(settings["marketCapAbove"])))
        # if "avgVolumeAbove" in settings: tag_value_list.append(TagValue("avgVolumeAbove", str(settings["avgVolumeAbove"])))
        # --- End conversion ---

        req_id = self.ib_client.get_next_req_id()

        found_symbols = []
        scan_complete_event = threading.Event()

        def on_data(rank, contractDetails, distance, benchmark, projection, legsStr):
            sym = contractDetails.contract.symbol
            if contractDetails.contract.secType == 'STK':
                 found_symbols.append(sym)

        def on_done():
            scan_complete_event.set()

        self.ib_client.register_scanner_data_callback(req_id, on_data, on_done)

        print(f"[SCANNER] Starting scan {sub.scanCode}, instrument={sub.instrument}, location={sub.locationCode}, filters={[(tv.tag, tv.value) for tv in tag_value_list]}") # Log readable filters

        # --- Pass tag_value_list correctly ---
        # 4th arg is scannerSubscriptionOptionList (list of TagValue)
        # 5th arg is scannerSubscriptionFilterOptions (list of TagValue)
        self.ib_client.reqScannerSubscription(req_id, sub, [], tag_value_list)
        # --- End correct call ---

        scan_completed = scan_complete_event.wait(timeout=10)

        self.ib_client.cancelScannerSubscription(req_id)

        if not scan_completed:
             print("[WARN] Scanner request timed out.")

        unique_symbols = list(dict.fromkeys(found_symbols))

        print(f"[SCANNER] Found {len(unique_symbols)} unique symbols. Returning top {limit}.")
        return unique_symbols[:limit]