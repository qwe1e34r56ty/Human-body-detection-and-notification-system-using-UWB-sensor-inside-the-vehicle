# -*- coding: euc-kr -*-
import serial;
import threading;
import struct;
import math;
import signal;
import sys;
import os;
import csv
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
import pyqtgraph as pg;
from pyqtgraph import QtGui;
from datetime import datetime;import numpy as np
import matplotlib.pyplot as plt

class GetCirFtDataSetWindow(QMainWindow):
	def __init__(self, label, dir):
		super().__init__();
		signal.signal(signal.SIGINT, self.signalHandler);
		self.dataLabel = label;
		self.dir = dir;
		if not os.path.exists(self.dir) :
			os.makedirs(self.dir);
			print(f"{self.dir} dir created");
		self.setWindowState(Qt.WindowFullScreen);
		self.setWindowTitle("Cir Data Display");
		centralWidget = QWidget();
		self.setCentralWidget(centralWidget);

		layout = QVBoxLayout();
		centralWidget.setLayout(layout);

		self.topPlotWidget = pg.PlotWidget();
		self.bottomPlotWidget = pg.PlotWidget();
		self.status = " ";
		self.statusLabel = QLabel(self.status);
		self.dataQLabel = QLabel(self.dataLabel);

		layout.addWidget(self.dataQLabel);
		layout.addWidget(self.topPlotWidget);
		layout.addWidget(self.bottomPlotWidget);
		layout.addWidget(self.statusLabel);

		self.topPlotWidget.setBackground('w');
		self.bottomPlotWidget.setBackground('w');

		self.pen = pg.mkPen(color = 'k', width = 3);
		self.topPlotWidget.getAxis('left').setPen(self.pen);
		self.topPlotWidget.getAxis('bottom').setPen(self.pen);
		self.bottomPlotWidget.getAxis('left').setPen(self.pen);
		self.bottomPlotWidget.getAxis('bottom').setPen(self.pen);

		#self.topPlotWidget.setYRange(0, 1);
		#self.bottomPlotWidget.setYRange(0, 1);

		self.x = list(range(0, 100))
		self.yArray2D = [[0] * 100, [0] * 100];
		self.topPlotCurve = self.topPlotWidget.plot(self.x, self.yArray2D[0], pen = self.pen);
		self.bottomPlotCurve = self.bottomPlotWidget.plot(self.x, self.yArray2D[1], pen = self.pen);

		self.running = True;
		self.serialList = [];
		self.serialDirList = [];
		self.serialErrorList = [];

		self.file = self.makeRecordFile();
		self.array3D = [];
		self.fileCount = 0;
		self.cirCount = 0;

	def appendSerial(self, dir) :
		self.serialErrorList.append(False);
		self.serialDirList.append(dir);
		self.serialList.append(serial.Serial(dir, 9600, timeout = 1));

	def startRecv(self):
		self.task = threading.Thread(target=self.uwbRecvTask);
		self.task.start();
		self.lock  = threading.Lock();

		self.timer = QTimer();
		self.timer.timeout.connect(self.updatePlot);
		self.timer.start(200);

	def updatePlot(self):
		tmp = self.getCirData();
		self.topPlotCurve.setData(self.x, tmp[0], pen = self.pen );
		self.bottomPlotCurve.setData(self.x, tmp[1], pen = self.pen );
		self.status = f"File Count : {self.fileCount}, Cir Count : {self.cirCount}";
		self.statusLabel.setText(self.status);

	def setCirData(self, newData):
		with self.lock:
			self.yArray2D = newData;
			
	def getCirData(self):
		with self.lock:
			return self.yArray2D;

	def uwbRecvTask(self):
		self.cirCount = 0;
		self.array3D = [];
		self.array2D = [];
		while self.running :
			if self.cirCount == 20 :
				self.writeCsv();
				self.file.close();
				self.file = self.makeRecordFile();
				self.array3D = [];
				self.fileCount += 1;
				self.cirCount = 0;
			try :
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
					print(int(data[400]));
					print(int(data[401]));
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
					resultStr += "\n";
					print(resultStr);
				self.setCirData(self.array2D);
				self.array2D.append(self.dataLabel);
				self.cirCount += 1;
				self.array3D.append(self.array2D);
			except Exception as e:
				print("An error occurred:", e);
				for i in range(0, len(self.serialList), 1):
					if self.serialList[i].is_open and self.serialErrorList[i] == True:
						self.serialList[i].close();
						self.serialList[i] = serial.Serial(self.serialDirList[i], 9600);
						self.serialErrorList[i] = False;
		for j in range(0, len(self.serialList), 1):
			self.serialList[j].close();
	def signalHandler(self, sig, frame):
		print("Ctrl+C");
		self.running = False;
		for j in range(0, len(self.serialList), 1):
			if self.serialList[j].is_open:
				self.serialList[j].close();
		if self.file:
			self.writeCsv();
			self.file.close();
		self.task.join();
		self.close();
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.running = False;
			for j in range(0, len(self.serialList), 1):
				if self.serialList[j].is_open:
					self.serialList[j].close();
			if self.file:
				self.writeCsv();
				self.file.close();
			self.task.join();
			self.close();
	def makeRecordFile(self):
		currentTime = datetime.now();
		timeString = currentTime.strftime("%Y-%m-%d_%H:%M:%S");
		print("현재 시간:", timeString);
		fileName = timeString + "_log.csv";
		return open(f"{self.dir}/{fileName}", "w");

	def writeCsv(self):
		writer = csv.writer(self.file);
		for data in self.array3D:
			row = data[0] + data[1] + [data[2]];
			writer.writerow(row);

if __name__ == "__main__" :
	app = QApplication(sys.argv);
	esp = GetCirFtDataSetWindow(sys.argv[1], sys.argv[2]);
	esp.appendSerial('/dev/ttyUSB0');
	esp.appendSerial('/dev/ttyUSB1');
	esp.show();
	esp.startRecv();
	sys.exit(app.exec_())