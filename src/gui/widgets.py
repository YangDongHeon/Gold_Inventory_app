
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

def _set_light_palette(app: QApplication):
    pal = QPalette()
    pal.setColor(QPalette.Window,        QColor("#ffffff"))
    pal.setColor(QPalette.Base,          QColor("#ffffff"))
    pal.setColor(QPalette.AlternateBase, QColor("#fafafa"))
    pal.setColor(QPalette.Text,          QColor("#212121"))   # 거의 검정
    pal.setColor(QPalette.WindowText,    QColor("#212121"))
    pal.setColor(QPalette.ButtonText,    QColor("#212121"))
    pal.setColor(QPalette.Highlight,     QColor("#1890ff"))   # 포인트 블루
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
