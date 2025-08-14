# -*- coding: euc-kr -*-
import sys;
import constants;
from obd2ClientService import *;
from startScreen import *;
from bluetoothScreen import *;
from homeScreen import *;
from requestScreen import *;
from menuScreen import *;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
import paho.mqtt.client as mqtt;
import serial;
import threading;
import numpy as np;
import math;
import struct;

class Main(QMainWindow):
	def __init__(self, serialDirList, modelPath):
		super().__init__();
		self.obd2ClientService = Obd2ClientService();
		self.serverConnect = ServerConnect();
		self.setWindowState(Qt.WindowFullScreen)
		self.setWindowTitle("FullScreen");

		self.serialList = [];
		self.serialDirList = [];
		self.serialErrorList = [];
		for dir in serialDirList:
			self.appendSerial(dir);
				
		self.running = True;
		self.task = threading.Thread(target=self.uwbRecvTask);
		self.task.start();
		self.lock = threading.Lock();

		self.uwbData = [];

		self.widgetList = [];
		self.stack = QStackedWidget();
		self.stack.setStyleSheet("background-color: #00060D;");
		self.setCentralWidget(self.stack);

		self.widgetList.append(StartScreen(self.serverConnect));
		self.widgetList.append(HomeScreen(self.obd2ClientService, self.serverConnect, self.getUwbData, modelPath));
		self.widgetList.append(RequestScreen(self.serverConnect));
		self.widgetList.append(BluetoothScreen(self.obd2ClientService));
		self.widgetList.append(MenuScreen());

		self.stack.addWidget(self.widgetList[constants.START_PAGE]);
		self.stack.addWidget(self.widgetList[constants.BLUETOOTH_PAGE]);
		self.stack.addWidget(self.widgetList[constants.REQUEST_PAGE]);
		self.stack.addWidget(self.widgetList[constants.HOME_PAGE]);
		self.stack.addWidget(self.widgetList[constants.MENU_PAGE]);


		self.widgetList[constants.START_PAGE].requestWork.connect(self.openScreen);
		self.widgetList[constants.BLUETOOTH_PAGE].requestWork.connect(self.openScreen);
		self.widgetList[constants.REQUEST_PAGE].requestWork.connect(self.openScreen);
		self.widgetList[constants.HOME_PAGE].requestWork.connect(self.openScreen);
		self.widgetList[constants.MENU_PAGE].requestWork.connect(self.openScreen);

		self.openScreen(constants.START_PAGE);

		self.mqttClient = mqtt.Client();
		self.mqttClient.on_connect = self.onConnect;
		self.mqttClient.username_pw_set(username=constants.MQTT_ID_TEXT, password=constants.MQTT_PWD_TEXT);
		self.mqttClient.connect(constants.SERVER_IP_TEXT, constants.MQTT_PORT);
		self.mqttClient.on_message = self.widgetList[constants.REQUEST_PAGE].addRequest;
		self.mqttClient.loop_start();
	def appendSerial(self, dir) :
		self.serialErrorList.append(False);
		self.serialDirList.append(dir);
		self.serialList.append(serial.Serial(dir, 9600, timeout = 1));

	def closeEvent(self, event):
		self.running = False;
	def onConnect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc));
		topic1 = constants.MQTT_TOPIC_LOOT_TEXT;
		topic1 += "/";
		topic1 += self.serverConnect.getMacAddress();
		topic2 = constants.MQTT_TOPIC_WINDOW_TEXT;
		topic2 += "/";
		topic2 += self.serverConnect.getMacAddress();
		topics = [(topic1, 0), (topic2, 0)];
		client.subscribe(topics);


	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.close();

	def openScreen(self, pageNum) :
		print(pageNum);
		print(self.widgetList[pageNum]);
		self.stack.setCurrentWidget(self.widgetList[pageNum]);
		return;

	def uwbRecvTask(self):
		self.array2D = [];
		while self.running :
			try:
				self.array2D = [];
				for i in range(0, len(self.serialList), 1):
					self.serialErrorList[i] = True;
					data = self.serialList[i].read(402);
					array = [];
					if len(data) == 0 :
						continue;
					self.data = data;
					resultStr = "";
					resultStr += str(i);
					resultStr += " : \n";
					#print(int(data[400]));
					#print(int(data[401]));
					if len(data) != 402 or int(data[400]) != 13 or int(data[401]) != 10 :
						raise Exception("Serial Read Error");
					self.serialErrorList[i] = False;
					for j in range(0, 400, 4):
						realValue = struct.unpack('<h', data[j:j+2])[0];
						imagValue = struct.unpack('<h', data[j+2:j+4])[0];
						cirValue = int(math.sqrt(realValue * realValue + imagValue * imagValue)) / 5000;
						if cirValue > 10000:
							raise Exception("Value Error");
						array.append(cirValue);
						resultStr += "\t" + str(cirValue) + " ";
						if j % 40 == 36 :
							resultStr += "\n";
					fftArray = np.abs(np.fft.fft(array));
					self.array2D.append(fftArray.tolist());
					#resultStr += "\n";
					#print(resultStr);
				self.setUwbData(self.array2D);
				#distance = self.serialList.readline().decode('utf-8').strip();
				#if len(distance) == 0 :
				#	continue;
				#setUwbData(float(distance));
				#print("Received:", distance);
				#print(self.getUwbData());
				if i == len(self.serialList) - 1 :
					self.predict();
			except KeyboardInterrupt:
				self.serial.close();
				print("Serial communication closed.");
				break;
			except Exception as e:
				#print("An error occurred:", e);
				for i in range(0, len(self.serialList), 1):
					if self.serialList[i].is_open and self.serialErrorList[i] == True:
						self.serialList[i].close();
						self.serialList[i] = serial.Serial(self.serialDirList[i], 9600);
						self.serialErrorList[i] = False;
		for i in range(0, len(self.serialList), 1):
			if self.serialList[i].is_open:
				self.serialList[i].close();
				self.serialList[i] = serial.Serial(self.serialDirList[i], 9600);

	def setUwbData(self, data):
		with self.lock:
			self.uwbData = data;

	def getUwbData(self):
		with self.lock:
			ret = self.uwbData;
		return ret;	
		
if __name__ == '__main__':
	dirArr = [];
	dirArr.append('/dev/ttyUSB0');
	dirArr.append('/dev/ttyUSB1');
	app = QApplication(sys.argv);
	main = Main(dirArr, "./cnn/binaryModel.tflite");
	main.show();
	sys.exit(app.exec_())