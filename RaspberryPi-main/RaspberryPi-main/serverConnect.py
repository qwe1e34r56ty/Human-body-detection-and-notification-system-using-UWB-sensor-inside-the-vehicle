import requests;
import constants;
import query;
import netifaces;

class ServerConnect:
	def __init__(self):
		self.serverAddress = "http://" + constants.SERVER_IP_TEXT + ":" + constants.SERVER_PORT_TEXT + "/" ;
		self.macAddress = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr'];

	def connectConfirm(self):
		url = self.serverAddress + query.CHECK_ID;
		data = { 'id' : self.macAddress };
		response = requests.post(url, json=data);
		if response.status_code == 200:
			result = response.json()
			#print(result);
			if result['result'] == False and result['entry'] == False :
				#print("server DB Error");
				return False;
			return True;
		else :
			return  False;

	def sendLog(self, start, door, person, speed, warning):
		url = self.serverAddress+ query.LOG;
		data = { 'id' : self.macAddress, 'start' : start, 'door' : door, 'person' : person, 'speed' : speed, 'warning':warning };
		print(data);
		response = requests.post(url, json=data);
		if response.status_code == 200:
			result = response.json()
			print(result);
			if result['result'] == False : 
				print("server DB Error");
				return False;
			return True;
		else:
			return False;

	def sendCir(self, cir):
		url = self.serverAddress + query.CIR;
		data = {'id' : self.macAddress, 
			'leftdata' : str(list(map(lambda x : round(x, 1), cir[0]))), 
			'rightdata': str(list(map(lambda x : round(x, 1), cir[1])))};

		print(data);
		response = requests.post(url, json=data);
		if response.status_code == 200:
			result = response.json()
			print(result);
			if result['result'] == False : 
				print("server DB Error");
				return False;
			return True;
		else:
			return False;

	def sendPoint(self, ltit, lgit):
		url = self.serverAddress + query.PLACE;
		data = {'id' : self.macAddress, 'latitude':ltit, 'longitude':lgit};
		print(data);
		response = requests.post(url, json=data);
		if response.status_code == 200:
			result = response.json()
			print(result);
			if result['result'] == False : 
				print("server DB Error");
				return False;
			return True;
		else:
			return False;


	def getMacAddress(self):
		return self.macAddress;

if __name__ == "__main__" :
	serverConnect = ServerConnect();
	print(serverConnect.connectConfirm());
