from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property
import random
import json

class ModernStyle:
    # Dark theme colors
    DARK_BACKGROUND = "#1E1E1E"
    DARK_DARKER_BACKGROUND = "#171717"
    DARK_TEXT = "#FFFFFF"
    DARK_BORDER = "#333333"

    # Light theme colors
    LIGHT_BACKGROUND = "#FFFFFF"
    LIGHT_DARKER_BACKGROUND = "#F0F0F0"
    LIGHT_TEXT = "#000000"
    LIGHT_BORDER = "#CCCCCC"

    # Common colors
    ACCENT = "#007AFF"
    SECONDARY_ACCENT = "#FF2D55"

    @staticmethod
    def get_stylesheet(is_dark_mode=True):
        bg = ModernStyle.DARK_BACKGROUND if is_dark_mode else ModernStyle.LIGHT_BACKGROUND
        darker_bg = ModernStyle.DARK_DARKER_BACKGROUND if is_dark_mode else ModernStyle.LIGHT_DARKER_BACKGROUND
        text = ModernStyle.DARK_TEXT if is_dark_mode else ModernStyle.LIGHT_TEXT
        border = ModernStyle.DARK_BORDER if is_dark_mode else ModernStyle.LIGHT_BORDER

        return f"""
        QWidget {{
            background-color: {bg};
            color: {text};
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
        }}

        QPushButton {{
            background-color: {ModernStyle.ACCENT};
            border: 2px solid {ModernStyle.ACCENT};
            border-radius: 8px;
            padding: 10px 20px;
            color: white;
            font-weight: bold;
            font-size: 13px;
            min-width: 100px;
        }}

        QPushButton:hover {{
            background-color: #0056b3;
            border-color: #0056b3;
        }}

        QLineEdit {{
            background-color: {darker_bg};
            border: 2px solid {border};
            border-radius: 6px;
            padding: 8px;
            color: {text};
            font-size: 14px;
        }}

        QGraphicsView {{
            background-color: {darker_bg};
            border: 2px solid {border};
            border-radius: 12px;
            padding: 20px;
            margin: 10px;
        }}

        QSlider {{
            height: 24px;
            background: transparent;
        }}

        QSlider::groove:horizontal {{
            height: 4px;
            background: {darker_bg};
            border-radius: 2px;
            margin: 0px;
        }}

        QSlider::handle:horizontal {{
            background: {ModernStyle.ACCENT};
            border: 2px solid {ModernStyle.ACCENT};
            width: 18px;
            height: 18px;
            border-radius: 9px;
            margin: -8px 0;
        }}

        QSlider::handle:horizontal:hover {{
            background: #0056b3;
            border-color: #0056b3;
        }}

        QSlider::sub-page:horizontal {{
            background: {ModernStyle.ACCENT};
            border-radius: 2px;
        }}

        QSlider::add-page:horizontal {{
            background: {border};
            border-radius: 2px;
        }}
        """

class FlashcardView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)

        # Create text item
        self.text_item = self.scene.addText("")
        font = QtGui.QFont("Segoe UI", 14)
        font.setBold(True)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QtGui.QColor(ModernStyle.DARK_TEXT))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(self.rect())
        self.centerText()

    def setText(self, text):
        self.text_item.setPlainText(text)
        self.centerText()

    def centerText(self):
        self.text_item.setPos(
            (self.width() - self.text_item.boundingRect().width()) / 2,
            (self.height() - self.text_item.boundingRect().height()) / 2
        )

class FlashcardApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.flashcards = []
        self.current_index = 0
        self.showing_answer = False
        self._rotation = 0
        self.init_ui()

    @Property(float)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.card_view.rotate(value - self.card_view.rotation())

    def init_ui(self):
        self.setWindowTitle('Modern Flashcards')
        self.setMinimumSize(600, 400)
        self.setStyleSheet(ModernStyle.get_stylesheet())

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Add theme toggle slider
        theme_layout = QtWidgets.QHBoxLayout()
        theme_label = QtWidgets.QLabel("Dark Mode")
        self.theme_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.theme_slider.setMaximum(1)
        self.theme_slider.setMinimum(0)
        self.theme_slider.setValue(1)  # Start with dark mode
        self.theme_slider.setFixedWidth(40)  # Make slider more compact
        self.theme_slider.setFixedHeight(24)  # Match height with the styling
        self.theme_slider.valueChanged.connect(self.toggle_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_slider)
        theme_layout.addStretch()
        theme_layout.setContentsMargins(0, 0, 0, 10)  # Add some bottom margin

        layout.addLayout(theme_layout)

        self.card_view = FlashcardView()
        self.card_view.setMinimumHeight(200)
        layout.addWidget(self.card_view)

        button_layout = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("Previous")
        self.flip_btn = QtWidgets.QPushButton("Flip")
        self.next_btn = QtWidgets.QPushButton("Next")
        self.add_btn = QtWidgets.QPushButton("Add Card")

        for btn in [self.prev_btn, self.flip_btn, self.next_btn, self.add_btn]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        self.prev_btn.clicked.connect(self.previous_card)
        self.flip_btn.clicked.connect(self.start_flip_animation)
        self.next_btn.clicked.connect(self.next_card)
        self.add_btn.clicked.connect(self.show_add_dialog)

        self.setLayout(layout)

        self.add_flashcard("What is Python?", "Python is a high-level programming language.")
        self.add_flashcard("What is PySide6?", "A set of Qt bindings for Python to create GUI applications.")
        self.update_display()

    def toggle_theme(self):
        is_dark = self.theme_slider.value() == 1
        self.setStyleSheet(ModernStyle.get_stylesheet(is_dark))
        text_color = ModernStyle.DARK_TEXT if is_dark else ModernStyle.LIGHT_TEXT
        self.card_view.text_item.setDefaultTextColor(QtGui.QColor(text_color))

    def add_flashcard(self, question, answer):
        self.flashcards.append({"question": question, "answer": answer})

    def update_display(self):
        if not self.flashcards:
            self.card_view.setText("No flashcards available")
            return

        card = self.flashcards[self.current_index]
        text = card["answer"] if self.showing_answer else card["question"]
        self.card_view.setText(text)

    def previous_card(self):
        if self.flashcards:
            self.current_index = (self.current_index - 1) % len(self.flashcards)
            self.showing_answer = False
            self.update_display()

    def next_card(self):
        if self.flashcards:
            self.current_index = (self.current_index + 1) % len(self.flashcards)
            self.showing_answer = False
            self.update_display()

    def start_flip_animation(self):
        self.anim = QPropertyAnimation(self, b"rotation")
        self.anim.setDuration(400)
        self.anim.setStartValue(0)
        self.anim.setEndValue(180)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(self._on_flip_finished)
        self.anim.start()

    def _on_flip_finished(self):
        self.showing_answer = not self.showing_answer
        self.update_display()
        self._rotation = 0
        self.card_view.setRotation(0)

    def show_add_dialog(self):
        dialog = AddCardDialog(self)
        if dialog.exec():
            question, answer = dialog.get_card_data()
            self.add_flashcard(question, answer)
            self.update_display()


class AddCardDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add New Flashcard")
        layout = QtWidgets.QVBoxLayout()

        self.question_edit = QtWidgets.QLineEdit()
        self.question_edit.setPlaceholderText("Enter question")
        self.answer_edit = QtWidgets.QLineEdit()
        self.answer_edit.setPlaceholderText("Enter answer")

        layout.addWidget(QtWidgets.QLabel("Question:"))
        layout.addWidget(self.question_edit)
        layout.addWidget(QtWidgets.QLabel("Answer:"))
        layout.addWidget(self.answer_edit)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_card_data(self):
        return self.question_edit.text(), self.answer_edit.text()

def main():
    app = QtWidgets.QApplication([])
    window = FlashcardApp()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
