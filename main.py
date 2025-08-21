import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QHBoxLayout, QStackedLayout, QScrollArea
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from reconstruct import ReconstructTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AREP 3D City - Aplikasi Rekonstruksi Praktis 3D City")
        self.setWindowIcon(QIcon("logo.png"))

        # Central widget and layout
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        # Tab widget
        central_layout.addWidget(ReconstructTab())

        # Footer
        footer_layout = QHBoxLayout()

        footer_text = QLabel("Departemen Teknik Geodesi Fakultas Teknik Universitas Gadjah Mada")
        footer_text.setStyleSheet("font-size: 10pt; color: gray;")
        footer_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        footer_layout.addWidget(footer_text)
        central_layout.addLayout(footer_layout)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())