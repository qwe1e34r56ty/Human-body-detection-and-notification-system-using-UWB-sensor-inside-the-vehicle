/*
 * MIT License
 * 
 * Copyright (c) 2018 Michele Biondi, Andrea Salvatori
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
*/

/*
 * Copyright (c) 2015 by Thomas Trojer <thomas@trojer.net>
 * Decawave DW1000 library for arduino.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @file BasicReceiver.ino
 * Use this to test simple sender/receiver functionality with two
 * DW1000:: Complements the "BasicSender" example sketch.
 * 
 * @todo
 *  - move strings to flash (less RAM consumption)
 *  
 */

#include <DW1000Ng.hpp>
#include <DW1000NgUtils.hpp>
#include <DW1000NgRanging.hpp>
#include <DW1000NgConstants.hpp>
#include <DW1000NgRegisters.hpp>
#include <SPIporting.hpp>

#define DEBUG 0
#define LEN_DATA 17

const uint8_t PIN_SS = 4; // spi select pin
uint8_t _ss = PIN_SS;
uint16_t numReceived = 0; // todo check int type
String message;

TaskHandle_t SerialTaskHandle;
    
constexpr uint16_t LEN_FP_INDEX = 2;
constexpr uint16_t CIR_FP_INDEX_SUB = 0x05;
constexpr uint16_t ACC_MEM = 0x25;
constexpr uint16_t LEN_CIR = 4;
constexpr uint16_t LEN_PMSC = 4;
constexpr uint16_t FACE_BIT = 6;
constexpr uint16_t AMCE_BIT = 15;
byte cirDataBytes[LEN_CIR * 64];

device_configuration_t DEFAULT_CONFIG = {
    false,
    true,
    true,
    true,
    false,
    SFDMode::STANDARD_SFD,
    Channel::CHANNEL_5,
    DataRate::RATE_850KBPS,
    PulseFrequency::FREQ_16MHZ,
    PreambleLength::LEN_256,
    PreambleCode::CODE_3
};

void setup() {
  // DEBUG monitoring
  Serial.begin(9600);
  // initialize the driver
  DW1000Ng::initializeNoInterrupt(PIN_SS);
  DW1000Ng::applyConfiguration(DEFAULT_CONFIG);
  DW1000Ng::setDeviceAddress(6);
  DW1000Ng::setNetworkId(10);
  DW1000Ng::setAntennaDelay(16436);

  byte pmscBytes[LEN_PMSC];
  _readBytesFromRegister(PMSC, PMSC_CTRL0_SUB, pmscBytes, LEN_PMSC);
  pmscBytes[0] |= 1 << FACE_BIT;
  pmscBytes[1] |= 1 << (AMCE_BIT - sizeof(byte));
  _writeBytesToRegister(PMSC, PMSC_CTRL0_SUB, pmscBytes, LEN_PMSC);

  if(DEBUG){
    Serial.println(F("### DW1000Ng-arduino-receiver-test ###"));
    // DEBUG chip info and registers pretty printed
    char msg[128];
    DW1000Ng::getPrintableDeviceIdentifier(msg);
    Serial.print("Device ID: "); Serial.println(msg);
    DW1000Ng::getPrintableExtendedUniqueIdentifier(msg);
    Serial.print("Unique ID: "); Serial.println(msg);
    DW1000Ng::getPrintableNetworkIdAndShortAddress(msg);
    Serial.print("Network ID & Device Address: "); Serial.println(msg);
    DW1000Ng::getPrintableDeviceMode(msg);
    Serial.print("Device mode: "); Serial.println(msg);
  }
}

void loop() {
  DW1000Ng::startReceive();
  while(!DW1000Ng::isReceiveDone()) {
    #if defined(ESP8266)
    yield();
    #endif
  }
  DW1000Ng::clearReceiveStatus();
  numReceived++;
  // get data as string
  DW1000Ng::getReceivedData(message);
  byte fpIndex[LEN_FP_INDEX];
  _readBytesFromRegister(RX_TIME, CIR_FP_INDEX_SUB, fpIndex, LEN_FP_INDEX);
  uint16_t f = ((uint16_t)fpIndex[0] | ((uint16_t)fpIndex[1] << 8)) >> 6; 

  int16_t c = 0;
  byte cirDataBytesTemp[LEN_CIR * 64 + 1];
  _readBytesFromRegister(ACC_MEM, f * LEN_CIR, cirDataBytesTemp, LEN_CIR * 64 + 1);
  
  memcpy(cirDataBytes, &cirDataBytesTemp[1], LEN_CIR * 64);

  int16_t real = *(int16_t*)(&cirDataBytes[0]);
  int16_t imag = *(int16_t*)(&cirDataBytes[2]);
  c = sqrt(real * real + imag * imag);

  if(DEBUG){
    Serial.print("Received message ... #"); Serial.println(numReceived);
    Serial.print("Data is ... "); Serial.println(message);
    Serial.print("RX power is [dBm] ... "); Serial.println(DW1000Ng::getReceivePower());
    Serial.print("Signal quality is ... "); Serial.println(DW1000Ng::getReceiveQuality());         
    String fpIndexString = "fpIndex : "; fpIndexString += f;
    Serial.println(fpIndexString);
  }

  Serial.write(cirDataBytes, 256);
  //Serial.println(*(uint8_t*)&cirDataBytes[0]);
}

void _readBytesFromRegister(byte cmd, uint16_t offset, byte data[], uint16_t data_size) {
	byte header[3];
	uint8_t headerLen = 1;
			
	// build SPI header
	if(offset == NO_SUB) {
		header[0] = READ | cmd;
	} else {
		header[0] = READ_SUB | cmd;
		if(offset < 128) {
			header[1] = (byte)offset;
			headerLen++;
		} else {
			header[1] = RW_SUB_EXT | (byte)offset;
			header[2] = (byte)(offset >> 7);
			headerLen += 2;
		}
	}
	SPIporting::readFromSPI(_ss, headerLen, header, data_size, data);
}
void _writeBytesToRegister(byte cmd, uint16_t offset, byte data[], uint16_t data_size) {
	byte header[3];
	uint8_t headerLen = 1;
			
	// TODO proper error handling: address out of bounds
  // build SPI header
	if(offset == NO_SUB) {
		header[0] = WRITE | cmd;
	} else {
		header[0] = WRITE_SUB | cmd;
		if(offset < 128) {
			header[1] = (byte)offset;
			headerLen++;
		} else {
			header[1] = RW_SUB_EXT | (byte)offset;
			header[2] = (byte)(offset >> 7);
			headerLen += 2;
		}
	}
			
	SPIporting::writeToSPI(_ss, headerLen, header, data_size, data);
}
