# -*- coding: euc-kr -*-
import serial;
import threading;
import struct;
import math;
import signal;
import json;
import sys;
from datetime import datetime;

class Esp():
	def __init__(self):
		signal.signal(signal.SIGINT, self.signalHandler);
		self.running = True;
		self.serial = serial.Serial('/dev/ttyS0', 9600, timeout = 1);
		self.file = self.makeRecordFile();
		self.array2D = [];
		self.task = threading.Thread(target=self.uwbRecvTask);
		self.task.start();
		self.task.join();
	def uwbRecvTask(self):
		arrayCount = 0;
		while self.running :
			if arrayCount == 63 :
				json.dump(self.array2D, self.file);
				self.file.close();
				self.file = self.makeRecordFile();
				self.array2D = [];
			try :
				data = self.serial.read(256);
				array = [];
				if len(data) == 0 :
					continue;
				self.data = data;
				resultStr = "";
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
			except Exception as e:
				self.serial.close();
				self.serial = serial.Serial('/dev/ttyS0', 9600);
				print("An error occurred:", e)
		self.serial.close();
	def signalHandler(self, sig, frame):
		print("Ctrl+C");
		if self.serial.is_open:
			self.serial.close();
		if self.file:
			json.dump(self.array2D, self.file, indent = 2);
			self.file.close();
		self.running = False;
	def makeRecordFile(self):
		currentTime = datetime.now();
		timeString = currentTime.strftime("%Y-%m-%d_%H:%M:%S");
		print("현재 시간:", timeString);
		fileName = timeString + "_log.txt";
		return open(fileName, 'w');
if __name__ == "__main__" :
	esp = Esp();
