import sys
import os
import re
import json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView

append_path = os.path.join(os.path.dirname(__file__), '../verif_config/cgi-bin')
sys.path.append(append_path)
import tool

class DataObject(QObject):
    dataChanged = pyqtSignal(str)

    def __init__(self, consel):
        super().__init__()
        self._data = ""
        self.consel = consel

    @pyqtSlot(str)
    def setData(self, data):
        self._data = data
        print(self._data)
        self.dataChanged.emit(data)

    @pyqtSlot(result=str)
    def getData(self):
        print(self._data)
        return self._data

    @pyqtSlot(str)
    def setPreview(self, text):
        print(text)
        #self.dataChanged.emit(text)

    @pyqtSlot(str, result=str)
    def LoadHtml(self, req):
        html_info = tool.LoadHtml(req)
        html_json = json.loads(html_info)
        self.print_mess(html_json["mess"])
        return html_info

    @pyqtSlot(QVariant,result=str)
    def LoadSvg(self,req):
        svg = tool.LoadSvg(req['fileContent'], req['skt'])
        return svg.decode('utf-8')

    @pyqtSlot(result=str)
    def GetHtml(self):
        html_info = tool.GetHtml('default')
        html_json = json.loads(html_info)
        self.print_mess(html_json["mess"])
        return html_info

    @pyqtSlot(str,result=str)
    def GetSvg(self,req):
        svg = tool.GetSvg('default',req)
        return svg.decode('utf-8')

    @pyqtSlot(QVariant, result=str)
    def GetLog(self,configs):
        getlog = tool.GetLog(configs['configs'],configs['config'])
        html_json = json.loads(getlog)
        self.print_mess(html_json["message"])
        return getlog

    @pyqtSlot(QVariant, result=str)
    def Save(self,req):
        getlog = tool.Save(req["fileName"], req["configs"], req["overwrite"])
        return getlog

    def print_mess(self, mess):
        mess_list = mess.split('\n')
        for s in mess_list:
            if not s:
                continue
            if '<i success>' in s:
                color = 'green'
            elif '<i warning>' in s:
                color = 'yellow'
            elif '<i>Fatal' in s or '<i>[Error]' in s:
                color = 'red'
            else:
                color = 'black'
            self.consel.consel(re.sub(r'<.*?>', '', s).strip(), color)