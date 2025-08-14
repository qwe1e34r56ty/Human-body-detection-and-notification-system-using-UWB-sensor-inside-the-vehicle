# -*- coding: euc-kr -*-
import serial;
import threading;
import struct;
import math;
import signal;
import json;
import sys;
from datetime import datetime;

class EspMulti():
	def __init__(self):
		signal.signal(signal.SIGINT, self.signalHandler);
		self.running = True;
		self.serial = []
		self.file = self.makeRecordFile();
		self.array3D = [];
		self.serialDirArr = [];
	def appendSerial(self, dir) :
		self.serialDirArr.append(dir);
		self.serial.append(serial.Serial(dir, 9600, timeout = 1));
	def startRecv(self):
		self.task = threading.Thread(target=self.uwbRecvTask);
		self.task.start();
		self.task.join();
	def uwbRecvTask(self):
		arrayCount = 0;
		while self.running :
			if arrayCount == 63 :
				json.dump(self.array3D, self.file);
				self.file.close();
				self.file = self.makeRecordFile();
				self.array3D = [];
			try :
				self.array2D = [];
				for j in range(0, len(self.serial), 1):
					data = self.serial[j].read(256);
					array = [];
					if len(data) == 0 :
						continue;
					self.data = data;
					resultStr = "";
					resultStr += str(j);
					resultStr += " : \n";
					if len(data) != 256 :
						continue;
					for i in range(0, 256, 4):
						realValue = struct.unpack('<h', data[i:i+2])[0];
						imagValue = struct.unpack('<h', data[i+2:i+4])[0];
						cirValue = int(math.sqrt(realValue * realValue + imagValue * imagValue));
						if cirValue > 10000:
							raise Exception("Value Error");
						array.append(cirValue);
						resultStr += "\t" + str(cirValue) + " ";
						if i % 32 == 28 :
							resultStr += "\n";
					self.array2D.append(array);
					arrayCount += 1;
					resultStr += "\n";
					print(resultStr);
				self.array3D.append(self.array2D);
			except Exception as e:
				for j in range(0, len(self.serial), 1):
					self.serial[j].close();
					self.serial[j] = serial.Serial(self.serialDirArr[j], 9600);
				print("An error occurred:", e)
		for j in range(0, len(self.serial), 1):
			self.serial[j].close();
	def signalHandler(self, sig, frame):
		print("Ctrl+C");
		self.running = False;
		for j in range(0, len(self.serial), 1):
			if self.serial[j].is_open:
				self.serial[j].close();
		if self.file:
			json.dump(self.array3D, self.file, indent = 2);
			self.file.close();
	def makeRecordFile(self):
		currentTime = datetime.now();
		timeString = currentTime.strftime("%Y-%m-%d_%H:%M:%S");
		print("현재 시간:", timeString);
		fileName = timeString + "_log.txt";
		return open(fileName, 'w');
if __name__ == "__main__" :
	esp = EspMulti();
	esp.appendSerial('/dev/ttyUSB0');
	esp.appendSerial('/dev/ttyUSB1');
	esp.startRecv();