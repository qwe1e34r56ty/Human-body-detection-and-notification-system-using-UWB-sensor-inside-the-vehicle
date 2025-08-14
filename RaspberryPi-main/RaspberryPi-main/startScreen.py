# -*- coding: euc-kr -*-
import sys;
import constants;
from serverConnect import *;
from loadingTextLabel import *;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
from time import sleep;
from acceptDialog import *;
from PyQt5.QtGui import QPixmap

class StartScreen(QWidget):
	requestWork = pyqtSignal(int);
	def __init__(self, serverConnect):
		super().__init__();
		self.layout = QVBoxLayout();
		self.loadingTextLabel = LoadingTextLabel(constants.SERVER_CONNECT_LOADING_TEXT);

		self.timer = QTimer(self);
		self.serverConnect = serverConnect;
		self.setLayout(self.layout);

	def showEvent(self, event):
		super().showEvent(event);
		self.layout.addWidget(self.loadingTextLabel);
		self.loadingTextLabel.startCount();		
		# 진행 과정을 보여주기 위해 실제 서버 연결에 약간 딜레이를 두고 실행
		self.timer.timeout.connect(self.delayedConnect);
		self.timer.start(4000);

	def delayedConnect(self):
		self.timer.stop();
		self.timer.disconnect();

		while self.serverConnect.connectConfirm() == False:
			self.loadingTextLabel.resetCount();
			self.loadingTextLabel.stopCount();
			self.loadingTextLabel.setText(constants.SERVER_CONNECT_DELAYED_TEXT);
			self.loadingTextLabel.startCount();

		self.loadingTextLabel.resetCount();
		self.loadingTextLabel.stopCount();
		self.loadingTextLabel.setText(constants.SERVER_CONNECT_SUCCEED_TEXT);
		self.timer.timeout.connect(self.openHomePage);
		self.timer.start(2000);
		
	def openHomePage(self):
		self.timer.stop();
		self.requestWork.emit(constants.HOME_PAGE)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	startScreen = StartScreen();
	startScreen.show();
	sys.exit(app.exec_())