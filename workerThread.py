#!/bin/env python3
# _*_ coding: UTF-8 _*_
import sys
import os
import re
import subprocess
import psutil
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class WorkerThread(QThread):
    finished = pyqtSignal(str)  # 任务完成信号
    error = pyqtSignal(str)  # 任务完成信号

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            # 去除stdout，大量的stdout会塞满PIPE，导致子进程卡死
            #self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.process = subprocess.Popen(self.command, shell=True, stderr=subprocess.PIPE)

            self.task =  f"任务 {self.command} 子进程pid {self.process.pid}"
            self.finished.emit(f"[Info] {self.task} 开始执行.")  # 发射任务完成信号
            # 等待子进程完成
            return_code = self.process.wait()  # 等待外部进程执行完成
            if return_code == 0:
                self.finished.emit(f"[Success] {self.task} 执行完成.")  # 发射任务完成信号
            else:
                self.finished.emit(f"[ERROR] {self.task} 执行错误 \n")  # 发射任务完成信号
                error_info = f" \n{self.task} 异常退出 (返回码 {return_code}) \n" 
                # 获取错误信息
                stderr_output = self.process.stderr.read()
                if stderr_output:
                    error_info += f"错误信息:\n{stderr_output.decode('utf-8')}\n"

                ## 获取标准输出信息
                #stdout_output = self.process.stdout.read()
                #if stdout_output:
                #    error_info += f"标准输出信息:\n{stdout_output.decode('utf-8')}\n"

                self.error.emit(error_info)
        except Exception as e:
            # 发射错误信息信号
            self.error.emit(f"任务发布失败: {str(e)} \n")

    def stop(self):
        if hasattr(self, "process") and self.process.poll() is None:
            parent = psutil.Process(self.process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            # 终止 subprocess 进程
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.finished.emit(f"[Stopped] 子进程 {self.command} 提前结束.")  # 发射任务完成信号

class MutiWorkThread():
    def __init__(self, table, consol, progressBar):
        super().__init__()
        self.table = table
        self.consol = consol
        self.progressBar = progressBar
        self.finishedTasks = 0

    def run(self, cmd):
        # 定义要执行的命令列表，每个元素是一个命令字符串
        self.commands = self.collectCMDs(cmd)
        
        if len(self.commands):
            self.progressBar.setValue(1)

        # 存储子进程的 Popen 对象
        self.threads = []

        # 启动子进程并存储 Popen 对象
        for command in self.commands:
            thread = WorkerThread(command)
            thread.finished.connect(self.taskFinished)
            thread.error.connect(self.taskError)
            self.threads.append(thread)
            thread.start()

    def stop(self):
        for thread in self.threads:
            thread.stop()

    def taskFinished(self, testcaseStr):
        if '[Success]' in testcaseStr:
            status = 'green'
        elif '[Stopped]' in testcaseStr:
            status = 'orange'
        elif '[Info]' in testcaseStr:
            status = 'black'
        else:
            status = 'red'
        self.consol.consel(testcaseStr, status)

        self.tagProcessStatus(testcaseStr)

        if status == 'black':
            return

        self.finishedTasks = self.finishedTasks + 1
        progress_value = (self.finishedTasks / len(self.threads)) * 100
        self.progressBar.setValue(int(progress_value))

    def taskError(self, error_info):
        self.consol.consel(error_info, 'red')

        self.finishedTasks = self.finishedTasks + 1
        progress_value = (self.finishedTasks / len(self.threads)) * 100
        self.progressBar.setValue(int(progress_value))
        style = "QProgressBar::chunk { background-color: orange; }"  # 设置已完成部分的颜色
        style += "QProgressBar {border: 2px solid grey; border-radius: 5px; background: lightgrey;}" 
        style += "QProgressBar { text-align: center; }"  # 设置文本居中
        self.progressBar.setStyleSheet(style)
        
    def tagProcessStatus(self, statusStr):
        test_pattern = re.compile(r"test=(.+?) ")
        if '[Info]' in statusStr:
            return

        finishedItem = test_pattern.findall(statusStr)[0]

        if '[Success]' in statusStr:
            status = True
        else:
            status = False 

        for row in range(self.table.rowCount()):
            matchedItem = self.table.item(row, 2)
            if finishedItem == matchedItem.text():
                if status:
                    icon = ":/ico/check-mark.png"
                else:
                    icon = ":/ico/error.png"

                statusItem = self.table.item(row, 0)
                pixmap = QPixmap(icon)
                statusItem.setIcon(QIcon(pixmap))

    def checkProcessStatus(self):
        # 监控每个子进程的状态
        for i, thread in enumerate(self.threads):
            return_code = thread.process.poll()  # 获取子进程的返回码

            if return_code is None:
                self.consol.consel(f"子进程 {self.commands[i]}: 仍在运行", 'black')
            elif return_code == 0:
                self.consol.consel(f"子进程 {self.commands[i]}: 执行成功", 'green')
            else:
                self.consol.consel(f"子进程 {self.commands[i]}: 执行失败 (返回码 {return_code}", 'black')
    
    def collectCMDs(self, cmd):
        selected_items = self.collectItems()

        cmds = []
        for item in selected_items:
            cmds.append(cmd + ' test=' + item)
        
        return cmds

    def collectItems(self):
        # 遍历表格的行
        selected_items = []
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 0)
            item = self.table.item(row, 1)
            if item.checkState() == Qt.Checked:
                selected_items.append(self.table.item(row, 2).text())
                # 创建QPixmap对象并设置图像
                pixmap = QPixmap(":/ico/loading.png")
                status_item.setIcon(QIcon(pixmap))

        return selected_items
