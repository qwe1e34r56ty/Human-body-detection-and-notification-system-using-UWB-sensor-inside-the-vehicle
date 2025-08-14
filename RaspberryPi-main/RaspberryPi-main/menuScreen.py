# -*- coding: euc-kr -*-
import sys;
import constants;
from serverConnect import *;
from obd2ClientService import *;
from startScreen import *;
from bluetoothScreen import *;
from homeScreen import *;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
import netifaces;
from menuGridLabel import *;
from datetime import datetime;


class MenuScreen(QWidget):
	requestWork = pyqtSignal(int);
	def __init__(self):
		super().__init__();
		self.layout = QVBoxLayout();
		self.layout.setSpacing(0);
		self.layout.setContentsMargins(30, 30, 30, 30);	
		self.setLayout(self.layout);

		self.navBarWidget = QWidget();
		self.navBarLayout = QHBoxLayout();

		self.backIcon = QIcon("./image/back.png");
		self.backButton = QPushButton(self);
		self.backButton.setIcon(self.backIcon);
		self.backButton.setIconSize(QSize(100, 100));
		self.backButton.setStyleSheet("border: none;");	
		self.backButton.clicked.connect(lambda: self.requestWork.emit(constants.HOME_PAGE));
		self.navBarLayout.addWidget(self.backButton);

		self.homeTextLabel = QLabel(self);
		self.homeTextLabel.setText("MENU");
		self.homeTextLabel.setStyleSheet("font-size:72px; color: #FFFFFF; ");
		self.navBarLayout.addWidget(self.homeTextLabel);
		#self.homeTextLabel.mousePressEvent = lambda event: self.requestWork.emit(constants.HOME_PAGE);

		#self.navBarLayout.addStretch(1);
		#self.timeTextLabel = QLabel(self);
		#self.timeTextLabel.setText(self.getHHMMDateString());
		#self.timeTextLabel.setStyleSheet("font-size:72px; color: #FFFFFF; ");
		#self.navBarLayout.addWidget(self.timeTextLabel);

		self.navBarLayout.addStretch();
		self.navBarWidget.setLayout(self.navBarLayout);
		self.navBarWidget.setFixedHeight(120);	
		self.layout.addWidget(self.navBarWidget);

		mainBodyWidget = QWidget();
		self.gridLayout = QGridLayout();

		self.columns = 5;
		self.rows = 2;

		self.gridLabelList = [[], []];
		for row in range(self.rows):
			for col in range(self.columns):
				self.gridLabelList[row].append(QLabel());
		self.gridLabelList[0][0] = MenuGridLabel(f'인증 요청', "./image/cert.png");
		self.gridLabelList[0][0].mousePressEvent = lambda event: self.requestWork.emit(constants.REQUEST_PAGE);
		self.gridLabelList[0][1] = MenuGridLabel(f'OBD 연결', "./image/obd.png");
		self.gridLabelList[0][1].mousePressEvent = lambda event: self.requestWork.emit(constants.BLUETOOTH_PAGE);

		for row in range(self.rows):
			for col in range(self.columns):
				self.gridLayout.addWidget(self.gridLabelList[row][col], row, col);

		mainBodyWidget.setLayout(self.gridLayout);
		mainBodyWidget.setStyleSheet("background-color: #011C26; border: 1px solid transparent; border-radius: 50px;");
		self.mainBodyWidget = mainBodyWidget;
		self.layout.addWidget(self.mainBodyWidget);


	def openHomeScreen(self):
		self.reqeustWork.emit();

	def getHHMMDateString(self):
		return datetime.now().strftime("%H:%M");


if __name__ ==  '__main__':
	app = QApplication(sys.argv)
	requestScreen = MenuScreen();
	requestScreen.show();
	sys.exit(app.exec_())