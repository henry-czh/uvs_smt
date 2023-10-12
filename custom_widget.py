from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import time


class CustomQCB(QComboBox):
    def wheelEvent(self, e):
        if e.type() == QEvent.Wheel:
            e.ignore()


class CustomQSB(QSpinBox):
    def wheelEvent(self, e):
        if e.type() == QEvent.Wheel:
            e.ignore()

class QComboBox_czh(QComboBox):
    def __init__(self, parent=None):
        super(QComboBox_czh,self).__init__(parent)

    def wheelEvent(self, e):
        if e.type() == QEvent.Wheel:
            e.ignore()

class QSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super(QSpinBox,self).__init__(parent)

    def wheelEvent(self, e):
        if e.type() == QEvent.Wheel:
            e.ignore()

class ColoredTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super(ColoredTextBrowser,self).__init__(parent)
        self.last_time = 0

    def tips(self):
        # 获取当前文本光标
        cursor = self.textCursor()

        # 创建文本字符格式，设置颜色
        char_format = QTextCharFormat()
        char_format.setForeground(QColor('blue'))
        cursor.setCharFormat(char_format)

        # 插入文本
        if self.last_time < time.mktime(time.localtime()):
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            cursor.insertText('<%s>\n' % (t))

    def consel(self, text, color):
        self.tips()

        # 获取当前文本光标
        cursor = self.textCursor()

        # 创建文本字符格式，设置颜色
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        cursor.setCharFormat(char_format)

        for line in text.strip().split('\n'):
            cursor.insertText(f"> {line} \n")

        self.last_time = time.mktime(time.localtime())
        ## 恢复默认字符格式
        #cursor.setCharFormat(QTextCharFormat())

        # 每当文本内容更新时，滚动到底部
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

