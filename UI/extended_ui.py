from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

class MyQWidget(QWidget):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        print(str(event.key()))


class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        print(str(event.key()))



