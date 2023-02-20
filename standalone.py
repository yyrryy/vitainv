from PyQt5.QtCore import QProcess, QThread, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import QUrl

# class ServerThread(QThread):
#     def run(self):
#         process = QProcess()
#         process.startDetached("python manage.py runserver")

app = QApplication([])

# Create a label to display the message
label = QLabel("Loading...", alignment=Qt.AlignCenter)
label.setStyleSheet("font-size: 30px;") # you can adjust the font size as per your requirement
label.show()

# Start the Django development server in a separate thread
# server_thread = ServerThread()
# server_thread.start()

# Wait for the server to start
import time
time.sleep(3)

web_view = QWebEngineView()
web_view.load(QUrl("http://localhost:8000"))
web_view.show()

# Hide the label when the server is started
label.hide()

app.exec_()
