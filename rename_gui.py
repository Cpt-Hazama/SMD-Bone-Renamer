import os
import re
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QScrollArea, QGroupBox, QVBoxLayout, QTextEdit


class BoneReplacerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SMD Bone Replacer")
        self.setGeometry(100, 100, 800, 600)

        label = QLabel(
            "Select the SMDs you want to change, then the TXT file containing the replacement mapping.")
        self.button_select_smd = QPushButton("Select SMD Files")
        self.button_select_smd.clicked.connect(self.open_smd_file_dialog)

        self.button_select_txt = QPushButton("Select TXT File")
        self.button_select_txt.clicked.connect(self.open_txt_file_dialog)

        self.file_paths_box_smd = QTextEdit()
        self.file_paths_box_smd.setReadOnly(True)
        scroll_area_smd = QScrollArea()
        scroll_area_smd.setWidgetResizable(True)
        scroll_area_smd.setWidget(self.file_paths_box_smd)

        self.file_path_txt = QTextEdit()
        self.file_path_txt.setReadOnly(True)
        scroll_area_txt = QScrollArea()
        scroll_area_txt.setWidgetResizable(True)
        scroll_area_txt.setWidget(self.file_path_txt)

        self.button_replace = QPushButton("Replace Bones")
        self.button_replace.setEnabled(False)
        self.button_replace.clicked.connect(self.process_smd_files)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.button_select_smd)
        layout.addWidget(scroll_area_smd)
        layout.addWidget(self.button_select_txt)
        layout.addWidget(scroll_area_txt)
        layout.addWidget(self.button_replace)

        self.setLayout(layout)

        self.smd_file_paths = []
        self.txt_file_path = ''

    def open_smd_file_dialog(self):
        # Show SMD file selection dialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("SMD Files (*.smd *.SMD)")
        # Set current directory of script file
        file_dialog.setDirectory(os.path.dirname(os.path.abspath(__file__)))
        if file_dialog.exec_():
            self.smd_file_paths = file_dialog.selectedFiles()
            self.file_paths_box_smd.setPlainText(
                '\n'.join(self.smd_file_paths))
            if self.smd_file_paths and self.txt_file_path:
                self.button_replace.setEnabled(True)
        else:
            self.smd_file_paths = []

    def open_txt_file_dialog(self):
        # Show TXT file selection dialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt *.TXT)")
        # Set current directory of script file
        file_dialog.setDirectory(os.path.dirname(os.path.abspath(__file__)))
        if file_dialog.exec_():
            self.txt_file_path = file_dialog.selectedFiles()[0]
            self.file_path_txt.setPlainText(self.txt_file_path)
            if self.smd_file_paths and self.txt_file_path:
                self.button_replace.setEnabled(True)
        else:
            self.txt_file_path = ''

    def process_smd_files(self):
        total_time_start = time.time()

        # Use self.smd_file_paths and self.txt_file_path instead of passing as argument
        file_paths = self.smd_file_paths
        txt_file_path = self.txt_file_path

        for file_path in file_paths:
            filename = os.path.basename(file_path)
            file_time_start = time.time()
            with open(file_path, 'r') as f:
                lines = f.readlines()

            start_index = None
            end_index = None
            for i, line in enumerate(lines):
                if line.strip() == 'nodes':
                    start_index = i
                elif line.strip() == 'end':
                    end_index = i
                    break

            if start_index is not None and end_index is not None:
                with open(txt_file_path, 'r') as f:
                    bone_replacements = {}
                    for line in f:
                        line = line.strip()
                        if line:
                            old_bone, new_bone = map(
                                str.strip, line.split('='))
                            bone_replacements[old_bone] = new_bone

                for i in range(start_index + 1, end_index):
                    for old_bone, new_bone in bone_replacements.items():
                        if old_bone in lines[i]:
                            lines[i] = lines[i].replace(old_bone, new_bone)
                            print('Replaced', old_bone, 'with', new_bone,)

                with open(file_path, 'w') as f:
                    f.writelines(lines)

                file_time_end = time.time()
                file_time_elapsed = file_time_end - file_time_start
                print('Bone names replaced in file:', filename)
                print('Time elapsed for', filename,
                      ':', file_time_elapsed, 'seconds')
            else:
                print('Error: Failed to find bone names section in file:', filename)

        total_time_end = time.time()
        total_time_elapsed = total_time_end - total_time_start
        print('Total processing time for all SMD files:',
              total_time_elapsed, 'seconds')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BoneReplacerApp()
    window.show()
    sys.exit(app.exec_())
