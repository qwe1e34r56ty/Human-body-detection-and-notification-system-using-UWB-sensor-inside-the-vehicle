import numpy as np;
from cnn.loadModel import *;
import tflite_runtime.interpreter as tflite;
import sys;

class BinaryPredictor() :
	def __init__(self, modelPath):
	# .ftlite 확장자 모델
		self.interpreter = loadModel(modelPath);
		self.interpreter.allocate_tensors();
		self.inputDetails = self.interpreter.get_input_details();
		self.outputDetails = self.interpreter.get_output_details();
		self.inputIndex = self.inputDetails[0]['index'];
		self.outputIndex = self.outputDetails[0]['index'];

	# input은 float 정수 200개 배열
	def predict(self, input):
		input = np.array([input], dtype=np.float32);
		#print(input);
		self.interpreter.set_tensor(self.inputIndex, input);
		self.interpreter.invoke();
		output =  self.interpreter.get_tensor(self.outputIndex);
		print(output);
		if output < 0.5 :
			# 사람
			return 0;
		else :
			# 그외
			return 1;
