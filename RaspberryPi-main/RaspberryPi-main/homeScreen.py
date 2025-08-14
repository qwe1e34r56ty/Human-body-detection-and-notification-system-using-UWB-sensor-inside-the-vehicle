# -*- coding: euc-kr -*-
import sys;
import constants;
from obd2ClientService import *;
from serverConnect import *;
from loadingTextLabel import *;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
from time import sleep;
from obd2ClientService import *;
from acceptDialog import *;
from cnn.binaryPredictor import *;
from cnn.loadCirFtDataSet import *;
from getPoint import *;
from stateLabel import *;
import math;
from getExternalFont import *;
from imageTextLabel import *;
from datetime import datetime;

class HomeScreen(QWidget):
	requestWork = pyqtSignal(int);
	def __init__(self, obd2ClientService, serverConnect, getUwbData, modelPath):
		super().__init__();
		self.layout = QVBoxLayout();
		self.layout.setSpacing(0);
		self.layout.setContentsMargins(30, 30, 30, 30);	
		self.setLayout(self.layout);

		self.navBarWidget = QWidget();
		self.navBarLayout = QHBoxLayout();
		self.menuLabel = QLabel(self);
		self.menuLabel.setPixmap(QPixmap("./image/menu.png").scaled(80, 80));
		self.menuLabel.setFixedSize(100, 100);
		self.navBarLayout.addWidget(self.menuLabel);
		self.menuLabel.mousePressEvent = lambda event : self.requestWork.emit(constants.MENU_PAGE);

		self.menuTextLabel = QLabel(self);
		self.menuTextLabel.setText("HOME");
		self.menuTextLabel.setStyleSheet("font-size:72px; color: #FFFFFF; ");
		self.navBarLayout.addWidget(self.menuTextLabel);
		#self.menuTextLabel.mousePressEvent = lambda event: self.requestWork.emit(constants.MENU_PAGE);

		self.navBarLayout.addStretch(1);
		self.timeTextLabel = QLabel(self);
		self.timeTextLabel.setText(self.getHHMMDateString());
		self.timeTextLabel.setStyleSheet("font-size:72px; color: #FFFFFF; ");
		self.navBarLayout.addWidget(self.timeTextLabel);

		self.navBarLayout.addStretch();
		self.navBarWidget.setLayout(self.navBarLayout);
		self.navBarWidget.setFixedHeight(120);
		self.navBarWidget.setStyleSheet("background-color: #00060D; border: 1px solid transparent;");
		self.layout.addWidget(self.navBarWidget);

		mainBodyWidget = QWidget();
		self.gridLayout = QGridLayout();

		mainBodyWidget.setLayout(self.gridLayout);
		mainBodyWidget.setStyleSheet("background-color: #011C26; border: 1px solid transparent; border-radius: 50px;");
		self.mainBodyWidget = mainBodyWidget;
		self.layout.addWidget(self.mainBodyWidget);

		self.networkStateLabel = stateLabel("서버", "./image/network_disconnected.png", "연결되지 않음");
		self.carStateLabel = stateLabel("차량", "./image/car_disconnected.png", "연결되지 않음");
		self.uwbStateLabel = stateLabel("감지 센서", "./image/sensor_connected.png", "연결됨");

		self.gridLayout.addWidget(self.networkStateLabel, 0, 0);
		self.gridLayout.addWidget(self.carStateLabel, 0, 1);
		self.gridLayout.addWidget(self.uwbStateLabel, 0, 2);
		
		self.loadingTextLabel = LoadingTextLabel(constants.SERVER_CONNECT_LOADING_TEXT);
		self.obd2ClientService = obd2ClientService;
		self.pred = BinaryPredictor(modelPath);

		self.serverConnect = serverConnect;
		self.getUwbData = getUwbData;

		self.bluetoothButton = QPushButton(constants.BLUETOOTH_PAGE_BUTTON_TEXT);
		self.bluetoothButton.setFont(getExternalFont());
		self.bluetoothButton.setStyleSheet("font-size:36px; color: #FFFFFF; ");
		self.bluetoothButton.clicked.connect(lambda: self.requestWork.emit(constants.BLUETOOTH_PAGE));

		self.requestButton = QPushButton(constants.REQUEST_PAGE_BUTTON_TEXT);
		self.requestButton.setFont(getExternalFont());
		self.requestButton.setStyleSheet("font-size:36px; color: #FFFFFF; ");
		self.requestButton.clicked.connect(lambda: self.requestWork.emit(constants.REQUEST_PAGE));

		self.testServerConnectButton = QPushButton(constants.SERVER_CONNECT_CHECK_BUTTON_TEXT);
		self.testServerConnectButton.setFont(getExternalFont());
		self.testServerConnectButton.setStyleSheet("font-size:36px; color: #FFFFFF; ");
		self.testServerConnectButton.clicked.connect(self.testServerConnect);
		#self.layout.addWidget(self.testServerConnectButton);

		#self.layout.addWidget(self.bluetoothButton);
		#self.layout.addWidget(self.requestButton);

		self.connectedLabel = QLabel("");
		self.connectedLabel.setStyleSheet("font-size:36px;");
		#self.layout.addWidget(self.connectedLabel);

		self.carStartLabel = QLabel(f"{constants.CAR_START_TEXT} : ");
		self.carStartLabel.setStyleSheet("font-size:36px;");
		#self.layout.addWidget(self.carStartLabel);

		self.vehicleSpeedLabel = QLabel(f"{constants.VEHICLE_SPEED_TEXT} : ");
		self.vehicleSpeedLabel.setStyleSheet("font-size:36px;");
		#self.layout.addWidget(self.vehicleSpeedLabel);

		self.doorLockLabel = QLabel(f"{constants.DOOR_LOCK_TEXT} : ");
		self.doorLockLabel.setStyleSheet("font-size:36px;");
		#self.layout.addWidget(self.doorLockLabel);

		self.warningLabel = QLabel(f"{constants.WARNING_TEXT} : ");
		self.warningLabel.setStyleSheet("font-size:36px;");
		#self.layout.addWidget(self.warningLabel);

		self.uwbLabel = QLabel(f"{constants.UWB_TEXT} : ");
		self.uwbLabel.setStyleSheet("font-size:36px;");
		#self.layout.addWidget(self.uwbLabel);


		self.updateTimer = QTimer(self);
		self.updateTimer.timeout.connect(self.update);
		self.updateTimer.start(100);

		self.updateCount = 0;	
		self.failedDialogExist = False;

		self.detectQueue = [1] * 25;

	def testServerConnect(self):
		if self.serverConnect.connectConfirm() :
			AcceptDialog("success").exec_();
		else :
			AcceptDialog("fail").exec_();
	def update(self):
		self.updateCount += 1;
		self.timeTextLabel.setText(self.getHHMMDateString());
		if self.serverConnect.connectConfirm() :
			self.networkStateLabel.setBottomText("연결됨");
			self.networkStateLabel.setImage( "./image/network_connected.png");
		else :
			self.networkStateLabel.setBottomText("연결되지 않음");
			self.networkStateLabel.setImage( "./image/network_disconnected.png");
		if self.obd2ClientService.isConnected() :
			self.carStateLabel.setBottomText("연결됨");
			self.carStateLabel.setImage( "./image/car_connected.png");
		else :
			self.carStateLabel.setBottomText("연결되지 않음");
			self.carStateLabel.setImage( "./image/car_disconnected.png");

		if self.updateCount * constants.SENSOR_GET_DATA_CYCLE > constants.SEND_LOG_CYCLE :
			if self.obd2ClientService.isConnected() :
				self.connectedLabel.setText(constants.OBD2_CONNECTED_TEXT);

				self.carStart = None;
				try:
					self.carStart = self.obd2ClientService.getCarStart();
				except Exception as e:
					print(f"Recv Failed : {e}");
					return;
	
				self.vehicleSpeed = 0;
				try:
					self.vehicleSpeed = self.obd2ClientService.getVehicleSpeed();
				except Exception as e:
					print(f"Recv Failed : {e}");
					return;

				self.doorLock = None;
				try:
					self.doorLock = self.obd2ClientService.getDoorLock();
				except Exception as e:
					print(f"Recv Failed : {e}");
					return;
			
				self.carStartLabel.setText(f"{constants.CAR_START_TEXT} : {self.carStart}");
				self.vehicleSpeedLabel.setText(f"{constants.VEHICLE_SPEED_TEXT} : {self.vehicleSpeed}");
				self.doorLockLabel.setText(f"{constants.DOOR_LOCK_TEXT} : {self.doorLock}");
			else :
				self.connectedLabel.setText(constants.OBD2_NOT_CONNECTED_TEXT);

			self.humanDetected = self.isHumanDetected();
			self.uwbLabel.setText(f"{constants.UWB_TEXT} : {self.humanDetected}");
			warningDetailText = "";
			if self.serverConnect.sendLog(int(0), int(1), int(self.humanDetected), 0, 1) :
				print("send log Succeed");
			else :
				print("send log Failed");
			if self.getUwbData() != [] and self.serverConnect.sendCir(self.getUwbData()) :
				print("send Cir Succeed");
			else :
				print("send Cir Failed");
			ltit, lgit = getPoint();
			if ltit != 0 and lgit != 0 :
				if self.serverConnect.sentPoint(ltit, lgit) :
					print("send Point Succeed");
				else :
					print("send Point Failed");
			else :
				print("get Point Failed");
			self.updateCount = 0;
			pass;

	def predict(self):
		tmp = self.getUwbData();
		if len(tmp) < 2 :
			return;
		merge = tmp[0] + tmp[1];
		ret = self.pred.predict(merge);
		print(ret);
		return ret;

	def showEvent(self, event):
		self.update();

	def isHumanDetected(self):
		self.detectQueue.append(self.predict());
		if len(self.detectQueue) > 25 :
			self.detectQueue.pop(0);
		print(self.detectQueue.count(0));
		if len(self.detectQueue) == 25 and self.detectQueue.count(0) >= 20:
			return True;
		return False;
	
	def warningNumber(self):
		if int(self.carStart) ==0 and int(self.doorLock) == 1 and self.isHumanDetected() :
			return 1;
		return 0;

	def setUwbData(self, uwbData):
		self.uwbData = uwbData;

	def getHHMMDateString(self):
		return datetime.now().strftime("%H:%M:%S");

if __name__ == '__main__':
	app = QApplication(sys.argv)
	homeScreen = HomeScreen(Obd2ClientService(), ServerConnect(), lambda : 0);
	homeScreen.show();
	sys.exit(app.exec_())