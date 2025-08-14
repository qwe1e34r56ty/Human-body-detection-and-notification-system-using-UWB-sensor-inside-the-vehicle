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
from getExternalFont import *;

class RequestScreen(QWidget):
	requestWork = pyqtSignal(int);
	def __init__(self, serverConnect):
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
		self.backButton.clicked.connect(lambda: self.requestWork.emit(constants.MENU_PAGE));
		self.navBarLayout.addWidget(self.backButton);

		self.homeTextLabel = QLabel(self);
		self.homeTextLabel.setText("CERT REQUEST");
		self.homeTextLabel.setStyleSheet("font-size:72px; color: #FFFFFF; ");
		self.navBarLayout.addWidget(self.homeTextLabel);


		self.navBarLayout.addStretch();
		self.navBarWidget.setLayout(self.navBarLayout);
		self.navBarWidget.setFixedHeight(120);	
		self.layout.addWidget(self.navBarWidget);

		#self.acceptGuideLabel = QLabel(constants.ACCEPT_GUIDE_TEXT);
		#self.layout.addWidget(self.acceptGuideLabel);
		#self.acceptGuideLabel.setStyleSheet("font-size:36px;");

		self.listView = QListView();
		self.layout.addWidget(self.listView);
		self.model = QStringListModel();
		self.listView.setModel(self.model);
		self.listView.setStyleSheet("font-size:60px; background-color: #FFFFFF; ");
		self.selectedRequest = None;

		self.deleteButton = QPushButton(constants.DELETE_TEXT);
		self.deleteButton.setStyleSheet("font-size:60px;");
		self.deleteButton.clicked.connect(self.deleteButtonClicked);
		#self.layout.addWidget(self.deleteButton);

		self.addressLabel = QLabel("식별 ID : " + netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']);
		self.addressLabel.setFont(getExternalFont());
		self.addressLabel.setStyleSheet("font-size:60px; color:#FFFFFF");
		self.addressLabel.setFixedHeight(100);
		self.layout.addWidget(self.addressLabel);

		self.requestList = [];
	
	def getSelectedRequestIndex(self):
		if len(self.requestList) == 0:
			return -1;
		selectedIndex = self.listView.selectedIndexes();
		if selectedIndex:
			index = selectedIndex[0].row();
			print(self.requestList);
			print(index)
			return index;
		else :
			return -1;

	def openHomeScreen(self):
		self.reqeustWork.emit();

	def setItems(self, items):
		self.model.setStringList(items);

	def addRequest(self, client, userData, message):
		recvMsg = message.payload.decode('utf-8');
		print("Received message:", recvMsg);
		items = recvMsg.strip("{}").split(", ");
		data = {};
		for item in items:
			key, value = item.split("=");
			data[key.strip()] = value.strip();
		if items[0][0] == 'r' :
			request = data["request"];
			if request == "open" or request == "close" :
				print(f"window {request} request received");
				return;
		id = data["id"];
		code = data["code"];
		string = "   " + constants.CONNECT_REQUEST_USER_ID_TEXT + " : " + id + "\n" + "   " + constants.CODE_TEXT + " : " + code;
		print(string);
		self.requestList.append(string);
		self.setItems(self.requestList);
	
	def deleteButtonClicked(self):
		selectedIndex = self.getSelectedRequestIndex();
		if selectedIndex == -1 :
			return;
		self.selectedRequest =  self.requestList[selectedIndex];
		print(self.selectedRequest[0]);
		self.requestList.pop(selectedIndex);
		self.setItems(self.requestList);

if __name__ ==  '__main__':
	app = QApplication(sys.argv)
	requestScreen = RequestScreen(ServerConnect());
	requestScreen.show();
	sys.exit(app.exec_())