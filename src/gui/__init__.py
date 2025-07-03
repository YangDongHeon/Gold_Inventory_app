
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from .main_window import MainWindow
from .widgets import _set_light_palette

def launch_app():
    app = QApplication(sys.argv)
    app.setStyle("fusion")          # 기본 Fusion 라이트
    _set_light_palette(app)         # 라이트 팔레트 설정

    app.setFont(QFont("Arial", 12))
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec_())
