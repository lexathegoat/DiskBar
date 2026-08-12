import argparse

from src.system_monitor.ui import SmartMonitorApp


def main():
    parser = argparse.ArgumentParser(description="Smart System Monitor")
    parser.add_argument("--headless", action="store_true", help="Run without opening the GUI window")
    parser.add_argument("--demo", action="store_true", help="Run a quick demo read without the UI")
    args = parser.parse_args()

    if args.headless or args.demo:
        app = SmartMonitorApp(headless=True)
        data = app.monitor.read()
        print(f"CPU {data.cpu_usage}% | GPU {data.gpu_usage}% | RAM {data.ram_used:.1f}/{data.ram_total:.1f} GB | SSD {data.disk_health}%")
        return

    app = SmartMonitorApp()
    app.run()


if __name__ == "__main__":
    main()
