# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connect_me.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
#��������������������
import sys
import os
import copy
import subprocess
import signal
import time
import collections
from configparser import ConfigParser

#PyQt5��������������������PyQt5.QtWidgets������
#from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import sip
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from xml.etree import ElementTree as ET

#����designer����������login����
from uvs import Ui_smt
import webChannel
from DiagTable import DiagTable
from workerThread import MutiWorkThread
from custom_widget import *
#from ico import icon
from web_rc import qInitResources

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QComboBox, QSpinBox
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEngineSettings


class MyMainForm(QMainWindow, Ui_smt):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        self.version = '如有疑问, 请联系 chaozhanghu@phytium.com.cn  @Qsmtool 23.09-0003'
        qInitResources()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 设置窗口关闭策略为允许通过关闭按钮关闭
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # System Setting
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.cfg_file       = os.getenv('BASE_CONFIG_FILE')
        self.usr_cfg_file   = os.getenv('USER_CONFIG_FILE')
        self.saveDir        = os.getenv('CONFIG_SAVE_DIR')
        self.svgfile        = os.getenv('SVG_FILE')
        TB_HOME             = os.getenv('TB_HOME')
        CBS_HOME            = os.getenv('CBS_HOME')

        cmn_setting_file = os.path.join(CBS_HOME,'testbench/uvs.ini')
        if not os.path.exists(cmn_setting_file):
            print('uvs.ini文件缺失!')
        self.cmn_config = ConfigParser()
        self.cmn_config.read(cmn_setting_file)

        self.simulateCMD = collections.OrderedDict()
        self.simulateCMD = {'clean':None,'build':None,'compiler':None,'elab':None,'sim':None,
                            'run':None,'ml=1':None,'gui=1':None,"fsdb=1":None,'wave':None,
                            'EDA云':None}

        max_threads_list = ['5', '10', '20', '50', '100']
        self.comboBox_threads.addItems(max_threads_list)
        tools_list = ['xrun', 'vcs']
        self.comboBox_tool.addItems(tools_list)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Create Console Window
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.textBrowser = ColoredTextBrowser(self.Consel)
        font = QFont()
        font.setFamily("Monospace")
        font.setPointSize(9)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_5.addWidget(self.textBrowser,1)

        self.lineEdit_cmd = QLineEdit()
        self.lineEdit_cmd.setMinimumSize(QSize(2, 2))
        self.lineEdit_cmd.setClearButtonEnabled(True)
        self.lineEdit_cmd.setObjectName("lineEdit_cmd")
        self.verticalLayout_5.addWidget(self.lineEdit_cmd,0)
        self.lineEdit_cmd.returnPressed.connect(self.executeCommand)
        # 设置占位符文本
        self.lineEdit_cmd.setPlaceholderText("输入shell命令...")

        # 创建一个QCompleter并关联到QLineEdit
        completer = QCompleter(['ls', 'make', 'git', 'cd', 'cat', 'grep'], self)
        self.lineEdit_cmd.setCompleter(completer)

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handleProcessOutput)
        self.process.readyReadStandardError.connect(self.handleProcessError)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 创建一个web界面
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        #self.main_tabWidget.addTab(self.web_view, "HTML")
        # 创建 QWebEngineView 组件
        self.web_view = QWebEngineView()
        self.main_tabWidget.setTabText(0, "仿真配置")
        self.scrollArea_svg.setWidget(self.web_view)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 增加web与qt程序之间的数据通道
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.data_obj = webChannel.DataObject(self.textBrowser)

        # 将数据对象添加到Web通道
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("dataObj", self.data_obj)
        self.web_view.page().setWebChannel(self.web_channel)


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 加载web界面
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        #self.web_view.loadFinished.connect(self.loadFinished)
        #self.web_view.loadProgress.connect(self.loadProgress)
        #url = QUrl.fromLocalFile(os.path.join(os.getenv("SMT_HOME"),"web/qtconfig.html"))
        #self.web_view.setUrl(url)
        self.web_view.setUrl(QUrl("qrc:/web/qtconfig.html"))

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 打开外部网页, 用以集成内网各平台环境
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        ## 创建 QWebEngineView 组件
        #self.baidu_view = QWebEngineView()
        #self.main_tabWidget.addTab(self.baidu_view, "搜索引擎")
        #self.baidu_view.setUrl(QUrl("http://www.baidu.com"));

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 创建一个文件浏览器
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.dir_model = QFileSystemModel()
        self.dir_model.setReadOnly(True)

        #self.current_path = QDir.currentPath()
        self.current_path = os.getenv('CBS_HOME')
        self.dir_model.setRootPath(self.current_path)
        self.treeView_filebrowser.setModel(self.dir_model)
        self.treeView_filebrowser.setRootIndex(self.dir_model.index(self.current_path))

        self.treeView_filebrowser.setColumnWidth(0, 300)

        # create right menu
        self.treeView_filebrowser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView_filebrowser.customContextMenuRequested.connect(self.creat_rightmenu)
        # double click
        self.treeView_filebrowser.doubleClicked.connect(self.doubleClickedRightmenu)
        
        # tooltip
        QToolTip.setFont(QFont('SansSerif',9))
        self.treeView_filebrowser.setToolTip('双击或单击右键可调出菜单')

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 创建线程池
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.mutiWorkThreads = MutiWorkThread(self)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Create Diag Table
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.load_diag_table = DiagTable(self)

        # 连接文本框的文本更改事件到过滤函数
        self.lineEdit.textChanged.connect(self.load_diag_table.filterTable)
        # 设置占位符文本
        self.lineEdit.setPlaceholderText("Filter..")

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Set statusbar information
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.statusbar.showMessage(self.version, 0)
        self.statusbar.show()

        #********************************************************
        # connect buttons and function 
        #********************************************************
        # 仿真运行按键
        self.run.clicked.connect(self.runSimulate)

        # 停止运行指定测试项
        self.stopSimuate.clicked.connect(self.stopSimuateFunc)

        ## 保存diag文件
        self.saveDiag.clicked.connect(self.load_diag_table.saveDiagFunc)

        ## 全选diag items
        self.selectalltc.clicked.connect(self.load_diag_table.selectalltcFunc)

        ## reload items
        self.reload.clicked.connect(self.load_diag_table.reloadDiagFile)

        # action "Exit"
        self.actionExit.triggered.connect(self.exitGui)

        # action "refresh file browser"
        self.actionreload.triggered.connect(self.load_diag_table.refreshFileBrowser)

        self.actionUVSWeb.triggered.connect(self.loadWeb)

        self.actionDcodeWeb.triggered.connect(self.loadWeb)

        self.actionDoc.triggered.connect(self.loadWeb)

        self.actionvproject.triggered.connect(self.loadWeb)

        self.actionreg.triggered.connect(self.loadWeb)

        #********************************************************
        # connect checkboxs and function 
        #********************************************************
        self.cloudCB.stateChanged.connect(self.connectCMDCB)
        self.cleanCB.stateChanged.connect(self.connectCMDCB)
        self.updateconfigsCB.stateChanged.connect(self.connectCMDCB)
        self.buildCB.stateChanged.connect(self.connectCMDCB)
        self.compiler.stateChanged.connect(self.connectCMDCB)
        self.simu_runCB.stateChanged.connect(self.connectCMDCB)
        self.simu_elabCB.stateChanged.connect(self.connectCMDCB)
        self.simu_simCB.stateChanged.connect(self.connectCMDCB)
        self.mlCB.stateChanged.connect(self.connectCMDCB)
        self.guiCB.stateChanged.connect(self.connectCMDCB)
        self.fsdbCB.stateChanged.connect(self.connectCMDCB)
        self.coverCB.stateChanged.connect(self.connectCMDCB)
        self.verdiCB.stateChanged.connect(self.connectCMDCB)
        self.quitCB.stateChanged.connect(self.connectCMDCB)

        self.load_diag_table.refreshFileBrowser()
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #   xxxxxxxxxx      Functions       xxxxxxxxxxxx
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def loadWeb(self):
        # 获取发送信号的 QAction
        sender_action = self.sender()

        if self.main_tabWidget.count() == 4:
            self.main_tabWidget.removeTab(3)

        webView = QWebEngineView()
        self.main_tabWidget.addTab(webView, f"{sender_action.text()}网页")
        self.main_tabWidget.setCurrentIndex(3)

        # 从配置文件中获取窗口参数
        if self.cmn_config.has_section('Webs'):
            webs_settings = self.cmn_config['Webs']
            # 区分不同的 QAction
            if sender_action.text() == "uvs":
                url = webs_settings.get('uvs_gitlab')
            elif sender_action.text() == "RTL":
                url = webs_settings.get('design_code_gitlab')
            elif sender_action.text() == "Doc":
                url = webs_settings.get('design_doc_gitlab')
            elif sender_action.text() == "vpj":
                url = webs_settings.get('vproject_gitlab')
            elif sender_action.text() == "reg":
                url = webs_settings.get('regs_gitlab')

            webView.setUrl(QUrl(url))

    #********************************************************
    # 运行shell命令
    #********************************************************
    def executeCommand(self):
        command = self.lineEdit_cmd.text()
        self.lineEdit_cmd.clear()

        cur_dir = self.dir_model.filePath(self.treeView_filebrowser.currentIndex())
        command = f"cd {cur_dir}; {command}"
        self.textBrowser.consel(command, 'green')

        self.process.start('bash', ['-c', command])

    def handleProcessOutput(self):
        output = self.process.readAllStandardOutput()
        output_text = str(output, encoding='utf-8')
        self.textBrowser.consel(output_text, 'black')

    def handleProcessError(self):
        error = self.process.readAllStandardError()
        error_text = str(error, encoding='utf-8')
        self.textBrowser.consel(error_text, 'black')

    #********************************************************
    # 运行仿真：1. 收集参数；2. 批量处理任务； 3. 收集运行结果；
    #********************************************************
    def runSimulate(self):
        current_progress = self.progressBar.value()
        if current_progress > 0 and current_progress < 100:
            self.textBrowser.consel('上次发布的任务还没有结束，需要发布新任务，请等待或开新的SMT窗口.', 'red')
            return

        #self.progressBar.setStyleSheet("")  # 清空样式表
        cmd = self.collectOpts()
        self.mutiWorkThreads.run(cmd)

    def SingleRunSimulate(self):
        cmd = self.collectOpts()
        self.mutiWorkThreads.singleRun(cmd)

    #********************************************************
    # 运行仿真：1. 收集参数；
    #********************************************************
    def collectOpts(self):
        ## 1. 收集参数
        if self.simulateCMD['EDA云']:
            cmd = 'bsub -Is make '
        else:
            cmd = 'make '
        cmd += f"tool={self.comboBox_tool.currentText()} "
        for key,value in self.simulateCMD.items():
            if value:
                if key == 'EDA云':
                    continue
                else:
                    cmd += key + ' '
        
        return cmd

    #********************************************************
    # 运行仿真：1. 收集参数；
    #********************************************************
    def connectCMDCB(self):
        sender = self.sender()  # 获取发出信号的复选框
        if sender is not None and isinstance(sender, QCheckBox):
            if sender.isChecked():
                self.simulateCMD[sender.text()] = True
            else:
                self.simulateCMD[sender.text()] = False

    #********************************************************
    # 停止仿真：1. 收集参数；2. 批量处理任务； 3. 收集运行结果；
    #********************************************************
    def stopSimuateFunc(self):
        self.mutiWorkThreads.stop()

    def singleStopSimulateFunc(self):
        self.mutiWorkThreads.singleStop()

    #********************************************************
    # 自定义关闭串口前的动作
    #********************************************************
    def closeEvent(self, event):
        # 在关闭窗口前执行自定义动作
        confirm = self.confirmation_dialog()
        if confirm:
            if os.path.exists(QDir.homePath()+'/.current_setting.cbs'):
                os.system('rm %s' % (QDir.homePath()+'/.current_setting.cbs'))
            event.accept()  # 允许关闭窗口
            self.stopSimuateFunc()
        else:
            event.ignore()  # 取消关闭窗口

    #********************************************************
    # 关机确认菜单
    #********************************************************
    def confirmation_dialog(self):
        # 创建一个确认对话框
        confirm_dialog = QMessageBox()
        confirm_dialog.setIcon(QMessageBox.Question)
        confirm_dialog.setWindowTitle("确认关闭窗口")
        confirm_dialog.setText("是否确定关闭窗口?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)

        # 显示对话框并等待用户的选择
        user_choice = confirm_dialog.exec_()

        # 根据用户的选择返回True或False
        if user_choice == QMessageBox.Yes:
            return True
        else:
            return False

    def exitGui(self):
        self.close()

    def loadFinished(self, ok):
        if not ok:
            print("页面加载失败")

    def loadProgress(self, progress):
        print("加载进度:", progress)

    def openFileBrowser(self, tool):
        index = self.treeView_filebrowser.currentIndex()
        #if index.isValid() and not self.dir_model.isDir(index):
        if not index.isValid():
            return
        file_name = self.dir_model.filePath(index)
        self.textBrowser.consel(f"{tool}打开 {file_name}", 'black')
        self.statusbar.showMessage(f"{tool}打开 {file_name}")
        self.statusbar.show()

        if tool == 'Gvim':
            cmd = f"gvim {file_name} &"
        elif tool == 'vscode':
            cmd = f"code {file_name} &"
        elif tool == 'Simvision':
            cmd = f"simvision -64bit {file_name} &"
        elif tool == 'Verdi':
            cmd = f"verdi -ssf {file_name} &"

        os.system(cmd)

    def openWithGvim(self):
        self.openFileBrowser("Gvim")
        self.statusbar.showMessage(self.version, 0)
        self.statusbar.show()

    def openWithCode(self):
        self.openFileBrowser("vscode")

    def openWithSimvision(self):
        self.openFileBrowser("Simvision")

    def openWithVerdi(self):
        self.openFileBrowser("Verdi")

    def doubleClickedRightmenu(self):
        index = self.treeView_filebrowser.currentIndex()
        if index.isValid() and self.dir_model.isDir(index):
            return
        else:
            self.creat_rightmenu()

    def creat_rightmenu(self):
        self.treeView_menu=QMenu(self)

        self.actionA = QAction(u'Open With Gvim',self)
        self.actionA.triggered.connect(self.openWithGvim)

        self.actionCode = QAction(u'Open With Code',self)
        self.actionCode.triggered.connect(self.openWithCode)

        self.actionSimvsion = QAction(u'Open With Simvision',self)
        self.actionSimvsion.triggered.connect(self.openWithSimvision)

        self.actionVerdi = QAction(u'Open With Verdi',self)
        self.actionVerdi.triggered.connect(self.openWithVerdi)

        self.treeView_menu.addAction(self.actionA)
        self.treeView_menu.addAction(self.actionCode)
        self.treeView_menu.addAction(self.actionSimvsion)
        self.treeView_menu.addAction(self.actionVerdi)
        self.treeView_menu.popup(QCursor.pos())


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    ## 设置Qt::AA_UseOpenGLES属性
    QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)

    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)

    QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

    exe_path = os.path.dirname(sys.executable)
    QCoreApplication.addLibraryPath(exe_path)
    #初始化
    myWin = MyMainForm()
    #将窗口控件显示在屏幕上
    myWin.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
