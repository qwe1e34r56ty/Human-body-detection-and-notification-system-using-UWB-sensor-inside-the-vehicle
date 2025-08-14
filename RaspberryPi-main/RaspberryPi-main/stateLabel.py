# -*- coding: euc-kr -*-
import sys;
from PyQt5.QtWidgets import *;
from PyQt5.QtCore import *;
from PyQt5.Qt import *;
from getExternalFont import *;

class stateLabel(QWidget):
	def __init__(self, topText, imagePath, bottomText):
		super().__init__();
        
		#self.setStyleSheet("background-color: #FFFFFF; border-radius: 50%;");
		self.setFixedSize(350, 380);
        
		self.layout = QVBoxLayout();
		self.layout.setContentsMargins(10, 10, 10, 10);	
        
		self.topTextLabel = QLabel(topText, self);
		self.topTextLabel.setStyleSheet("font-size:48px; color: #FFFFFF;");
		self.topTextLabel.setFont(getExternalFont());
		self.topTextLabel.setAlignment(Qt.AlignCenter);
		self.layout.addWidget(self.topTextLabel);
        
		self.pixmap = QPixmap(imagePath);
		self.image = QLabel(self);
		self.image.setPixmap(self.pixmap.scaled(220, 220));
		self.image.setFixedSize(335, 280);
		self.image.setAlignment(Qt.AlignCenter);
		self.layout.addWidget(self.image);

		self.bottomTextLabel = QLabel(bottomText, self);
		self.bottomTextLabel.setFont(getExternalFont());
		self.bottomTextLabel.setStyleSheet("font-size:48px; color: #FFFFFF;");
		self.bottomTextLabel.setAlignment(Qt.AlignCenter);
		self.layout.addWidget(self.bottomTextLabel);

		self.setLayout(self.layout);

	def setTopText(self, text):
		self.topTextLabel.setText(text);

	def setBottomText(self, text):
		self.bottomTextLabel.setText(text);

	def setImage(self, imagePath):
		self.pixmap = QPixmap(imagePath);
		self.image.setPixmap(self.pixmap.scaled(200, 200));

if __name__ == '__main__':
	app = QApplication(sys.argv);
    
	topText = "위";
	imagePath = "./image/network_disconnected.png";
	bottomText = "아래";
    
	widget = stateLabel(topText, imagePath, bottomText);
	widget.show();
    
	sys.exit(app.exec_());