from src.system_monitor.hardware import HardwareMonitor, SensorData


def test_health_summary_reports_problem_state():
    monitor = HardwareMonitor()
    data = SensorData()
    data.cpu_temp = 92
    data.gpu_temp = 88
    data.ram_used = 28
    data.ram_total = 32
    data.disk_health = 81
    data.disk_free = 7
    data.cpu_usage = 96
    data.gpu_usage = 97
    data.alerts = ["CPU temperature reached critical levels"]
    summary = monitor.get_status_summary(data)

    assert summary["state"] == "critical"
    assert summary["score"] <= 100
    assert "critical" in summary["summary_text"].lower()
    assert "cpu" in summary["summary_text"].lower()


def test_health_summary_reports_healthy_state():
    monitor = HardwareMonitor()
    data = SensorData()
    data.cpu_temp = 45
    data.gpu_temp = 52
    data.ram_used = 10
    data.ram_total = 32
    data.disk_health = 97
    data.disk_free = 42
    data.cpu_usage = 32
    data.gpu_usage = 40
    data.alerts = []
    summary = monitor.get_status_summary(data)

    assert summary["state"] == "good"
    assert summary["score"] >= 80
    assert "stable" in summary["summary_text"].lower()
