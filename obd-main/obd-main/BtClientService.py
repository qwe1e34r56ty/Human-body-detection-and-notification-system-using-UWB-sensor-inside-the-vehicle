import bluetooth

class BtClientService:
	def __init__(self):
		self.clientSock = None;
	def scanDevices(self):
		devices = bluetooth.discover_devices(duration = 8, lookup_names=True, lookup_class=True);
		print("Nearby devices:");
		for addr, name, _ in devices:
			print(f"Device Name: {name}, Address: {addr}");
		return devices;
	def makeConnect(self, device_address, port):
		try:
			self.clientSock = bluetooth.BluetoothSocket(bluetooth.RFCOMM);
			self.clientSock.connect((device_addr, port));

			print(f"Connected to {device_addr} on port {port}");
		except Exception as e:
			print(f"Connect Failed: {e}");
			pass;
	def isConnected(self):
		try:
			peer_addr = self.clientSock.getpeername();
			print(f"Connected with {peer_addr}");
			return True;
		except (bluetooth.btcommon.BluetoothError, AttributeError):
			print("Not Connected");
			return False;
		except Exception as e:
			print(f"Error: {e}");
			return False;

	def sendStr(self, str):
		if not self.isConnected() :
			return;
		try:
			self.clientSock.send(str);
		except Exception as e:
			print(f"Send Failed: {e}")

	def recvStr(self, len):
		if not self.isConnected() :
			return None;
		try:
			str = self.clientSock.recv(len);
			return str;
		except Exception as e:
			print(f"Recv Failed: {e}")
			return None;

if __name__ == "__main__":
	test = BtClientService();
	#test.scanDevices();
	test.isConnected();
	test.sendStr("abc");