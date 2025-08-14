from btClientService import *;
from enum import Enum;

class Obd2ClientService(BtClientService):
	class Pid(Enum):
		CARSTART = "010C" + chr(13) + chr(10);
		VEHICLESPEED = "010D" + chr(13) + chr(10);
		DOORLOCK = "0110" + chr(13) + chr(10);

	def __init__(self):
		super().__init__();
		self.carStart = False;
		self.vehicleSpeed = 0;
		self.doorLock = False;

	def makeConnect(self, name, deviceAddr, port):
		return super().makeConnect(name, deviceAddr, port);

	def isConnected(self):
		return super().isConnected();

	def getCarStart(self):
		ret = super().sendStr("010C" + chr(13) + chr(10));
		if ret == False:
			raise Exception("getCatStart Failed : Send Error");
		receivedStr = super().recvStr(1024);
		receivedStr += super().recvStr(1024);
		#print(f"CarStart : {receivedStr}"); 
		if receivedStr == "":
			raise Exception("getCartStart Failed : recv Error");
		value = 0;
		value += self.asciiToDec(receivedStr[11]); value *= 16;
		value += self.asciiToDec(receivedStr[12]); value *= 16;
		value += self.asciiToDec(receivedStr[14]); value *= 16;
		value += self.asciiToDec(receivedStr[15]);
		if value < 3000 :
			return False;
		else:
			return True;

	def getVehicleSpeed(self):
		ret = super().sendStr("010D" + chr(13) + chr(10));
		if ret == False:
			raise Exception("getVehicleSpeed Failed : Send Error");
		receivedStr = super().recvStr(1024);
		receivedStr += super().recvStr(1024);
		#print(f"VehicleSpeed : {receivedStr}"); 
		if receivedStr == "":
			raise Exception("getVehicleSpeed Failed : recv Error");
		return 16 * self.asciiToDec(receivedStr[11]) + self.asciiToDec(receivedStr[12]);
	def getDoorLock(self):
		ret = super().sendStr("0110" + chr(13) + chr(10));
		receivedStr = super().recvStr(1024);
		receivedStr += super().recvStr(1024);
		#print(f"DoorLock : {receivedStr}"); 
		if ret == False:
			raise Exception("getDoorLock Failed : Send Error");
		if receivedStr == "":
			raise Exception("getDoorLock Failed : recv Error");
		value = 0;
		value += self.asciiToDec(receivedStr[11]); value *= 16;
		value += self.asciiToDec(receivedStr[12]); value *= 16;
		value += self. asciiToDec(receivedStr[14]); value *= 16;
		value += self.asciiToDec(receivedStr[15]);
		if value < 3000 :
			return False;
		else:
			return True;

	def getTemperature(self):
		ret = super().sendStr("0105" + chr(13) + chr(10));
		if ret == False:
			raise Exception("getVehicleSpeed Failed : Send Error");
		receivedStr = super().recvStr(1024);
		receivedStr += super().recvStr(1024);
		print(f"Temperature : {receivedStr}"); 
		if receivedStr == "":
			raise Exception("getVehicleSpeed Failed : recv Error");
		return 16 * self.asciiToDec(receivedStr[11]) + self.asciiToDec(receivedStr[12]) - 40;

	def getThrottle(self):
		ret = super().sendStr("0111" + chr(13) + chr(10));
		if ret == False:
			raise Exception("getVehicleSpeed Failed : Send Error");
		receivedStr = super().recvStr(1024);
		receivedStr += super().recvStr(1024);
		print(f"Temperature : {receivedStr}"); 
		if receivedStr == "":
			raise Exception("getVehicleSpeed Failed : recv Error");
		return 100 / (16 * self.asciiToDec(receivedStr[11]) + self.asciiToDec(receivedStr[12])) * 255;


	def getOxygen(self):
		ret = super().sendStr("0114" + chr(13) + chr(10));
		if ret == False:
			raise Exception("getVehicleSpeed Failed : Send Error");
		receivedStr = super().recvStr(1024);
		receivedStr += super().recvStr(1024);
		print(f"Temperature : {receivedStr}"); 
		if receivedStr == "":
			raise Exception("getVehicleSpeed Failed : recv Error");
		return (16 * self.asciiToDec(receivedStr[11]) + self.asciiToDec(receivedStr[12])) / 200;


	def asciiToDec(self, c):
		if(c >= 48 and c <= 57):
			return c - 48;
		elif(c >= 65 and c <= 70):
			return c - 55;
		else:
			return 0;

if __name__ == "__main__":
	deviceAddr = input("Enter Obd2 Bt Adapter address: ");
	port = int(input("Enter RFCOMM port: "));
	obd2ClientService = Obd2ClientService();
	obd2ClientService.makeConnect("Infocar", deviceAddr, port);
	obd2ClientService.getCarStart();
	obd2ClientService.getVehicleSpeed();
	obd2ClientService.getDoorLock();
	pass;