import BtClientService;
from enum import Enum;

class obd2ClientService:
	class Pid(Enum):
		CARSTART = "010C" + chr(13) + chr(10);
		VEHICLESPEED = "010D" + chr(13) + chr(10);
		DOORLOCK = "0110" + chr(13) + chr(10);
	def __init__(self):
		self.carStart = False;
		self.vehicleSpeed = 0;
		self.doorLock = False;
		self.BtClientService = BtService();
	def makeConnect(self, deviceAddr, port):
		return self.BtClientService.makeConnnect(deviceAddr, port);
	def isConnected(self):
		return self.BtClientService.isConnected();
	def getCarStart(self):
		ret = self.BtClientService.sendStr(Pid.CARSTART);
		if ret == False:
			raise Exception("getCatStart Failed : Send Error");
		str = self.BtClientService.recvStr(1024);
		if str == "":
			raise Exception("getCartStart Failed : recv Error");
		if str[15] == 48 :
			return False;
		else:
			return True;
	def getVehicleSpeed(self):
		ret = self.BtClientService.sendStr(Pid.VEHICLESPEED);
		if ret == False:
			raise Exception("getVehicleSpeed Failed : Send Error");
		if str == "":
			raise Exception("getVehicleSpeed Failed : recv Error");
		return 16 * asciiToDec(str[11]) + asciiToDec(str[12]);
	def getDoorLock(self):
		ret = self.BtClientService.sendStr(Pid.DOORLOCK);
		if ret == False:
			raise Exception("getDoorLock Failed : Send Error");
		if str == "":
			raise Exception("getDoorLock Failed : recv Error");
		if str[15] == 48 :
			return False;
		else:
			return True;
	def asciiToDec(c):
		if(c >= 48 and c <= 57):
			return c - 48;
		elif(c >= 65 and c <= 70):
			return c - 55;
		else:
			return 0;
if __name__ == "__main__":
	#deviceAddr = inpurt("Enter Obd2 Bt Adapter address: ");
	#port = int(input("Enter RFCOMM port: ");
	#getData(device_address, port);
	pass;