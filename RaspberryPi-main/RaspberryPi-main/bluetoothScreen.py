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
from acceptDialog import *;
from getExternalFont import *;

class BluetoothScreen(QWidget):
	requestWork = pyqtSignal(int);
	def __init__(self,  obd2ClientService):
		super().__init__();
		self.devices = [];
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
		self.backButton.clicked.connect(lambda: self.requestWork.emit(constants.MENU_PAGE));
		self.navBarLayout.addWidget(self.backButton);

		self.homeTextLabel = QLabel(self);
		self.homeTextLabel.setText("OBD CONNECT");
		self.homeTextLabel.setStyleSheet("font-size:72px; color: #FFFFFF; ");
		self.navBarLayout.addWidget(self.homeTextLabel);


		self.navBarLayout.addStretch();
		self.navBarWidget.setLayout(self.navBarLayout);
		self.navBarWidget.setFixedHeight(120);	
		self.layout.addWidget(self.navBarWidget);

		#self.bluetoothGuideLabel = QLabel(constants.BLUETOOTH_GUIDE_TEXT);
		#self.layout.addWidget(self.bluetoothGuideLabel);
		#self.bluetoothGuideLabel.setStyleSheet("font-size:36px;");
		self.obd2ClientService = obd2ClientService;

		self.listView = QListView();
		self.layout.addWidget(self.listView);
		self.model = QStringListModel();
		self.listView.setModel(self.model);
		self.listView.setStyleSheet("font-size:48px; background-color: #FFFFFF;");
		self.selectedDevice = None;

		self.buttonLayout = QHBoxLayout();
		self.connectButton = QPushButton(constants.BLUETOOTH_CONNECT_TEXT, self);
		self.scanButton = QPushButton(constants.BLUETOOTH_SCAN_TEXT, self);

		self.buttonLayout.addWidget(self.connectButton);
		self.connectButton.setStyleSheet("font-size:60px; color:#FFFFFF; border: 1px solid transparent;");
		self.connectButton.clicked.connect(self.connectButtonClicked);
		self.connectButton.setFont(getExternalFont());
		self.connectButton.setFixedHeight(100);

		self.buttonLayout.addWidget(self.scanButton);
		self.scanButton.setStyleSheet("font-size:60px; color:#FFFFFF; border: 1px solid transparent;");
		self.scanButton.clicked.connect(self.scanButtonClicked);
		self.scanButton.setFont(getExternalFont());
		self.scanButton.setFixedHeight(100);

		self.layout.addLayout(self.buttonLayout);

		self.stateLabel = QLabel();
		self.layout.addWidget(self.stateLabel);
		self.setLayout(self.layout);

	def setItems(self, items):
		self.model.setStringList(items);

	def showEvent(self,event):
		super().showEvent(event);

	def scanButtonClicked(self, event):			
		self.connectButton.setEnabled(False);
		self.connectButton.setStyleSheet("font-size:60px; color:#gray; border: 1px solid transparent;");
		self.connectButton.update();

		self.scanButton.setEnabled(False);
		self.scanButton.setStyleSheet("font-size:60px; color:#gray; border: 1px solid transparent;");
		self.scanButton.update();

		QApplication.processEvents();

		self.devices = self.obd2ClientService.scanDevices();
		self.connectButton.setEnabled(True);
		self.connectButton.setStyleSheet("font-size:60px; color:#FFFFFF; border: 1px solid transparent;");
		self.scanButton.setEnabled(True);
		self.scanButton.setStyleSheet("font-size:60px; color:#FFFFFF; border: 1px solid transparent;");

		print("scan 종료");
		tmp = [];
		for addr, name, _ in self.devices :
			tmp.append("   " + name + " : " + addr);
		if len(self.devices) == 0 :
			tmp.append("검색된 장치가 없습니다.");
		self.setItems(tmp);
	
	def connectButtonClicked(self, event):
		index, self.selectedDevice = self.getSelectedDevice();
		if self.selectedDevice == None :
			#dialog = AcceptDialog("선택된 장치가 없습니다");
			#dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
			#dialog.exec_();
			return;
		print(self.selectedDevice[0]);
		print(constants.BLUETOOTH_PORT);
		self.obd2ClientService.makeConnect(self.selectedDevice[1], self.selectedDevice[0], constants.BLUETOOTH_PORT);
		if self.obd2ClientService.isConnected():
			current_text = index.data(Qt.DisplayRole);
			self.model.setData(index, current_text + "\t\t - 연결 성공", Qt.DisplayRole)
			#dialog = AcceptDialog("장치 연결 성공");
			#dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
			#dialog.exec_();
		else:
			current_text = index.data(Qt.DisplayRole);
			self.model.setData(index, current_text + "\t\t - 연결 실패", Qt.DisplayRole)
			#dialog = AcceptDialog("장치 연결 실패");
			#dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
			#dialog.exec_();
		pass;

	def getSelectedDevice(self):
		if len(self.devices) == 0:
			return None;
		selectedIndex = self.listView.selectedIndexes();
		if selectedIndex:
			index = selectedIndex[0].row();
			print(self.devices);
			print(index);
			return selectedIndex[0],[self.devices[index][0], self.devices[index][1]];
		else :
			return None, None;

if __name__ == "__main__" :
	app = QApplication(sys.argv)
	bluetoothScreen = BluetoothScreen(Obd2ClientService());
	bluetoothScreen.show()
	sys.exit(app.exec_());