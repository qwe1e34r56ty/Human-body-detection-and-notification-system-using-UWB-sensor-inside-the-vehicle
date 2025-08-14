# -*- coding: euc-kr -*-
import sys;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *
from getExternalFont import *;

class LoadingTextLabel(QLabel):
	def __init__(self, text):
		super().__init__();
		self.index = 0;
		self.text = text;
		self.setText(self.text);	
		self.setFont(getExternalFont());
		self.setStyleSheet("background-color: #00060D; font-size:48px; color: #FFFFFF; ");
		self.setAlignment(Qt.AlignCenter);
		self.timer = QTimer(self);

	def updateText(self):
		tmp = "";
		for i in range(0, self.index):
			tmp += ".";
		super().setText(self.text + tmp);
		self.index += 1;
		self.index %= 5;

	def setText(self, text):
		super().setText(text);
		self.text = text;

	def stopCount(self):
		self.timer.stop();

	def resetCount(self):
		self.index = 0;

	def startCount(self):
		self.timer.timeout.connect(self.updateText);
		self.timer.start(200);

if __name__ == "__main__":
	app = QApplication(sys.argv)
	loadingTextLabel = LoadingTextLabel("main");
	loadingTextLabel.show();
	sys.exit(app.exec_())