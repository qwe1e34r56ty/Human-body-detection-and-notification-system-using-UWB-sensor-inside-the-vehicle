import serial;
import time;
import string;
import pynmea2;
import sys;

def getPoint(port = "/dev/ttyS0"):
	while True :
		try :
			ser=serial.Serial(port, baudrate=9600, timeout=0.5);
			dataout = pynmea2.NMEAStreamReader();
			newdata=ser.readline().decode('utf-8');
			if len(newdata) < 6 : 
				continue;
			if newdata[0:6] == "$GPRMC":
				newmsg=pynmea2.parse(newdata);
				lat=newmsg.latitude;
				lng=newmsg.longitude;
				gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng);
				print(gps);
				return (lat, lng);
		except Exception as e:
			print(0);
			return (0, 0);

if __name__ == "__main__":
	while True:
		getPoint();