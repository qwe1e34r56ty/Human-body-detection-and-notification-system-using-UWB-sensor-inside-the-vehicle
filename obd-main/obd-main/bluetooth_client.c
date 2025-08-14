#include<stdio.h>
#include<stdlib.h>
#include<signal.h>
#include<unistd.h>
#include<sys/socket.h>
#include<bluetooth/bluetooth.h>
#include<bluetooth/rfcomm.h>
#include<errno.h>
#include<fcntl.h>
#include<time.h>

int fd;
int s;
void ctrl_c_handler(int signal);
void close_sockets();
char* now_time_str();

int asciiToDec(char);
int get_data();
int get_engine_speed();
int get_vehicle_speed();
int get_maf();	// it is an MAF value, but the obd simulator you use does not provide a lock or not, so work with it as a lock or not value

const int delay;

int main(int argc,char **argv){
	(void) signal(SIGINT,ctrl_c_handler);
	char *message1 = "Read thread\n";
	char *message2 = "Write threadn";
	int iret1, iret2;
	struct sockaddr_rc addr= { 0 };
	int status;
	int result;
	char* dest = argv[1];	
	time_t nowTime;

	char logFileName[30] = { 0 };

	strcpy(logFileName, "log_");
	strcat(logFileName, now_time_str());
	strcat(logFileName, ".txt");
	fd = open(logFileName, O_CREAT | O_WRONLY | O_TRUNC, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP);
	if(dup2(fd, 1) == -1){
		fprintf(stderr, "redirect failed");
		return 1;
	}	

	s = socket(AF_BLUETOOTH,SOCK_STREAM,BTPROTO_RFCOMM);
	addr.rc_family = AF_BLUETOOTH;
	addr.rc_channel = 1 ;
	str2ba(dest,&addr.rc_bdaddr);
	fprintf(stderr, "going 2 connect\n");
	status = connect(s,(struct sockaddr *)&addr,sizeof(addr));

	if(0 == status){
		fprintf(stderr, "connect success\n");
		do{
			status = get_data();
			sleep(5);
		}while(status >= 0);
	}
	else{
		printf("failed\n");
		printf("%d\n", errno);
	}
	close_sockets();
	close(fd);
	return 0;
}

char* now_time_str(){
	static char timeStr[20];

	time_t nowTime;
	struct tm* timeInfo;
	time(&nowTime);
	timeInfo = localtime(&nowTime);
	strftime(timeStr, sizeof(timeStr), "%Y_%m_%d_%H_%M_%S", timeInfo);
	return timeStr;
}

int get_data(){
	int engineSpeed, vehicleSpeed, maf;

	engineSpeed = get_engine_speed();
	if(engineSpeed < 0)
		return engineSpeed;	vehicleSpeed  = get_vehicle_speed();
	if(vehicleSpeed < 0)
		return vehicleSpeed;
	maf = get_maf();
	if(maf < 0)
		return maf;

	int isEngineOn = (engineSpeed == 0) ? 0 : 1;
	int isDoorLock = (maf == 0) ? 0 : 1;	

	fprintf(stdout, "isEngineOn : %s, vehicleSpeed : %d, isDoorLock : %s, ",
		(isEngineOn == 1) ? "TRUE" : "FALSE", vehicleSpeed, (isDoorLock == 1) ? "TRUE" : "FALSE");
	fprintf(stdout, "date : %s,\n", now_time_str());
	return 0;
}

int asciiToDec(char c){
	if(c >= 48 && c <= 57)
		return c - 48;
	else if(c >= 65 && c <= 70)
		return c - 55;
	return 0;
}

int get_engine_speed(){
	int result = 0;
	int status = 0;
	char msg[25] = "010C";

	msg[strlen(msg)] = 13;
	msg[strlen(msg)] = 10;
	msg[strlen(msg)] = 0;
	status = send(s, msg, strlen(msg), 0);
	if(status <= 0)
		return status;

	char buf[1024] = { 0 };
	int bytes_read;
	memset(buf, 0, sizeof(buf));
	bytes_read = recv(s, buf, sizeof(buf), 0);
	if(bytes_read <= 0)
		return bytes_read;

	result += 16 * 16 * 16 * asciiToDec(buf[11]);
	result += 16 * 16 * asciiToDec(buf[12]);
	result += 16 * asciiToDec(buf[14]);
	result += asciiToDec(buf[15]);

	bytes_read = recv(s, buf, sizeof(buf), 0);
	if(bytes_read < 0)
		return bytes_read;

	fprintf(stderr, "%d\n", result);
	return result;
}

int get_vehicle_speed(){
	int result = 0;
	int status = 0;
	char msg[25] = "010D";

	msg[strlen(msg)] = 13;
	msg[strlen(msg)] = 10;
	msg[strlen(msg)] = 0;
	status = send(s, msg, strlen(msg), 0);
	if(status <= 0)
		return status;

	char buf[1024] = { 0 };
	int bytes_read;
	memset(buf, 0, sizeof(buf));
	bytes_read = recv(s, buf, sizeof(buf), 0);
	if(bytes_read <= 0)
		return bytes_read;

	result += 16 *  asciiToDec(buf[11]);
	result += asciiToDec(buf[12]);

	bytes_read = recv(s, buf, sizeof(buf), 0);
	if(bytes_read < 0)
		return bytes_read;

	fprintf(stderr, "%d\n", result);
	return result;
}

int get_maf(){
	int result = 0;
	int status = 0;
	char msg[25] = "0110";

	msg[strlen(msg)] = 13;
	msg[strlen(msg)] = 10;
	msg[strlen(msg)] = 0;
	status = send(s, msg, strlen(msg), 0);
	if(status <= 0)
		return status;

	char buf[1024] = { 0 };
	int bytes_read;
	memset(buf, 0, sizeof(buf));
	bytes_read = recv(s, buf, sizeof(buf), 0);
	if(bytes_read <= 0)
		return bytes_read;

	result += 16 * 16 * 16 * asciiToDec(buf[11]);
	result += 16 * 16 * asciiToDec(buf[12]);
	result += 16 * asciiToDec(buf[14]);
	result += asciiToDec(buf[15]);

	bytes_read = recv(s, buf, sizeof(buf), 0);
	if(bytes_read < 0)
		return bytes_read;

	fprintf(stderr, "%d\n", result);
	return result;

}

void close_sockets(){
	close(s);
	close(fd);
	fprintf(stderr,"Close sockets\n");
}

void ctrl_c_handler(int signal){
	fprintf(stderr,"Interrupt caught[NO: %d ]\n",signal);
	close_sockets();
	exit(0);
}
