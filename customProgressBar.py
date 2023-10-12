import sys
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt

class CustomProgressBar(QProgressBar):
    def setValue(self, value, threshold=None, color_below=None, color_above=None):
        if threshold is not None and color_below is not None and color_above is not None:
            self.threshold = threshold
            self.color_below = color_below
            self.color_above = color_above
        super().setValue(value)

    def paintEvent(self, event):
        painter = self.style().standardPalette()

        # 获取进度条的已完成值
        progress = self.value()
        
        # 根据进度值选择颜色
        if progress < self.threshold:
            painter.setColor(QProgressBar.Text, self.color_below)
            painter.setColor(QProgressBar.Foreground, self.color_below)
        else:
            painter.setColor(QProgressBar.Text, self.color_above)
            painter.setColor(QProgressBar.Foreground, self.color_above)

        # 根据进度值选择颜色
        if progress < 30:
            # 未完成部分颜色
            painter.setColor(QProgressBar.Text, Qt.red)
            painter.setColor(QProgressBar.Foreground, Qt.red)
        elif progress >= 30 and progress < 70:
            # 已成功完成部分颜色
            painter.setColor(QProgressBar.Text, Qt.green)
            painter.setColor(QProgressBar.Foreground, Qt.green)
        else:
            # 已错误完成部分颜色
            painter.setColor(QProgressBar.Text, Qt.blue)
            painter.setColor(QProgressBar.Foreground, Qt.blue)

        self.setPalette(painter)
        super(CustomProgressBar, self).paintEvent(event)