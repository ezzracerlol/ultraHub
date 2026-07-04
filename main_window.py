from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QStatusBar, QLabel, QSystemTrayIcon, QPushButton
)
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import QTimer

from whoophub_config import load_whoophub_config
from whoophub_serial import WhoopHubSerial
from whoophub_theme import get_style
from whoophub_lang import get_lang
from msp_reader import (
    MSPParser, build_request,
    decode_analog, MSP_ANALOG,
    decode_fc_variant, decode_fc_version, decode_board_info, decode_status_ex,
    MSP_FC_VARIANT, MSP_FC_VERSION, MSP_BOARD_INFO, MSP_STATUS_EX,
    decode_rc, decode_motor, decode_attitude,
    MSP_RC, MSP_MOTOR, MSP_ATTITUDE,
    decode_gps, MSP_RAW_GPS,
)

from connection_widget import ConnectionWidget
from battery_widget import BatteryWidget
from video_widget import VideoWidget
from logs_widget import LogsWidget
from stats_widget import StatsWidget
from system_widget import SystemWidget
from profiles_widget import ProfilesWidget
from rc_widget import RCWidget
from motors_widget import MotorsWidget
from attitude_widget import AttitudeWidget
from whoophub_history import SessionHistoryWidget
from notifications import WhoopNotifier
from gps_map_widget import GpsMapWidget
from drone_3d_widget import Drone3DWidget
from cycles_widget import CyclesWidget
from checklist_widget import ChecklistWidget
from weather_widget import WeatherWidget
from osd_widget import OSDWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_whoophub_config()
        self.active_profile = self.config.copy()
        self._dark_mode = True
        self._ru_lang = True

        self.serial = WhoopHubSerial()
        self.msp_parser = MSPParser()
        self._fc_info_requested = False
        self._poll_counter = 0

        self.notifier = WhoopNotifier()
        self._setup_tray()
        self._build_ui()
        self._connect_signals()
        self._apply_theme()

        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_telemetry)
        self.refresh_ports()

    def _setup_tray(self):
        px = QPixmap(32, 32)
        px.fill(QColor("#4fc3f7"))
        self.tray = QSystemTrayIcon(QIcon(px), self)
        self.tray.setToolTip("WhoopHub")
        self.tray.show()
        self.notifier.setup(self.tray)

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        top_row = QHBoxLayout()
        self.connection_widget = ConnectionWidget()
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedWidth(110)
        self.theme_btn.clicked.connect(self._toggle_theme)
        self.lang_btn = QPushButton()
        self.lang_btn.setFixedWidth(50)
        self.lang_btn.clicked.connect(self._toggle_lang)
        top_row.addWidget(self.connection_widget, stretch=1)
        top_row.addWidget(self.theme_btn)
        top_row.addWidget(self.lang_btn)
        layout.addLayout(top_row)

        self.tabs = QTabWidget()

        dashboard = QWidget()
        dash_layout = QVBoxLayout(dashboard)
        self.battery_widget = BatteryWidget(
            full_v=self.active_profile.get("full_voltage", 4.35),
            empty_v=self.active_profile.get("empty_voltage", 3.0),
            warn_v=self.active_profile.get("warn_voltage", 3.3),
        )
        dash_layout.addWidget(self.battery_widget)
        dash_layout.addStretch()

        self.system_widget    = SystemWidget()
        self.drone_3d         = Drone3DWidget()
        self.rc_widget        = RCWidget()
        self.motors_widget    = MotorsWidget()
        self.attitude_widget  = AttitudeWidget()
        self.gps_widget       = GpsMapWidget()
        self.osd_widget       = OSDWidget()
        self.video_widget     = VideoWidget()
        self.logs_widget      = LogsWidget()
        self.stats_widget     = StatsWidget()
        self.history_widget   = SessionHistoryWidget()
        self.cycles_widget    = CyclesWidget()
        self.checklist_widget = ChecklistWidget()
        self.weather_widget   = WeatherWidget()
        self.profiles_widget  = ProfilesWidget()
        self.profiles_widget.profile_selected.connect(self._apply_profile)

        self.tabs.addTab(dashboard,               "Дашборд")
        self.tabs.addTab(self.system_widget,      "Система")
        self.tabs.addTab(self.drone_3d,           "3D Модель")
        self.tabs.addTab(self.rc_widget,          "RC Каналы")
        self.tabs.addTab(self.motors_widget,      "Моторы")
        self.tabs.addTab(self.attitude_widget,    "Горизонт")
        self.tabs.addTab(self.gps_widget,         "GPS Карта")
        self.tabs.addTab(self.osd_widget,         "OSD")
        self.tabs.addTab(self.video_widget,       "Видео")
        self.tabs.addTab(self.logs_widget,        "Логи")
        self.tabs.addTab(self.stats_widget,       "Статистика")
        self.tabs.addTab(self.history_widget,     "История")
        self.tabs.addTab(self.cycles_widget,      "Батареи")
        self.tabs.addTab(self.checklist_widget,   "Чеклист")
        self.tabs.addTab(self.weather_widget,     "Погода")
        self.tabs.addTab(self.profiles_widget,    "Профили")

        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        self.status_bar   = QStatusBar()
        self.drone_label  = QLabel()
        self.notice_label = QLabel()
        self.status_bar.addWidget(self.drone_label)
        self.status_bar.addPermanentWidget(self.notice_label)
        self.setStatusBar(self.status_bar)

        self._update_texts()

    def _get_lang(self):
        return get_lang(self._ru_lang)

    def _update_texts(self):
        L = self._get_lang()
        self.setWindowTitle(L["app_title"])
        self.theme_btn.setText(L["theme_btn_light"] if self._dark_mode else L["theme_btn_dark"])
        self.lang_btn.setText(L["lang_btn"])
        self.notice_label.setText(L["status_notice"])
        self.drone_label.setText(
            f"{L['drone_label']} {self.active_profile.get('drone_name', self.active_profile.get('name', '—'))}"
        )

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()
        self._update_texts()

    def _toggle_lang(self):
        self._ru_lang = not self._ru_lang
        self._update_texts()

    def _apply_theme(self):
        self.setStyleSheet(get_style(self._dark_mode))

    def _connect_signals(self):
        self.connection_widget.refresh_requested.connect(self.refresh_ports)
        self.connection_widget.connect_requested.connect(self.connect_serial)
        self.connection_widget.disconnect_requested.connect(self.disconnect_serial)

    def _apply_profile(self, profile):
        self.active_profile = profile
        self.battery_widget.full_v = profile["full_voltage"]
        self.battery_widget.warn_v = profile["warn_voltage"]
        self.battery_widget.empty_v = profile["empty_voltage"]
        self.weather_widget.set_profile(profile)
        self._update_texts()

    def refresh_ports(self):
        self.connection_widget.set_ports(self.serial.list_ports())

    def connect_serial(self, port):
        ok = self.serial.connect(port, baudrate=115200)
        self.connection_widget.set_connected_state(ok)
        if ok:
            self._fc_info_requested = False
            self.poll_timer.start(250)

    def disconnect_serial(self):
        self.poll_timer.stop()
        self.serial.disconnect()
        self.connection_widget.set_connected_state(False)
        self.battery_widget.reset()

    def _poll_telemetry(self):
        if not self.serial.is_connected():
            return

        if not self._fc_info_requested:
            for cmd in [MSP_FC_VARIANT, MSP_FC_VERSION, MSP_BOARD_INFO]:
                self.serial.write(build_request(cmd))
            self._fc_info_requested = True

        self.serial.write(build_request(MSP_ANALOG))
        self.serial.write(build_request(MSP_RC))
        self.serial.write(build_request(MSP_ATTITUDE))

        self._poll_counter += 1
        if self._poll_counter % 8 == 0:
            self.serial.write(build_request(MSP_STATUS_EX))
            self.serial.write(build_request(MSP_MOTOR))
            self.serial.write(build_request(MSP_RAW_GPS))

        raw = self.serial.read_all()
        if not raw:
            return
        self.msp_parser.feed(raw)

        for command, payload in self.msp_parser.parse_frames():
            if command == MSP_ANALOG:
                data = decode_analog(payload)
                if data:
                    self.battery_widget.update_values(
                        data["voltage"], data["current"], data["mah_drawn"]
                    )
                    self.stats_widget.add_point(data["voltage"], data["current"])
                    self.logs_widget.add_entry(
                        data["voltage"], data["current"], data["mah_drawn"]
                    )
                    self.osd_widget.update_telemetry(
                        voltage=data["voltage"],
                        current=data["current"],
                        mah=data["mah_drawn"],
                        rssi=data["rssi_percent"],
                    )
                    self.notifier.check_voltage(
                        data["voltage"],
                        self.active_profile.get("warn_voltage", 3.3),
                        self.active_profile.get("empty_voltage", 3.0),
                    )
            elif command == MSP_FC_VARIANT:
                self.system_widget.update_fc_info(variant=decode_fc_variant(payload))
            elif command == MSP_FC_VERSION:
                self.system_widget.update_fc_info(version=decode_fc_version(payload))
            elif command == MSP_BOARD_INFO:
                self.system_widget.update_fc_info(board=decode_board_info(payload))
            elif command == MSP_STATUS_EX:
                status = decode_status_ex(payload)
                if status:
                    self.system_widget.update_status(status)
                    self.osd_widget.update_telemetry(
                        armed=status["armed"],
                        sats=len(status["sensors"]),
                    )
            elif command == MSP_RC:
                channels = decode_rc(payload)
                if channels:
                    self.rc_widget.update_channels(channels)
            elif command == MSP_MOTOR:
                motors = decode_motor(payload)
                if motors:
                    self.motors_widget.update_motors(motors)
            elif command == MSP_ATTITUDE:
                att = decode_attitude(payload)
                if att:
                    self.attitude_widget.update_attitude(
                        att["roll"], att["pitch"], att["yaw"]
                    )
                    self.drone_3d.update_attitude(
                        att["roll"], att["pitch"], att["yaw"]
                    )
                    self.osd_widget.update_telemetry(
                        roll=att["roll"],
                        pitch=att["pitch"],
                        yaw=att["yaw"],
                    )
            elif command == MSP_RAW_GPS:
                gps = decode_gps(payload)
                if gps:
                    self.gps_widget.update_gps(
                        gps["lat"], gps["lon"],
                        gps["alt"], gps["sats"], gps["fix"]
                    )

    def closeEvent(self, event):
        self.poll_timer.stop()
        self.serial.disconnect()
        self.video_widget.stop_stream()
        self.logs_widget.stop_session()
        super().closeEvent(event)