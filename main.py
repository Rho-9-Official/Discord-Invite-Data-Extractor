import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel
from PyQt5.QtCore import Qt, QTimer
import re
import requests

class LoadingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.loading_label = QLabel("Loading...")
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord Server Invite Info")
        self.setGeometry(100, 100, 1200, 900)  # Larger size

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.invite_entry = QLineEdit()
        self.invite_entry.setPlaceholderText("Enter invite link or code")
        layout.addWidget(self.invite_entry)

        self.fetch_button = QPushButton("Fetch Info")
        self.fetch_button.clicked.connect(self.fetch_invite_info)
        layout.addWidget(self.fetch_button)

        self.invite_list_entry = QLineEdit()
        self.invite_list_entry.setPlaceholderText("Enter multiple invite links or codes (space-separated)")
        layout.addWidget(self.invite_list_entry)

        self.fetch_multiple_button = QPushButton("Fetch Multiple Info")
        self.fetch_multiple_button.clicked.connect(self.fetch_multiple_invite_info)
        layout.addWidget(self.fetch_multiple_button)

        self.info_text = QTextEdit()
        self.info_text.setPlaceholderText("Invite information will be displayed here")
        layout.addWidget(self.info_text)

        self.loading_widget = LoadingWidget()
        self.loading_widget.hide()
        layout.addWidget(self.loading_widget)

        self.central_widget.setLayout(layout)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #202225; /* Darker grey */
            }
            QPushButton {
                background-color: #7289da; /* Discord blue */
                color: #ffffff; /* White */
                border: 2px solid #ffffff; /* White border */
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #677bc4; /* Lighter blue on hover */
            }
            QLineEdit, QTextEdit {
                background-color: #2f3136; /* Slightly darker grey */
                color: #ffffff; /* White */
                border: 2px solid #7289da; /* Discord blue border */
                border-radius: 5px;
                padding: 10px; /* Increased padding */
                font-size: 16px; /* Larger font size */
            }
            QLabel {
                color: #ffffff; /* White */
            }
        """)

    def fetch_invite_info(self):
        invite_input = self.invite_entry.text().strip()
        invite_code = self.extract_invite_code(invite_input)
        if not invite_code:
            self.info_text.setPlainText("Please enter a valid invite link or code.")
            return

        url = f"https://discord.com/api/v8/invites/{invite_code}?with_counts=true"
        self.loading_widget.show()
        QApplication.processEvents()  # Ensure the loading widget is shown
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            invite_data = response.json()

            info_text = f"Guild Name: {invite_data['guild']['name']}\n"
            info_text += f"Guild Members: {invite_data['approximate_member_count']}\n"
            info_text += f"Online Members: {invite_data['approximate_presence_count']}\n"
            info_text += "\nInviter Details:\n"
            inviter = invite_data.get('inviter', {})
            info_text += f"ID: {inviter.get('id', 'None')}\n"
            info_text += f"Username: {inviter.get('username', 'None')}\n"
            info_text += f"Discriminator: {inviter.get('discriminator', 'None')}\n"
            info_text += f"Avatar: {inviter.get('avatar', 'None')}\n"
            info_text += f"\nServer ID: {invite_data['guild']['id']}\n"
            self.type_out_text(info_text, 10)
        except requests.RequestException as e:
            if response.status_code == 429:  # Rate limited
                retry_after = response.headers.get("Retry-After", "Unknown")
                self.info_text.setPlainText(f"Rate limited. Please try again after {retry_after} seconds.")
            else:
                self.info_text.setPlainText(f"Failed to fetch invite information: {str(e)}")
        finally:
            self.loading_widget.hide()

    def fetch_multiple_invite_info(self):
        invite_inputs = self.invite_list_entry.text().strip().split()
        invite_codes = [self.extract_invite_code(invite.strip()) for invite in invite_inputs if self.extract_invite_code(invite.strip())]

        if not invite_codes:
            self.info_text.setPlainText("Please enter valid invite links or codes.")
            return

        self.info_text.clear()
        self.loading_widget.show()
        QApplication.processEvents()  # Ensure the loading widget is shown

        for invite_code in invite_codes:
            url = f"https://discord.com/api/v8/invites/{invite_code}?with_counts=true"
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                invite_data = response.json()

                info_text = f"Guild Name: {invite_data['guild']['name']}\n"
                info_text += f"Guild Members: {invite_data['approximate_member_count']}\n"
                info_text += f"Online Members: {invite_data['approximate_presence_count']}\n"
                info_text += "\nInviter Details:\n"
                inviter = invite_data.get('inviter', {})
                info_text += f"ID: {inviter.get('id', 'None')}\n"
                info_text += f"Username: {inviter.get('username', 'None')}\n"
                info_text += f"Discriminator: {inviter.get('discriminator', 'None')}\n"
                info_text += f"Avatar: {inviter.get('avatar', 'None')}\n"
                info_text += f"\nServer ID: {invite_data['guild']['id']}\n"
                info_text += "----------------------------------------\n"
                self.type_out_text(info_text, 1)
            except requests.RequestException as e:
                if response.status_code == 429:  # Rate limited
                    retry_after = response.headers.get("Retry-After", "Unknown")
                    self.info_text.setPlainText(f"Rate limited. Please try again after {retry_after} seconds.")
                else:
                    self.info_text.setPlainText(f"Failed to fetch invite information: {str(e)}")
        self.loading_widget.hide()

    def extract_invite_code(self, invite_input):
        pattern = r"(?:https?:\/\/)?(?:www\.)?(?:discord(?:\.gg|\.com\/invite)\/)?([a-zA-Z0-9]+)"
        match = re.search(pattern, invite_input)
        if match:
            return match.group(1)
        return None

    def type_out_text(self, text, delay):
        self.info_text.moveCursor(self.info_text.textCursor().End)
        self.info_text.insertPlainText(text)
        self.index = 0
        self.text = text
        self.timer = QTimer()
        self.timer.timeout.connect(self.insert_character)
        self.timer.start(delay)  # Adjust the delay here (in milliseconds)

    def insert_character(self):
        if self.index < len(self.text):
            self.info_text.moveCursor(self.info_text.textCursor().End)
            self.info_text.insertPlainText(self.text[self.index])
            self.index += 1
        else:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
