from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QFont, QFontDatabase
import sys;

def getExternalFont(fontPath = "./font/TmoneyRoundWindExtraBold.ttf", size = 20):
	QFontDatabase.addApplicationFont(fontPath);
	font_id = QFontDatabase.addApplicationFont(fontPath);
	font_family = QFontDatabase.applicationFontFamilies(font_id)[0];

	return QFont(font_family, size);

if __name__ ==  "__main__" :
	app = QApplication(sys.argv);
	label = QLabel("Hello World");
	label.resize(200, 100);
	font = getExternalFont();
	label.setFont(getExternalFont());
	label.show();
	sys.exit(app.exec_());