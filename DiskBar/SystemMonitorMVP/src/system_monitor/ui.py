import tkinter as tk

from .config import DEFAULT_LANGUAGE, STRINGS
from .hardware import HardwareMonitor


class SmartMonitorApp:
    THEMES = {
        "midnight": {"bg": "#0f172a", "panel": "#111827", "accent": "#7dd3fc", "text": "#e2e8f0"},
        "aurora": {"bg": "#071b1f", "panel": "#0f2e33", "accent": "#34d399", "text": "#d1fae5"},
        "sunset": {"bg": "#1f1222", "panel": "#2a1d2b", "accent": "#fbbf24", "text": "#fef3c7"},
    }

    def __init__(self, headless=False):
        self.language = DEFAULT_LANGUAGE
        self.monitor = HardwareMonitor()
        self.headless = headless
        self.theme = "midnight"
        self.root = None
        self.overlay_root = None
        self.history_window = None
        self.taskbar_widget = None
        self.last_data = None

        if not headless:
            self.root = tk.Tk()
            self.root.title("Smart System Monitor MVP")
            self.root.geometry("980x620")
            self.root.configure(bg="#0f172a")
            self.root.minsize(900, 560)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self._build_ui()

    def on_close(self):
        if self.overlay_root is not None and self.overlay_root.winfo_exists():
            self.overlay_root.destroy()
        if self.history_window is not None and self.history_window.winfo_exists():
            self.history_window.destroy()
        if self.taskbar_widget is not None and self.taskbar_widget.winfo_exists():
            self.taskbar_widget.destroy()
        self.root.destroy()

    def _t(self, key: str) -> str:
        return STRINGS.get(self.language, STRINGS[DEFAULT_LANGUAGE]).get(key, key)

    def _status_for_temp(self, temp: float) -> str:
        if temp < 60:
            return self._t("normal")
        if temp < 75:
            return self._t("high")
        return self._t("critical")

    def _mini_bar(self, value: float, width: int = 18):
        value = max(0.0, min(100.0, value))
        filled = int(value / 100 * width)
        return "█" * filled + "░" * (width - filled)

    def _apply_theme(self):
        if self.root is None:
            return
        theme = self.THEMES.get(self.theme, self.THEMES["midnight"])
        self.root.configure(bg=theme["bg"])

    def _status_pill(self, parent, text, color):
        label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg="#03111f",
            padx=8,
            pady=2,
            bd=0,
            relief="flat",
        )
        label.pack(anchor="w")
        return label

    def _build_card(self, parent, title, accent, value_text, status_text, usage_percent):
        card = tk.Frame(parent, bg="#111827", padx=12, pady=12, highlightbackground=accent, highlightthickness=1)
        card.pack(side="left", fill="y", expand=True, padx=8, pady=8)

        header = tk.Frame(card, bg="#111827")
        header.pack(fill="x")
        tk.Label(header, text=title, font=("Segoe UI", 11, "bold"), bg="#111827", fg="#e2e8f0").pack(side="left")
        self._status_pill(header, status_text, accent).pack(side="right")

        tk.Label(card, text=value_text, font=("Segoe UI", 18, "bold"), bg="#111827", fg=accent).pack(anchor="w", pady=(10, 4))
        tk.Label(card, text=self._mini_bar(usage_percent), font=("Consolas", 11), bg="#111827", fg=accent).pack(anchor="w")
        tk.Label(card, text=f"{usage_percent:.0f}%", font=("Segoe UI", 9), bg="#111827", fg="#cbd5e1").pack(anchor="w", pady=(4, 0))
        return card

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        top = tk.Frame(self.root, bg="#0f172a", padx=16, pady=12)
        top.grid(row=0, column=0, sticky="ew")

        title = tk.Label(top, text=self._t("title"), font=("Segoe UI", 20, "bold"), bg="#0f172a", fg="#e2e8f0")
        title.pack(side="left")

        buttons = tk.Frame(top, bg="#0f172a")
        buttons.pack(side="right")

        for lang_code, label in (("tr", "TR"), ("en", "EN")):
            btn = tk.Button(
                buttons,
                text=label,
                bg="#1e293b",
                fg="white",
                bd=0,
                relief="flat",
                padx=10,
                pady=4,
                command=lambda code=lang_code: self.set_language(code),
            )
            btn.pack(side="left", padx=4)

        for theme_name, label in (("midnight", "Dark"), ("aurora", "Aurora"), ("sunset", "Sunset")):
            btn = tk.Button(
                buttons,
                text=label,
                bg="#334155",
                fg="white",
                bd=0,
                relief="flat",
                padx=8,
                pady=4,
                command=lambda name=theme_name: self.set_theme(name),
            )
            btn.pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="Mini Taskbar",
            bg="#0ea5e9",
            fg="white",
            bd=0,
            relief="flat",
            padx=12,
            pady=5,
            command=self.toggle_taskbar,
        ).pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="Gaming Overlay",
            bg="#1d4ed8",
            fg="white",
            bd=0,
            relief="flat",
            padx=12,
            pady=5,
            command=self.toggle_overlay,
        ).pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="History",
            bg="#0f766e",
            fg="white",
            bd=0,
            relief="flat",
            padx=12,
            pady=5,
            command=self.show_history,
        ).pack(side="left", padx=4)

        body = tk.Frame(self.root, bg="#0f172a")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        self.metric_frame = tk.Frame(body, bg="#0f172a")
        self.metric_frame.pack(fill="x")

        self.cpu_card = self._build_card(self.metric_frame, self._t("cpu"), "#6ee7b7", "", self._t("normal"), 0)
        self.gpu_card = self._build_card(self.metric_frame, self._t("gpu"), "#fbbf24", "", self._t("normal"), 0)
        self.ram_card = self._build_card(self.metric_frame, self._t("ram"), "#60a5fa", "", self._t("normal"), 0)
        self.disk_card = self._build_card(self.metric_frame, self._t("ssd"), "#a78bfa", "", self._t("normal"), 0)
        self.health_card = self._build_card(self.metric_frame, self._t("health"), "#34d399", "", self._t("normal"), 0)

        self.summary_frame = tk.Frame(body, bg="#111827", padx=14, pady=14)
        self.summary_frame.pack(fill="x", pady=(14, 0))

        self.summary_label = tk.Label(
            self.summary_frame,
            text="",
            font=("Segoe UI", 12),
            bg="#111827",
            fg="#dbeafe",
            justify="left",
            anchor="w",
        )
        self.summary_label.pack(fill="x")

        self.alert_label = tk.Label(
            self.summary_frame,
            text="",
            font=("Segoe UI", 11),
            bg="#111827",
            fg="#fbbf24",
            justify="left",
            anchor="w",
        )
        self.alert_label.pack(fill="x", pady=(6, 0))

        self.status_line = tk.Label(
            self.summary_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#111827",
            fg="#a7f3d0",
            justify="left",
            anchor="w",
        )
        self.status_line.pack(fill="x", pady=(4, 0))

        self.status_bar_frame = tk.Frame(body, bg="#0f172a")
        self.status_bar_frame.pack(fill="x", pady=(14, 0))

        self.cpu_bar = tk.Label(self.status_bar_frame, text="", font=("Consolas", 11), bg="#0f172a", fg="#6ee7b7")
        self.cpu_bar.pack(anchor="w", pady=3)
        self.gpu_bar = tk.Label(self.status_bar_frame, text="", font=("Consolas", 11), bg="#0f172a", fg="#fbbf24")
        self.gpu_bar.pack(anchor="w", pady=3)
        self.ram_bar = tk.Label(self.status_bar_frame, text="", font=("Consolas", 11), bg="#0f172a", fg="#60a5fa")
        self.ram_bar.pack(anchor="w", pady=3)
        self.disk_bar = tk.Label(self.status_bar_frame, text="", font=("Consolas", 11), bg="#0f172a", fg="#a78bfa")
        self.disk_bar.pack(anchor="w", pady=3)

    def set_language(self, code: str):
        self.language = code
        if self.root is not None:
            self.update_ui(force=True)

    def set_theme(self, theme_name: str):
        if theme_name in self.THEMES:
            self.theme = theme_name
            self._apply_theme()
            if self.root is not None:
                self.update_ui(force=True)

    def _draw_history_graph(self, canvas, data_points, color, y_max, label):
        if not data_points:
            return
        width = 420
        height = 180
        padding = 20
        data = data_points[-120:]
        x_step = (width - 2 * padding) / max(len(data) - 1, 1)
        points = []
        for i, value in enumerate(data):
            x = padding + i * x_step
            y = height - padding - (value / y_max) * (height - 2 * padding)
            points.append((x, y))
        if len(points) > 1:
            canvas.create_line(points, fill=color, width=2)
        canvas.create_text(30, 12, text=label, fill=color, anchor="w", font=("Segoe UI", 9, "bold"))

    def show_history(self):
        if self.root is None or self.headless:
            return
        if self.history_window is not None and self.history_window.winfo_exists():
            self.history_window.focus_set()
            return

        history = self.monitor.history
        self.history_window = tk.Toplevel(self.root)
        self.history_window.title("Performance History")
        self.history_window.geometry("520x420")
        self.history_window.configure(bg="#0b1220")

        canvas = tk.Canvas(self.history_window, width=500, height=360, bg="#0b1220", highlightthickness=0)
        canvas.pack(padx=10, pady=10)

        canvas.create_line(20, 20, 480, 20, fill="#334155")
        canvas.create_line(20, 200, 480, 200, fill="#334155")
        canvas.create_line(20, 340, 480, 340, fill="#334155")

        temps = [item["gpu"] for item in history["temperature"]]
        cpu_hist = [item["cpu"] for item in history["usage"]]
        gpu_hist = [item["gpu"] for item in history["usage"]]

        self._draw_history_graph(canvas, temps, "#fbbf24", max(100, max(temps, default=100)), "GPU Temp")
        self._draw_history_graph(canvas, gpu_hist, "#60a5fa", 100, "GPU Usage")
        canvas.create_text(20, 335, text="CPU trend: " + str(cpu_hist[-1:]), fill="#cbd5e1", anchor="w", font=("Segoe UI", 9))

    def toggle_taskbar(self):
        if self.root is None or self.headless:
            return
        if self.taskbar_widget is None or not self.taskbar_widget.winfo_exists():
            self.create_taskbar_widget()
        else:
            self.taskbar_widget.destroy()
            self.taskbar_widget = None

    def create_taskbar_widget(self):
        if self.root is None:
            return
        self.taskbar_widget = tk.Toplevel(self.root)
        self.taskbar_widget.overrideredirect(True)
        self.taskbar_widget.attributes("-topmost", True)
        self.taskbar_widget.configure(bg="#020817")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        widget_w = 560
        widget_h = 74
        x = max(0, (screen_w - widget_w) // 2)
        y = max(0, screen_h - widget_h - 18)
        self.taskbar_widget.geometry(f"{widget_w}x{widget_h}+{x}+{y}")

        frame = tk.Frame(self.taskbar_widget, bg="#020817", padx=12, pady=10)
        frame.pack(fill="both", expand=True)

        self.taskbar_title = tk.Label(frame, text="System", bg="#020817", fg="#e2e8f0", font=("Segoe UI", 10, "bold"))
        self.taskbar_title.pack(anchor="w")

        self.taskbar_cpu = tk.Label(frame, text="", bg="#020817", fg="#6ee7b7", font=("Consolas", 10))
        self.taskbar_cpu.pack(anchor="w")

        self.taskbar_stats = tk.Label(frame, text="", bg="#020817", fg="#cbd5e1", font=("Segoe UI", 9))
        self.taskbar_stats.pack(anchor="w")

        self.update_taskbar_widget()

    def update_taskbar_widget(self):
        if self.taskbar_widget is None or not self.taskbar_widget.winfo_exists():
            return
        data = self.last_data or self.monitor.read()
        self.taskbar_cpu.config(text=f"CPU {data.cpu_usage}%  GPU {data.gpu_usage}%  RAM {(data.ram_used / data.ram_total * 100 if data.ram_total else 0):.0f}%  SSD {data.disk_health}%")
        self.taskbar_stats.config(text=f"Temp {data.cpu_temp}°C / {data.gpu_temp}°C  Health {data.health_score}/100")
        self.taskbar_widget.after(2000, self.update_taskbar_widget)

    def toggle_overlay(self):
        if self.root is None or self.headless:
            return
        if self.overlay_root is None or not self.overlay_root.winfo_exists():
            self.create_overlay()
        else:
            self.overlay_root.destroy()
            self.overlay_root = None

    def create_overlay(self):
        self.overlay_root = tk.Toplevel(self.root)
        self.overlay_root.overrideredirect(True)
        self.overlay_root.attributes("-topmost", True)
        self.overlay_root.attributes("-alpha", 0.85)
        self.overlay_root.geometry("420x150+1680+30")
        self.overlay_root.configure(bg="#020817")

        frame = tk.Frame(self.overlay_root, bg="#020817", padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        title = tk.Label(frame, text="Gaming Mode", font=("Segoe UI", 14, "bold"), bg="#020817", fg="#f8fafc")
        title.pack(anchor="w")

        self.overlay_stats = tk.Label(frame, text="", font=("Consolas", 18, "bold"), bg="#020817", fg="#7dd3fc")
        self.overlay_stats.pack(anchor="w", pady=(8, 0))

        self.overlay_status = tk.Label(frame, text="", font=("Segoe UI", 10), bg="#020817", fg="#a7f3d0")
        self.overlay_status.pack(anchor="w")

        self.update_overlay()

    def update_overlay(self):
        if self.overlay_root is None or not self.overlay_root.winfo_exists():
            return
        data = self.monitor.read()
        self.overlay_stats.config(text=f"FPS 144   CPU {data.cpu_temp}°C   GPU {data.gpu_temp}°C")
        self.overlay_status.config(text=f"CPU {data.cpu_usage}% | GPU {data.gpu_usage}% | RAM {data.ram_used:.1f}/{data.ram_total:.1f} GB | VRAM {data.vram_used:.1f}/{data.vram_total:.1f} GB")
        self.overlay_root.after(2000, self.update_overlay)

    def update_ui(self, force=False):
        if self.root is None:
            return
        data = self.monitor.read()
        self.last_data = data

        self.cpu_card.destroy()
        self.gpu_card.destroy()
        self.ram_card.destroy()
        self.disk_card.destroy()
        self.health_card.destroy()

        self.cpu_card = self._build_card(self.metric_frame, self._t("cpu"), "#6ee7b7", f"{data.cpu_temp}°C | {data.cpu_usage}%", self._status_for_temp(data.cpu_temp), data.cpu_usage)
        self.gpu_card = self._build_card(self.metric_frame, self._t("gpu"), "#fbbf24", f"{data.gpu_temp}°C | {data.gpu_usage}%", self._status_for_temp(data.gpu_temp), data.gpu_usage)
        self.ram_card = self._build_card(self.metric_frame, self._t("ram"), "#60a5fa", f"{data.ram_used:.1f} / {data.ram_total:.1f} GB", self._t("normal"), (data.ram_used / data.ram_total) * 100 if data.ram_total else 0)
        self.disk_card = self._build_card(self.metric_frame, self._t("ssd"), "#a78bfa", f"{data.disk_temp}°C | {data.disk_health}%", self._t("normal"), (data.disk_used / data.disk_total) * 100 if data.disk_total else 0)
        self.health_card = self._build_card(self.metric_frame, self._t("health"), "#34d399", f"{data.health_score}/100", self._t("normal"), data.health_score)

        summary = self.monitor.get_status_summary(data)
        self.summary_label.config(
            text=(
                f"{self._t('health_score')}: {data.health_score}/100   |   "
                f"CPU {data.cpu_temp}°C   GPU {data.gpu_temp}°C   RAM {(data.ram_used / data.ram_total * 100 if data.ram_total else 0):.0f}%   SSD {data.disk_health}%"
            )
        )
        self.alert_label.config(
            text=(self._t("alerts") + ": " + (", ".join(data.alerts) if data.alerts else self._t("no_alerts")))
        )
        self.status_line.config(text=f"Status: {summary['state'].upper()} • {summary['summary_text']}")

        cpu_bar = self._mini_bar(data.cpu_usage)
        gpu_bar = self._mini_bar(data.gpu_usage)
        ram_bar = self._mini_bar((data.ram_used / data.ram_total) * 100 if data.ram_total else 0)
        disk_bar = self._mini_bar((data.disk_used / data.disk_total) * 100 if data.disk_total else 0)

        self.cpu_bar.config(text=f"CPU  {cpu_bar}  {data.cpu_usage}%")
        self.gpu_bar.config(text=f"GPU  {gpu_bar}  {data.gpu_usage}%")
        self.ram_bar.config(text=f"RAM  {ram_bar}  {(data.ram_used / data.ram_total * 100 if data.ram_total else 0):.0f}%")
        self.disk_bar.config(text=f"SSD  {disk_bar}  {data.disk_health}%")

        if self.taskbar_widget is not None and self.taskbar_widget.winfo_exists():
            self.update_taskbar_widget()

        self.root.after(2000, self.update_ui)

    def run(self):
        if self.root is None:
            self.last_data = self.monitor.read()
            return self.last_data

        self.update_ui(force=True)
        self.root.mainloop()
