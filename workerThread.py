#!/bin/env python3
# _*_ coding: UTF-8 _*_
import sys
import os
import re
import subprocess
import psutil
import queue
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class WorkerThread(QThread):
    finished = pyqtSignal(str)  # 任务完成信号
    error = pyqtSignal(str)  # 任务完成信号
    outputReceived = pyqtSignal(str) 

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            # bug记录：去除stdout，大量的stdout会塞满PIPE，导致子进程卡死
            self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.task =  f"任务 {self.command} 子进程pid {self.process.pid}"
            self.finished.emit(f"[Info] {self.task} 开始执行.")  # 发射任务完成信号

            while True:
                output = self.process.stdout.readline()
                if output.decode('utf-8') == '' and self.process.poll() is not None:
                    break
                if output.decode('utf-8'):
                    self.outputReceived.emit(output.decode('utf-8'))

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
            self.finished.emit(f"[Stopped] 任务 {self.command} 提前结束.")  # 发射任务完成信号

class MutiWorkThread():
    def __init__(self, smtui):
        super().__init__()

        self.smtui = smtui
        self.table = smtui.diag_table
        self.consol = smtui.textBrowser
        self.progressBar = smtui.progressBar
        self.resultBrowser = smtui.textBrowser_result

        self.finishedTasks = 0
        self.thread_queue = queue.Queue()
        self.test_record = {}
        self.task_status_record = {}

        self.test_pattern = re.compile(r"test=(.+?) ")
        # 存储子进程的 Popen 对象
        self.threads = []

        self.error_style = "QProgressBar::chunk { background-color: orange; }"  # 设置已完成部分的颜色
        self.error_style += "QProgressBar {border: 2px solid grey; border-radius: 5px; background: lightgrey;}" 
        self.error_style += "QProgressBar { text-align: center; }"  # 设置文本居中

        self.finished_style = "QProgressBar::chunk { background-color: green; }"  # 设置已完成部分的颜色
        self.finished_style += "QProgressBar {border: 2px solid grey; border-radius: 5px; background: lightgrey;}" 
        self.finished_style += "QProgressBar { text-align: center; }"  # 设置文本居中

    def singleRun(self, cmd):
        commands = self.collectSingleRunCMDs(cmd)
        self.consol.consel(f"新增任务到进程池，该操作将扩展 {len(commands)} 并行进程数. \n", 'black')

        for item in commands:
            self.creat_thread(item)

        self.updateProgress()

    def run(self, cmd):
        self.max_threads = int(self.smtui.comboBox_threads.currentText())
        self.consol.consel(f"设置最大并行任务数 {str(self.max_threads)}\n", 'black')
        self.thread_count = 0

        self.consol.consel(f"queue:{self.thread_queue.qsize()}\n",'black')
        self.consol.consel(f"count:{self.thread_count}\n",'black')
        self.consol.consel(f"finished:{self.finishedTasks}\n",'black')
        self.consol.consel(f"threads:{len(self.threads)}\n",'black')
        # 定义要执行的命令列表，每个元素是一个命令字符串
        self.commands = self.collectCMDs(cmd)
        
        # 启动子进程并存储 Popen 对象
        for item in self.commands:
            self.thread_queue.put(item)

        while self.thread_count < self.max_threads and self.thread_count <= self.thread_queue.qsize():
            cur_cmd = self.thread_queue.get()
            self.creat_thread(cur_cmd)
            self.thread_count += 1

        # update progress bar
        self.updateProgress()

    def creat_thread(self, cmd):
        thread = WorkerThread(cmd)
        thread.finished.connect(self.taskFinished)
        thread.error.connect(self.taskError)
        thread.outputReceived.connect(self.taskResult)
        self.threads.append(thread)
        thread.start()

        #修改状态标记
        if not len(self.test_pattern.findall(cmd)):
            return
        cur_test = self.test_pattern.findall(cmd)[0].strip()
        status_item = self.table.item(self.test_record[cur_test], 0)
        # 创建QPixmap对象并设置图像
        pixmap = QPixmap(":/ico/loading.png")
        status_item.setIcon(QIcon(pixmap))

    def stop(self):
        while self.thread_queue.qsize():
            pending_cmd = self.thread_queue.get()
            cmd_status = f"[Stopped] 任务 {pending_cmd} 提前结束. \n"
            self.consol.consel(cmd_status, 'orange')

            self.tagProcessStatus(cmd_status)

            self.finishedTasks = self.finishedTasks + 1
            self.updateProgress()

        for thread in self.threads:
            if thread.poll() is not None:
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
        self.updateProgress()

        # 启动下一个补位的thread
        if not self.thread_queue.empty():
            next_cmd = self.thread_queue.get()
            self.creat_thread(next_cmd)

    def taskError(self, error_info):
        self.consol.consel(error_info, 'red')

        #self.finishedTasks = self.finishedTasks + 1
        #self.updateProgress()
        #self.progressBar.setStyleSheet(self.error_style)
        
        ## 启动下一个补位的thread
        #if not self.thread_queue.empty():
        #    next_cmd = self.thread_queue.get()
        #    self.creat_thread(next_cmd)

    def updateProgress(self):
        if self.progressBar.value() == 0:
            self.progressBar.setValue(1)
            self.progressBar.setStyleSheet(self.finished_style)

        for key,value in self.task_status_record.items():
            if not value:
                self.progressBar.setStyleSheet(self.error_style)
            else:
                self.progressBar.setStyleSheet(self.finished_style)

        progress_value = (self.finishedTasks / len(self.threads)) * 100
        self.progressBar.setValue(int(progress_value))

    def taskResult(self, result):
        ## 检查当前行数是否超过上限
        #if self.result_line_count >= self.result_max_lines:
        #    # 删除旧的行，保留最新的行
        #    cursor = self.resultBrowser.textCursor()
        #    cursor.movePosition(QTextCursor.Start)
        #    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, self.result_line_count - self.result_max_lines)
        #    cursor.removeSelectedText()
        #    self.result_line_count = self.result_max_lines - 1

        cursor = self.resultBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(result)
        #self.result_line_count += 1
        self.resultBrowser.setTextCursor(cursor)
        self.resultBrowser.ensureCursorVisible()

    def tagProcessStatus(self, statusStr):
        if '[Info]' in statusStr:
            return

        finishedItem = self.test_pattern.findall(statusStr)[0]

        if '[Success]' in statusStr:
            status = True
        else:
            status = False 

        for row in range(self.table.rowCount()):
            matchedItem = self.table.item(row, 2)
            if finishedItem == matchedItem.text():
                if status:
                    icon = ":/ico/check-mark.png"
                    self.task_status_record[finishedItem] = True
                else:
                    icon = ":/ico/error.png"
                    self.task_status_record[finishedItem] = False

                statusItem = self.table.item(row, 0)
                check_item = self.table.item(row, 1)
                pixmap = QPixmap(icon)
                statusItem.setIcon(QIcon(pixmap))
                check_item.setFlags(check_item.flags() | Qt.ItemIsUserCheckable)  # add Qt.ItemIsUserCheckable 标志

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
    
    def collectSingleRunCMDs(self, cmd):
        cmds = []
        selected_items = []
        # 新增一行并复制当前选中的行
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        for row in selected_rows:
            selected_items.append(self.table.item(row, 2).text())
            self.test_record[self.table.item(row, 2).text()] = row

        for item in selected_items:
            cmds.append(cmd + ' test=' + item + ' ')
        
        return cmds

    def collectCMDs(self, cmd):
        selected_items = self.collectItems()

        cmds = []
        for item in selected_items:
            cmds.append(cmd + ' test=' + item + ' ')
        
        return cmds

    def collectItems(self):
        # 遍历表格的行
        selected_items = []
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 0)
            check_item = self.table.item(row, 1)
            if check_item.checkState() == Qt.Checked:
                selected_items.append(self.table.item(row, 2).text())
                self.test_record[self.table.item(row, 2).text()] = row
                # 创建QPixmap对象并设置图像
                pixmap = QPixmap(":/ico/parcel.png")
                status_item.setIcon(QIcon(pixmap))
                check_item.setFlags(check_item.flags() & ~Qt.ItemIsUserCheckable)  # 移除 Qt.ItemIsUserCheckable 标志

        return selected_items
