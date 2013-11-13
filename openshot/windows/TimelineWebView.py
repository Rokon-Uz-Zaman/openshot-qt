#!/usr/bin/env python
#	OpenShot Video Editor is a program that creates, modifies, and edits video files.
#   Copyright (C) 2009  Jonathan Thomas, TJ
#
#	This file is part of OpenShot Video Editor (http://launchpad.net/openshot/).
#
#	OpenShot Video Editor is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenShot Video Editor is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with OpenShot Video Editor.  If not, see <http://www.gnu.org/licenses/>.

import os
from PyQt5.QtCore import QFileInfo, pyqtSlot, QUrl, Qt
from PyQt5.QtWidgets import QAbstractSlider
from PyQt5.QtWebKitWidgets import QWebView
from classes.logger import log

class TimelineWebView(QWebView):
	html_path = ('windows','html','openshot_timeline_demo','timeline.html')
	#html_path = ('windows','html','test.html')

	#Capture wheel event to alter zoom slider control
	def wheelEvent(self, event):
		if int(self.window.app.keyboardModifiers() & Qt.ControlModifier) > 0:
			#For each 120 (standard scroll unit) adjust the zoom slider
			tick_scale = 120
			y = event.angleDelta().y()
			up = y > 0
			while (y != 0):
				if up and y > tick_scale:
					y -= tick_scale
				elif not up and y < -tick_scale:
					y += tick_scale
				else:
					y = 0
				if up:
					self.window.sliderZoom.triggerAction(QAbstractSlider.SliderPageStepAdd)
				else:
					self.window.sliderZoom.triggerAction(QAbstractSlider.SliderPageStepSub)		
			log.info('Ctrl+MouseWheel used on timeline. New zoom: ' + str(self.window.sliderZoom.value()))
		#Otherwise pass on to implement default functionality (scroll in QWebView)
		else:
			super(type(self), self).wheelEvent(event)
	
	#Demo slot callable from javascript
	@pyqtSlot()
	def navigate(self):
		#load url from address bar
		self.setUrl(QUrl(self.window.txtAddress.text()))
		
	def addJavaScriptObject(self):
		#Export self as a javascript object in webview
		self.page().mainFrame().addToJavaScriptWindowObject('timeline', self)
		self.page().mainFrame().addToJavaScriptWindowObject('mainWindow', self.window)
	
	def __init__(self, window):
		QWebView.__init__(self)
		self.window = window
		#self.installEventFilter(window)
		
		#set url from configuration (QUrl takes absolute paths for file system paths, create from QFileInfo)
		self.setUrl(QUrl.fromLocalFile(QFileInfo(os.path.join(*self.html_path)).absoluteFilePath()))
		
		#Connect signal of javascript initialization to our javascript reference init function
		self.page().mainFrame().javaScriptWindowObjectCleared.connect(self.addJavaScriptObject)
		