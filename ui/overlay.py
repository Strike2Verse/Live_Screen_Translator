from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(300, 200, 500, 300)

        self.results = []
        self.hide_overlay = False
        self.is_moving = False

        self.dragging = False
        self.resizing = False
        self.offset = None
        self.resize_margin = 10

    def is_interacting(self):   # ✅ ADD THIS
        return self.dragging or self.resizing or self.is_moving

    def update_results(self, results):
        # 🔥 ALWAYS HANDLE RESULTS

        if not results:
            self.results = []   # clear overlay
            self.update()
            return

        self.results = results
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(0, 120, 255, 30))
        painter.setPen(QPen(QColor(0, 120, 255), 2, Qt.DashLine))
        painter.drawRect(self.rect())

        if self.hide_overlay:
            return

        for r in self.results:
            metrics = painter.fontMetrics()
            text_width = metrics.boundingRect(r["translated"]).width()

            rect = QRect(
                r["x"] + 3,
                r["y"] + 3,
                max(text_width + 20, r["w"]),
                max(20, r["h"])
            )

            font = QFont("Noto Sans", 10, QFont.Bold)
            if r["h"] > 50:
                font.setPointSize(12)
            elif r["h"] < 25:
                font.setPointSize(8)

            painter.setFont(font)

            painter.setBrush(QColor(0, 0, 0, 200))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 10, 10)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(
                rect,
                Qt.AlignCenter | Qt.TextWordWrap,
                r["translated"]
            )

    def mousePressEvent(self, event):
        pos = event.position().toPoint()

        if abs(pos.x() - self.width()) < self.resize_margin and \
           abs(pos.y() - self.height()) < self.resize_margin:
            self.resizing = True
        else:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        self.is_moving = True
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        if self.resizing:
            self.resize(max(150, pos.x()), max(100, pos.y()))
        elif self.dragging:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.is_moving = False