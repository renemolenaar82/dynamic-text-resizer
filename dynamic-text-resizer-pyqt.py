import sys
import platform
from PyQt5.QtCore import Qt, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QTextCursor, QColor, QPalette, QFontMetrics
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit

class AnimatedTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._font_size = 72
        self._target_font_size = 72
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set font to DejaVu Sans with Arial as fallback
        font = QFont()
        font.setFamily("DejaVu Sans, Arial")
        font.setPointSize(self._font_size)
        self.setFont(font)
        
        self.setStyleSheet("""
            QTextEdit {
                background: #1A1A1A;
                color: #E0E0E0;
                border: none;
                padding: 40px;
                selection-background-color: #444;
                selection-color: #FFF;
            }
        """)
        self.setCursorWidth(2)
        palette = self.palette()
        palette.setColor(QPalette.Highlight, QColor("#444"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFF"))
        self.setPalette(palette)
        self.textChanged.connect(self.schedule_adjust_font_size)
        self.animation = QPropertyAnimation(self, b"fontSize")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._resize_timer = QTimer(self)
        self._resize_timer.setInterval(100)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self.adjust_font_size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.schedule_adjust_font_size()

    def schedule_adjust_font_size(self):
        self._resize_timer.start()

    def minimumSizeHint(self):
        return super().minimumSizeHint()

    # Property for animation
    def getFontSize(self):
        return self._font_size

    def setFontSize(self, size):
        size = int(size)
        if size != self._font_size:
            self._font_size = size
            font = self.font()
            font.setPointSize(size)
            self.setFont(font)

    fontSize = pyqtProperty(int, fget=getFontSize, fset=setFontSize)

    def adjust_font_size(self):
        text = self.toPlainText()
        if not text:
            new_size = 72
            if new_size != self._font_size:
                self.animate_font_size(new_size)
            return

        # Binary search for best fit
        min_size, max_size = 8, 200
        best_size = min_size
        width = int(self.viewport().width() - 20)
        height = int(self.viewport().height() - 20)
        if width <= 1 or height <= 1:
            return

        while min_size <= max_size:
            mid = (min_size + max_size) // 2
            font = QFont("DejaVu Sans, Arial", mid)
            lines = self.calculate_wrapped_lines(text, font, width)
            line_height = QFontMetrics(font).lineSpacing()
            total_height = len(lines) * line_height

            if total_height <= height:
                best_size = mid
                min_size = mid + 1
            else:
                max_size = mid - 1

        target_size = max(8, best_size - 2)
        if target_size != self._font_size:
            self.animate_font_size(target_size)

    def animate_font_size(self, to_size):
        self.animation.stop()
        self.animation.setStartValue(self._font_size)
        self.animation.setEndValue(to_size)
        self.animation.start()

    def calculate_wrapped_lines(self, text, font, width):
        metrics = QFontMetrics(font)
        lines = []
        for para in text.split('\n'):
            words = para.split()
            if not words:
                lines.append("")
                continue
            current_line = ""
            for word in words:
                test_line = (current_line + " " + word) if current_line else word
                if metrics.width(test_line) <= width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
        return lines if lines else [""]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Font Size Text")

        # Maximize window cross-platform
        system = platform.system()
        if system == "Windows":
            self.showFullScreen()
        elif system == "Darwin":
            self.showFullScreen()
        else:
            self.showFullScreen()

        # Set background black
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("black"))
        self.setPalette(pal)

        # Central Widget
        self.text_widget = AnimatedTextEdit()
        self.setCentralWidget(self.text_widget)

        # Keyboard shortcut: Ctrl+A for select all
        self.text_widget.installEventFilter(self)

        # Focus & cursor on startup
        QTimer.singleShot(150, self.activate_window)

    def activate_window(self):
        self.raise_()
        self.activateWindow()
        self.text_widget.setFocus()
        cursor = QTextCursor(self.text_widget.document())
        cursor.movePosition(QTextCursor.Start)
        self.text_widget.setTextCursor(cursor)

    # Optional: cross-platform Ctrl+A handling (for Mac/Win/Linux consistency)
    def eventFilter(self, obj, event):
        if obj is self.text_widget and event.type() == event.KeyPress:
            if (event.key() == Qt.Key_A and (event.modifiers() & Qt.ControlModifier)):
                self.text_widget.selectAll()
                return True
            elif event.key() == Qt.Key_Escape:
                self.showNormal()  # Exit full screen when Escape is pressed
                return True
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())