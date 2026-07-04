DARK = """
QWidget { background-color: #1e1f22; color: #d4d6d9; font-family: "Segoe UI", Arial; font-size: 13px; }
QMainWindow { background-color: #1e1f22; }
QTabWidget::pane { border: 1px solid #33363a; background-color: #232427; }
QTabBar::tab { background-color: #2a2c30; color: #9a9da1; padding: 8px 18px; border: 1px solid #33363a; border-bottom: none; }
QTabBar::tab:selected { background-color: #232427; color: #4fc3f7; border-top: 2px solid #4fc3f7; }
QGroupBox { border: 1px solid #33363a; border-radius: 4px; margin-top: 10px; padding-top: 10px; font-weight: bold; color: #9a9da1; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QPushButton { background-color: #2f3236; border: 1px solid #45484d; border-radius: 4px; padding: 6px 14px; color: #d4d6d9; }
QPushButton:hover { background-color: #3a3d42; border-color: #4fc3f7; }
QPushButton:pressed { background-color: #232427; }
QPushButton:disabled { color: #5a5d61; }
QComboBox, QLineEdit { background-color: #2a2c30; border: 1px solid #45484d; border-radius: 3px; padding: 4px 8px; }
QProgressBar { border: 1px solid #45484d; border-radius: 4px; text-align: center; background-color: #2a2c30; }
QProgressBar::chunk { background-color: #4caf50; border-radius: 3px; }
QStatusBar { background-color: #2a2c30; border-top: 1px solid #33363a; }
QListWidget, QTableWidget { background-color: #232427; border: 1px solid #33363a; gridline-color: #33363a; }
QHeaderView::section { background-color: #2a2c30; color: #9a9da1; padding: 4px; border: 1px solid #33363a; }
QDoubleSpinBox, QSpinBox { background-color: #2a2c30; border: 1px solid #45484d; border-radius: 3px; padding: 4px 8px; color: #d4d6d9; }
QLabel { color: #d4d6d9; }
"""

LIGHT = """
QWidget { background-color: #f5f5f5; color: #1a1a1a; font-family: "Segoe UI", Arial; font-size: 13px; }
QMainWindow { background-color: #f5f5f5; }
QTabWidget::pane { border: 1px solid #cccccc; background-color: #ffffff; }
QTabBar::tab { background-color: #e0e0e0; color: #555555; padding: 8px 18px; border: 1px solid #cccccc; border-bottom: none; }
QTabBar::tab:selected { background-color: #ffffff; color: #0277bd; border-top: 2px solid #0277bd; }
QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 10px; padding-top: 10px; font-weight: bold; color: #555555; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QPushButton { background-color: #e0e0e0; border: 1px solid #bbbbbb; border-radius: 4px; padding: 6px 14px; color: #1a1a1a; }
QPushButton:hover { background-color: #bbdefb; border-color: #0277bd; }
QPushButton:pressed { background-color: #cccccc; }
QPushButton:disabled { color: #aaaaaa; }
QComboBox, QLineEdit { background-color: #ffffff; border: 1px solid #bbbbbb; border-radius: 3px; padding: 4px 8px; color: #1a1a1a; }
QProgressBar { border: 1px solid #bbbbbb; border-radius: 4px; text-align: center; background-color: #e0e0e0; }
QProgressBar::chunk { background-color: #4caf50; border-radius: 3px; }
QStatusBar { background-color: #e0e0e0; border-top: 1px solid #cccccc; }
QListWidget, QTableWidget { background-color: #ffffff; border: 1px solid #cccccc; gridline-color: #eeeeee; }
QHeaderView::section { background-color: #e0e0e0; color: #555555; padding: 4px; border: 1px solid #cccccc; }
QDoubleSpinBox, QSpinBox { background-color: #ffffff; border: 1px solid #bbbbbb; border-radius: 3px; padding: 4px 8px; color: #1a1a1a; }
QLabel { color: #1a1a1a; }
"""


def get_style(dark=True):
    return DARK if dark else LIGHT