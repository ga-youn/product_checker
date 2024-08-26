import os
import sys
import subprocess
import threading
import time
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit

class ScrapyGUI(QWidget):
    log_signal = pyqtSignal(str)
    update_timer_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_running = False
        self.auto_run = False
        self.log_signal.connect(self.append_log)
        self.update_timer_signal.connect(self.update_timer)

        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self._enable_run_button)
        self.timer.setInterval(1000)  # Timer updates every 1 second

    def initUI(self):
        self.run_button = QPushButton('Run Spider', self)
        self.run_button.clicked.connect(self.run_spider)

        self.auto_button = QPushButton('Start Auto Run (10 min)', self)
        self.auto_button.clicked.connect(self.toggle_auto_run)

        self.status_label = QLabel('Status: 시작전', self)
        self.timer_label = QLabel('Time until next run: N/A', self)

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.run_button)
        vbox.addWidget(self.auto_button)
        vbox.addWidget(self.status_label)
        vbox.addWidget(self.timer_label)
        vbox.addWidget(self.log_text)

        self.setLayout(vbox)
        self.setWindowTitle('Scrapy Spider Controller')
        self.setGeometry(300, 300, 600, 400)

    def run_spider(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.setText('Status: 진행중')
            self.run_button.setEnabled(False)  # Disable button

            project_path = r"C:\Users\gyym9\product_checker"
            output_file = os.path.join(project_path, 'output.json')

            # Start the Scrapy process
            self._start_scrapy_process(project_path, output_file)
        else:
            self.append_log("Spider is already running.")

    def _start_scrapy_process(self, project_path, output_file):
        try:
            command = ['scrapy', 'crawl', 'product_spider', '-o', output_file]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=project_path,
                bufsize=1,  # Line buffering
                universal_newlines=True
            )

            threading.Thread(target=self._read_process_output, args=(process.stdout,)).start()
            threading.Thread(target=self._read_process_output, args=(process.stderr, True)).start()

            process.wait()
            self._on_spider_finished()

        except Exception as e:
            self.log_signal.emit(f"Error: {e}")
            self._on_spider_finished()

    def _read_process_output(self, pipe, is_error=False):
        try:
            for line in iter(pipe.readline, ''):
                if line.strip():
                    self.log_signal.emit(line.strip())
        except Exception as e:
            self.log_signal.emit(f"Error while reading output: {e}")
        finally:
            pipe.close()

    def _on_spider_finished(self):
        self.is_running = False
        self.status_label.setText('Status: 완료')
        self._start_countdown(30)  # Start countdown for button re-enable

    def _start_countdown(self, seconds):
        self.remaining_time = seconds
        self.update_timer_signal.emit(self.remaining_time)  # Update UI with the initial time
        self.timer.start()  # Start the timer

    def _enable_run_button(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_timer_signal.emit(self.remaining_time)
        else:
            self.timer.stop()
            self.run_button.setEnabled(True)  # Re-enable button

    def toggle_auto_run(self):
        if self.auto_run:
            self.auto_run = False
            self.auto_button.setText('Start Auto Run (10 min)')
            self.timer.stop()  # Stop auto run
            self.timer_label.setText('Time until next run: N/A')
        else:
            self.auto_run = True
            self.auto_button.setText('Stop Auto Run')
            threading.Thread(target=self._auto_run_spider).start()

    def _auto_run_spider(self):
        while self.auto_run:
            if not self.is_running:
                self.run_spider()
            time.sleep(600)  # Run every 10 minutes

    def update_timer(self, remaining_time):
        self.timer_label.setText(f'Time until next run: {remaining_time} seconds')

    def append_log(self, message):
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ScrapyGUI()
    gui.show()
    sys.exit(app.exec_())
