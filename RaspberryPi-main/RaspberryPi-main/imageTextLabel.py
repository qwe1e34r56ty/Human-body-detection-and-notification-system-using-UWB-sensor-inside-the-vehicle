# -*- coding: euc-kr -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class ImageTextLabel(QWidget):
	def __init__(self, imagePath, text):
		super().__init__()
        
		self.layout = QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)

		self.imageLabel = QLabel(self)
		self.imageLabel.setPixmap(QPixmap(imagePath).scaled(200, 200));
		self.imageLabel.setFixedSize(200, 200)
		self.imageLabel.setAlignment(Qt.AlignCenter);

		self.textLabel = QLabel(text, self)
		self.textLabel.setAlignment(Qt.AlignCenter);

		self.layout.addWidget(self.imageLabel)
		self.layout.addWidget(self.textLabel)
		self.setLayout(self.layout)
		self.setFixedSize(200, 250)

	def setImage(self, imagePath) :
		self.imageLabel.setPixmap(QPixmap(imagePath).scaled(200, 200));
		self.imageLabel.setFixedSize(200, 200)

	def setText(self, text):
		self.textLabel.setText(text);

if __name__ == "__main__":
	app = QApplication(sys.argv)
	widget = QWidget();
	layout = QVBoxLayout();
	widget.setLayout(layout);
	widget.layout().addWidget(ImageTextLabel("image.jpg", "Hello"));
	widget.show();
	sys.exit(app.exec_())