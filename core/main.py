import json
import os
import threading
import time
import sys

from core.trade_execution import TradeExecutionApp
from core.data_fetcher import DataFetcher
from core.workflow_manager import WorkflowManager

def load_config(relative_config_path="config/config.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path_from_root = os.path.join(project_root, relative_config_path)

    if os.path.exists(config_path_from_root):
        print(f"[INFO] Loading config from: {config_path_from_root}")
        config_path_to_load = config_path_from_root
    else:
        print(f"[WARN] Config not found at default location: {config_path_from_root}")
        print(f"[INFO] Trying path as provided: {relative_config_path}")
        if os.path.exists(relative_config_path):
            config_path_to_load = relative_config_path
        else:
             print(f"[ERROR] Config file not found at '{config_path_from_root}' or '{relative_config_path}'")
             sys.exit(1)

    try:
        with open(config_path_to_load, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load or parse config file '{config_path_to_load}': {e}")
        sys.exit(1)

def main():
    config = load_config()
    if not config: return

    ib_client = TradeExecutionApp(config)
    ib_client.connect_to_ib()

    api_thread = threading.Thread(target=ib_client.run_loop, daemon=True)
    api_thread.start()

    print("[MAIN] Waiting for IBKR connection to be ready...")
    connection_established = ib_client.connection_ready_event.wait(timeout=15)

    if not connection_established:
        print("[ERROR] IBKR connection timed out (15 seconds). Please check TWS/Gateway connection and clientId.")
        try:
            ib_client.disconnect()
            api_thread.join(timeout=2)
        except Exception as e:
            print(f"[WARN] Error during disconnection attempt: {e}")
        sys.exit(1)

    print("[MAIN] IBKR Connection established.")

    fetcher = DataFetcher(ib_client, config)
    wf_manager = WorkflowManager(config, ib_client, fetcher)

    wf_manager.run_daily_workflow()

    mode = config.get("mode", "live").lower()

    if mode == "historical":
        print("[MAIN] Backtest completed. Closing logs and exiting.")
        ib_client.disconnect()
        api_thread.join(timeout=5)
        wf_manager.finalize()
        print("[MAIN] Script finished.")
        return
    else:
        try:
            print("[MAIN] Live mode started. Press Ctrl+C to exit.")
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n[MAIN] Ctrl+C caught, exiting live mode.")
        finally:
            print("[MAIN] Disconnecting IBKR and closing logs...")
            ib_client.disconnect()
            api_thread.join(timeout=5)
            wf_manager.finalize()
            print("[MAIN] Logs closed. Safe to open CSV.")
            print("[MAIN] Script finished.")

if __name__ == "__main__":
    main()