# -*- coding: euc-kr -*-
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import tflite_runtime.interpreter as tf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

num_features = 200

def findCsvFilesInDir(dir):
	ret = []
	for file in os.listdir(dir):
		filePath = os.path.join(dir, file)
		if os.path.isfile(filePath):
			if file.endswith(".csv"):
				ret.append(filePath);
	return ret;

def loadCirFtDataSet(pathArr):
	X = np.empty((0, num_features));
	Y = np.empty((0,));
	for path in pathArr :
		data = pd.read_csv(path, header=None)
		X = np.append(X, data.iloc[:, :-1].values, axis=0)  # X에 데이터 추가
		Y = np.append(Y, data.iloc[:, -1].values, axis=0)
	return X, Y;

if __name__ == "__main__" :
	X, Y = loadCirFtDataSet(findCsvFilesInDir(sys.argv[1]));
	print(len(X));