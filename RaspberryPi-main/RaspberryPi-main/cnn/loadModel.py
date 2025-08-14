import tflite_runtime.interpreter as tflite;
import sys;

def loadModel(filePath):
	interpreter = tflite.Interpreter(filePath);
	return interpreter;

if __name__ ==  "__main__":
	print(loadModel(sys.argv[1]));