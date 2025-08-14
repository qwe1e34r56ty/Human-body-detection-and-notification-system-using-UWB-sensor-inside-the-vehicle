from binaryPredictor import *;
from loadCirFtDataSet import *;

modelPath = input("model path: ");
pred = BinaryPredictor(modelPath);
dataSetDir = input("dataSetDir: ");
X, Y = loadCirFtDataSet(findCsvFilesInDir(dataSetDir));
while 1:
	index = input("predict index(quit : q) : ");
	if index != 'q' and not index.isdigit():
		print("Invalid Input");
		continue;
	if index == 'q' :
		break;
	print(pred.predict(X[int(index)]));
	