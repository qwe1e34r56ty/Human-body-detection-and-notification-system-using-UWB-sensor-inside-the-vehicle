#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>

int main(int argc, char** argv) {
	inquiry_info *devices = NULL;
	int maxDevices = 8;
	int numDevices = 0;
	int devId, sock;

	devId = hci_get_route(NULL);
	sock = hci_open_dev(devId);
	if(devId < 0 || sock < 0){
		fprintf(stderr, "socket open failed");
		return 1;
	}
	char addrStr[18] = { 0 };
	char name[255] = { 0 };
	while(numDevices >= 0){
		numDevices = hci_inquiry(0, 4, maxDevices, NULL, &devices, IREQ_CACHE_FLUSH);
		fprintf(stderr, "%d\n", numDevices);
		for(int i = 0; i < numDevices; i++){
			ba2str(&(devices + i)->bdaddr, addrStr);
			memset(name, 0, sizeof(name));
			if(hci_read_remote_name(sock, &(devices + i)->bdaddr, sizeof(name), name, 0) < 0)
				strcpy(name, "[unknown]");
			fprintf(stderr, "%s %s\n", addrStr, name);
		}
    		if (numDevices < 0) {
        		perror("Bluetooth inquiry failed");
        		return 1;
    		}
	}
    	free(devices);
    	return 0;
}