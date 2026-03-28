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
        self.resize_margin = 14

    def is_interacting(self):
        return self.dragging or self.resizing or self.is_moving

    def update_results(self, results):
        # Update overlay only when valid results are available
        if not results:
            self.results = []
            self.update()
            return

        self.results = results
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Enable smooth rendering for text and shapes
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw selection border
        painter.setBrush(QColor(0, 120, 255, 20))
        painter.setPen(QPen(QColor(0, 120, 255, 2), 2, Qt.DashLine))
        painter.drawRect(self.rect())

        if self.hide_overlay:
            return

        for r in self.results:
            font = QFont()
            font.setFamilies(["Segoe UI", "Arial", "Sans Serif"])
            font.setPointSize(10)
            font.setWeight(QFont.DemiBold)
            font.setLetterSpacing(QFont.PercentageSpacing, 102)

            painter.setFont(font)

            metrics = painter.fontMetrics()
            text_width = metrics.boundingRect(r["translated"]).width()

            # Center translation above detected text
            center_x = r["x"] + r["w"] // 2
            width = max(text_width + 20, r["w"])

            rect = QRect(
                center_x - width // 2,
                r["y"] + 2,
                width,
                max(22, r["h"])
            )

            # Shadow
            shadow = rect.adjusted(2, 2, 2, 2)
            painter.setBrush(QColor(0, 0, 0, 120))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(shadow, 10, 10)

            # Background pill
            painter.setBrush(QColor(20, 20, 20, 210))
            painter.drawRoundedRect(rect, 12, 12)

            # Adjust font size based on box height
            if r["h"] > 50:
                font.setPointSize(12)
            elif r["h"] < 22:
                font.setPointSize(9)
            else:
                font.setPointSize(10)

            painter.setFont(font)

            inner_rect = rect.adjusted(8, 4, -8, -4)

            painter.setPen(QColor(245, 245, 245))
            painter.drawText(
                inner_rect,
                Qt.AlignCenter | Qt.TextWordWrap,
                r["translated"]
            )

        # Resize handle
        handle_size = 16
        painter.setBrush(QColor(0, 120, 255, 220))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(
            QRect(
                self.width() - handle_size,
                self.height() - handle_size,
                handle_size,
                handle_size
            ),
            4, 4
        )

    def mousePressEvent(self, event):
        pos = event.position().toPoint()

        # Detect resize area (bottom-right corner)
        if abs(pos.x() - self.width()) < self.resize_margin and \
           abs(pos.y() - self.height()) < self.resize_margin:
            self.resizing = True
        else:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        self.is_moving = True

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