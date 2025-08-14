# -*- coding: euc-kr -*-
import sys;
import constants;
from obd2ClientService import *;
from serverConnect import *;
from loadingTextLabel import *;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
from  PyQt5.QtGui import *;
from time import sleep;

class AcceptDialog(QDialog):
	def __init__(self, text):
		super().__init__();
		self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
		self.setStyleSheet("border: 1px solid black;");
		layout = QVBoxLayout();
		label = QLabel(text);
		label.setStyleSheet("font-size:36px; border: none;");

		button = QPushButton("확인")
		button.setStyleSheet("font-size:36px;");
		button.clicked.connect(self.accept)
		layout.addWidget(label);
		layout.addWidget(button);
		self.setLayout(layout);

	def resizeEvent(self, event):
		width = QDesktopWidget().screenGeometry().width();
		height = QDesktopWidget().screenGeometry().height();
		self.resize(width * 0.2, height * 0.2);

if __name__ == "__main__" :
	app = QApplication(sys.argv)
	sys.exit(AcceptDialog("테스트").exec_());
