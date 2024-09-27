import sys
import io
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt, QRect
from PIL import ImageGrab

class SnippingTool(QWidget):
    def __init__(self):
        super().__init__()
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.is_snipping = False
        self.snipped_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Snipping Tool')
        self.setGeometry(100, 100, 300, 200)

        self.label = QLabel("Press 'Start Snip' to capture a portion of the screen", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.snip_btn = QPushButton('Start Snip', self)
        self.snip_btn.clicked.connect(self.startSnipping)

        self.save_btn = QPushButton('Save Snip', self)
        self.save_btn.clicked.connect(self.saveSnip)
        self.save_btn.setEnabled(False)

        self.resnip_btn = QPushButton('Resnip', self)
        self.resnip_btn.clicked.connect(self.startSnipping)
        self.resnip_btn.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.snip_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.resnip_btn)

        self.setLayout(layout)
        self.show()

    def startSnipping(self):
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowOpacity(0.3)
        self.is_snipping = True
        self.label.setText("Click and drag to select the area to snip. Use arrow keys to adjust.")
        self.snip_btn.setEnabled(False)
        self.resnip_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

    def paintEvent(self, event):
        if self.is_snipping and None not in (self.start_x, self.start_y, self.end_x, self.end_y):
            brush = QPainter(self)
            brush.setPen(Qt.red)
            brush.drawRect(QRect(self.start_x, self.start_y, self.end_x - self.start_x, self.end_y - self.start_y))

    def mousePressEvent(self, event):
        if self.is_snipping:
            self.start_x = event.x()
            self.start_y = event.y()

    def mouseMoveEvent(self, event):
        if self.is_snipping:
            self.end_x = event.x()
            self.end_y = event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_snipping:
            self.end_x = event.x()
            self.end_y = event.y()
            self.is_snipping = False
            self.update()
            self.captureScreen()
            self.save_btn.setEnabled(True)
            self.resnip_btn.setEnabled(True)
            self.setWindowOpacity(1.0)
            self.setWindowState(Qt.WindowNoState)

    def keyPressEvent(self, event):
        if self.is_snipping and None not in (self.start_x, self.start_y, self.end_x, self.end_y):
            if event.key() == Qt.Key_Left:
                self.start_x -= 1
                self.end_x -= 1
            elif event.key() == Qt.Key_Right:
                self.start_x += 1
                self.end_x += 1
            elif event.key() == Qt.Key_Up:
                self.start_y -= 1
                self.end_y -= 1
            elif event.key() == Qt.Key_Down:
                self.start_y += 1
                self.end_y += 1
            self.update()

    def captureScreen(self):
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        # Capture the screen using PIL
        self.snipped_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        # Convert the captured image to a format Qt can use
        buffer = io.BytesIO()
        self.snipped_image.save(buffer, format="PNG")
        buffer.seek(0)
        image = QImage()
        image.loadFromData(buffer.getvalue())

        # Set the QLabel to display the snipped image
        self.label.setPixmap(QPixmap.fromImage(image))

    def saveSnip(self):
        if self.snipped_image:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Snip", "", "PNG Files (*.png);;All Files (*)", options=options
            )
            
            if file_path:
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'  # Ensure the file has a .png extension

                self.snipped_image.save(file_path)
                self.label.setText(f"Snip saved as '{file_path}'")
                self.save_btn.setEnabled(False)
                self.snip_btn.setEnabled(True)
                self.resnip_btn.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tool = SnippingTool()
    sys.exit(app.exec_())
