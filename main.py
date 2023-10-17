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

#PyQt5��������������������PyQt5.QtWidgets������
#from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import sip
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from xml.etree import ElementTree as ET

#����designer����������login����
from uvs import Ui_smt
import extractDiag
import webChannel
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

        qInitResources()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 设置窗口关闭策略为允许通过关闭按钮关闭
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # System Setting
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.cfg_file = os.getenv('BASE_CONFIG_FILE')
        self.usr_cfg_file = os.getenv('USER_CONFIG_FILE')
        self.saveDir = os.getenv('CONFIG_SAVE_DIR')
        self.svgfile = os.getenv('SVG_FILE')
        self.diag_file = os.getenv('DIAG_FILE')

        self.reloadDiagEvent = False
        self.saveDiagEvent = False

        #self.html_file = os.getenv('HTML_FILE')
        #self.saveDir = os.path.abspath(os.path.join(os.getcwd(), "../config"))

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Create Console Window
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.textBrowser = ColoredTextBrowser(self.Consel)
        font = QFont()
        font.setFamily("Monospace")
        font.setPointSize(9)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_5.addWidget(self.textBrowser)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 启动后台CGI服务
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 要执行的外部命令
        #cgi_path = os.path.abspath(os.path.join(os.getcwd(), "verif_config"))
        #command = "cd %s; python2 -m CGIHTTPServer 8008  > ~/.uvs/cgihttp.out" % (cgi_path)

        # 使用subprocess.Popen()创建非阻塞子进程
        #self.process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

        # 获取命令的标准输出和标准错误
        #stdout_data, stderr_data = process.communicate()
        #self.textBrowser.consel(process.stdout, 'black')
        #self.textBrowser.consel(process.stderr, 'black')

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
        self.treeView_filebrowser.doubleClicked.connect(self.creat_rightmenu)
        
        # tooltip
        QToolTip.setFont(QFont('SansSerif',9))
        self.treeView_filebrowser.setToolTip('双击或单击右键可调出菜单')

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Create Diag Table
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 设置选择模式为整行选择
        self.diag_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 隐藏行序号
        self.diag_table.verticalHeader().setVisible(False)
        # 连接表头点击信号
        #self.diag_table.horizontalHeader().sectionClicked.connect(self.onHeaderClicked)

        # 设置表头标签
        self.diag_table.setColumnCount(10)
        self.table_header = [" ", " ",
                        "testcase*", 
                        "path*", 
                        "config*",
                        "scp",
                        "comp_argvs",
                        "run_argvs",
                        "run_boards",
                        "argv"]
        self.diag_table.setHorizontalHeaderLabels(self.table_header)

        self.fillDataForTable()

        # 连接到itemChanged信号
        self.diag_table.itemChanged.connect(self.handleItemChanged)
        # 连接文本框的文本更改事件到过滤函数
        self.lineEdit.textChanged.connect(self.filterTable)
        # 设置占位符文本
        self.lineEdit.setPlaceholderText("Filter..")

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

        # 为表格添加右键菜单
        self.diag_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.diag_table.customContextMenuRequested.connect(self.diagTableContextMenu)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Set statusbar information
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.statusbar.showMessage('如有疑问, 请联系 chaozhanghu@phytium.com.cn  @Qsmtool 23.09-0001', 0)
        self.statusbar.show()

        #********************************************************
        # connect buttons and function 
        #********************************************************
        # 仿真运行按键
        self.run.clicked.connect(self.runSimulate)

        # 停止运行指定测试项
        self.stopSimuate.clicked.connect(self.stopSimuateFunc)

        ## 保存diag文件
        self.saveDiag.clicked.connect(self.saveDiagFunc)

        ## 全选diag items
        self.selectalltc.clicked.connect(self.selectalltcFunc)

        ## reload items
        self.reload.clicked.connect(self.reloadDiagFunc)

        # action "Exit"
        self.actionExit.triggered.connect(self.exitGui)

        # action "refresh file browser"
        self.actionreload.triggered.connect(self.refreshFileBrowser)

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #   xxxxxxxxxx      Functions       xxxxxxxxxxxx
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #********************************************************
    # 填充diag table的内容
    #********************************************************
    def fillDataForTable(self):
        self.diag_info = extractDiag.extractDiag(self.diag_file)
        self.textBrowser.consel("加载diag文件成功!", 'green')

        # 设置初始行数和列数
        line_nums = len(self.diag_info)
        self.diag_table.setRowCount(line_nums)

        self.previous_data = [[str(cellData) for cellData in row] for row in self.diag_info]

        for row, rowData in enumerate(self.diag_info):
            path_exist = False
            for col, cellData in enumerate(rowData):
                item = QTableWidgetItem(str(cellData))
                self.diag_table.setItem(row, col+2, item)
                if col==0:
                    simdir_path = os.path.join(os.getcwd(),'simdir',str(cellData))
                if col==0 and os.path.exists(simdir_path):
                    path_exist = True

            # 创建一个QCheckBox并将其放入单元格
            checkbox = QTableWidgetItem()
            checkbox.setFlags(checkbox.flags() | Qt.ItemIsUserCheckable)
            checkbox.setCheckState(Qt.Unchecked)
            self.diag_table.setItem(row, 1, checkbox)

            # 设置元格Item
            statusItem = QTableWidgetItem()
            if path_exist:
                pixmap = QPixmap(":/ico/checkmark.png")
            else:
                pixmap = QPixmap(":/ico/null.png")
            statusItem.setIcon(QIcon(pixmap))
            self.diag_table.setItem(row, 0, statusItem)

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

    #********************************************************
    # 当diag table发生编辑时，触发相关函数 1. 改变背景颜色；
    #********************************************************
    def handleItemChanged(self, item):
        if item and item.column() < 2:
            return

        # 只在文本更改时更改背景颜色
        if not self.reloadDiagEvent and not self.saveDiagEvent:
            item.setBackground(QColor("orange"))

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

    #********************************************************
    # 运行仿真：1. 收集参数；2. 批量处理任务； 3. 收集运行结果；
    #********************************************************
    def runSimulate(self):
        current_progress = self.progressBar.value()
        if current_progress > 0 and current_progress < 100:
            self.textBrowser.consel('上次发布的任务还没有结束，需要发布新任务，请等待或开新的SMT窗口.', 'red')
            return

        self.progressBar.setStyleSheet("")  # 清空样式表
        cmd = self.collectOpts()
        self.mutiWorkThreads = MutiWorkThread(self.diag_table, self.textBrowser, self.progressBar)
        self.mutiWorkThreads.run(cmd)

    #********************************************************
    # 运行仿真：1. 收集参数；
    #********************************************************
    def collectOpts(self):
        # 1. 收集参数
        if self.cloudCB.isChecked():
            cmd = 'bsub make '
        else:
            cmd = 'make '
        if self.cleanCB.isChecked():
            cmd = cmd + 'clean '
        if self.updateconfigsCB.isChecked():
            cmd = cmd + 'updateconfigs '
        if self.buildCB.isChecked():
            cmd = cmd + 'build '
        if self.compiler.isChecked():
            cmd = cmd + 'compiler '
        if self.simu_runCB.isChecked():
            cmd = cmd + 'run '
        if self.simu_elabCB.isChecked():
            cmd = cmd + 'elab '
        if self.simu_simCB.isChecked():
            cmd = cmd + 'sim '
        if self.pldcompCB.isChecked():
            cmd = cmd + 'comp '
        if self.pld_runCB.isChecked():
            cmd = cmd + 'run '
        if self.mlCB.isChecked():
            cmd = cmd + 'ml=1 '
        
        return cmd
    #********************************************************
    # 停止仿真：1. 收集参数；2. 批量处理任务； 3. 收集运行结果；
    #********************************************************
    def stopSimuateFunc(self):
        self.mutiWorkThreads.stop()

    #********************************************************
    # 重新加载diag文件
    #********************************************************
    def reloadDiagFunc(self):
        self.reloadDiagEvent = True
        self.textBrowser.consel("刷新diag表信息.","green")
        self.diag_table.setSortingEnabled(False)
        self.diag_table.clearContents()
        self.diag_table.setRowCount(0)
        self.fillDataForTable()
        self.diag_table.repaint()
        self.diag_table.setSortingEnabled(True)
        self.reloadDiagEvent = False

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

    #********************************************************
    # 保存diag文件
    #********************************************************
    def saveDiagFunc(self):
        self.saveDiagEvent = True
        fout = open(self.diag_file, 'w+')
        fout.write("// 以下为SMT自动生成内容, 遵循diag语法规则, 可以自行编辑该文件.\n\n")

        for row in range(self.diag_table.rowCount()):
            for col in range(self.diag_table.columnCount()):
                if col <= 1:
                    continue
                colData = self.diag_table.item(row,col).text()
                if col==2:
                    fout.write(colData + ' ')
                elif col in [3,4,5]:
                    fout.write(self.table_header[col].strip('*')+'='+colData+' ')
                elif col >= 6:
                    fout.write(self.table_header[col]+'=\''+colData+'\' ')
                self.diag_table.item(row,col).setBackground(QColor(255, 255, 255))  # 恢复默认背景颜色
            fout.write('\n\n')

        self.saveDiagEvent = False
        self.textBrowser.consel('Diag文件保存成功.', 'green')

    def selectalltcFunc(self):
        current_state = self.diag_table.item(0, 1).checkState()
        for row in range(self.diag_table.rowCount()):
            item = self.diag_table.item(row, 1)
            if current_state == Qt.Unchecked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

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

    #********************************************************
    # 过滤table中的项
    #********************************************************
    def filterTable(self):
        filter_text = self.lineEdit.text().strip()
        for row in range(self.diag_table.rowCount()):
            show_row = False
            for col in range(self.diag_table.columnCount()):
                colData = self.diag_table.item(row,col).text()
                if filter_text in colData or filter_text in colData.lower():
                    show_row = True

            self.diag_table.setRowHidden(row, not show_row)

    #********************************************************
    # table右键菜单
    #********************************************************
    def diagTableContextMenu(self, pos):
        # 创建右键菜单
        context_menu    = QMenu(self)
        action_edit     = QAction("编辑", self)
        action_delete   = QAction("删除", self)
        action_add      = QAction("新增", self)
        action_run      = QAction("运行", self)
        action_config   = QAction("查看配置详情", self)
        action_stimuli  = QAction("查看激励详情", self)
        action_simdir   = QAction("查看运行结果", self)
        action_testbench= QAction("查看testbench", self)

        # 连接菜单项的槽函数
        action_edit.triggered.connect(self.editTableItem)
        action_delete.triggered.connect(self.deleteTableItem)
        action_add.triggered.connect(self.addTableItem)
        action_run.triggered.connect(self.runSimulate)
        action_config.triggered.connect(self.showTableConfig)
        action_stimuli.triggered.connect(self.showSource)
        action_testbench.triggered.connect(self.showTB)
        action_simdir.triggered.connect(self.showSimdir)

        # 将菜单项添加到右键菜单
        #context_menu.addAction(action_edit)
        context_menu.addAction(action_add)
        context_menu.addAction(action_run)
        context_menu.addAction(action_delete)
        context_menu.addAction(action_config)
        context_menu.addAction(action_stimuli)
        context_menu.addAction(action_simdir)
        context_menu.addAction(action_testbench)

        # 显示右键菜单
        context_menu.exec_(self.diag_table.mapToGlobal(pos))

    def showSource(self):
        selected_item = self.getSelectedRow();
        if not selected_item:
            return

        path = self.diag_table.item(selected_item.row(), 3).text().strip()
        source_path = os.path.join(os.getcwd(), 'src/c', path)

        if os.path.exists(source_path):
            self.treeView_filebrowser.setRootIndex(self.dir_model.index(source_path))
        else:
            self.textBrowser.consel("路径不存在: %s" % (source_path), 'red')

    def showSimdir(self):
        selected_item = self.getSelectedRow();
        if not selected_item:
            return

        path = self.diag_table.item(selected_item.row(), 2).text().strip()
        source_path = os.path.join(os.getcwd(), 'simdir', path)
        if os.path.exists(source_path):
            self.treeView_filebrowser.setRootIndex(self.dir_model.index(source_path))
        else:
            self.textBrowser.consel("路径不存在: %s" % (source_path), 'red')

    def refreshFileBrowser(self):
        source_path = os.getenv('CBS_HOME')
        if os.path.exists(source_path):
            self.treeView_filebrowser.setRootIndex(self.dir_model.index(source_path))
        else:
            self.textBrowser.consel("路径不存在: %s" % (source_path), 'red')

    def showTB(self):
        source_path = os.getenv('TB_HOME')
        if os.path.exists(source_path):
            self.treeView_filebrowser.setRootIndex(self.dir_model.index(source_path))
        else:
            self.textBrowser.consel("路径不存在: %s" % (source_path), 'red')

    def showTableConfig(self):
        selected_item = self.getSelectedRow();
        if not selected_item:
            return

        config_name = self.diag_table.item(selected_item.row(), 4).text().strip()
        config_file = os.path.join(os.getcwd(),'config/')+config_name+'.mk'
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                file_contents = file.read()
                file_contents = file_contents.replace('\n', '\\n')
        else:
            self.textBrowser.consel('该测试项对应的配置文件不存在!', 'red')
            return

        # 在这里触发执行Web页面中的JavaScript函数
        js_code = f'''pyqtLoadConfig(\"{file_contents}\");
        var inputElement = document.getElementById("fileSave");
        inputElement.value = \"{config_name}\";
        '''
        self.web_view.page().runJavaScript(js_code)
        self.showSVGTab()

    def getSelectedRow(self):
        selected_items = self.diag_table.selectedItems()
        if not selected_items:
            return

        # 每行有10个items
        if len(selected_items) > 12:
            self.textBrowser.consel("一次只能查询一个测试项的配置！\n", 'red')
        
        return selected_items[0]

    def showSVGTab(self):
        selected_item = self.getSelectedRow();
        if not selected_item:
            return

        self.main_tabWidget.setCurrentIndex(0)
        
    def editTableItem(self):
        # 编辑选定的表格项
        selected_items = self.diag_table.selectedItems()
        if selected_items:
            item = selected_items[0]
            item.setText("编辑后的内容")

    def deleteTableItem(self):
        # 删除选定的行
        selected_rows = set()
        for item in self.diag_table.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            # 从previous_data中删除相应的行
            del self.previous_data[row]
            self.diag_table.removeRow(row)

    def addTableItem(self):
        self.textBrowser.consel("创建新的diag项.", 'green')

        # 新增一行并复制当前选中的行
        selected_rows = set()
        for item in self.diag_table.selectedItems():
            selected_rows.add(item.row())

        new_row = self.diag_table.rowCount()
        self.diag_table.insertRow(new_row)

        copy_valid = True
        if not selected_rows:
            copy_valid = False
            selected_rows.add(0)

        for row in selected_rows:
            for col in range(self.diag_table.columnCount()):
                if col < 2:
                    continue
                if copy_valid:
                    source_item = self.diag_table.item(row, col).text()
                else:
                    source_item = ''

                if col == 2:
                    new_item = QTableWidgetItem(source_item+'_new')
                else:
                    new_item = QTableWidgetItem(source_item)
                # 更改单元格的背景颜色
                new_item.setBackground(QColor("orange"))
                self.diag_table.setItem(new_row, col, new_item)
        
            # 创建一个QCheckBox并将其放入单元格
            checkbox = QTableWidgetItem()
            checkbox.setFlags(checkbox.flags() | Qt.ItemIsUserCheckable)
            checkbox.setCheckState(Qt.Unchecked)
            self.diag_table.setItem(new_row, 1, checkbox)

            # 设置元格Item
            statusItem = QTableWidgetItem()
            pixmap = QPixmap(":/ico/null.png")
            statusItem.setIcon(QIcon(pixmap))
            self.diag_table.setItem(new_row, 0, statusItem)

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

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
            cmd = f"gvim --remote-tab-silent {file_name}"
        elif tool == 'vscode':
            cmd = f"code {file_name}"
        elif tool == 'Simvision':
            cmd = f"simvision -64bit {file_name}"
        elif tool == 'Verdi':
            cmd = f"verdi -ssf {file_name}"

        os.system(cmd)

    def openWithGvim(self):
        self.openFileBrowser("Gvim")
        self.statusbar.showMessage('如有疑问, 请联系 chaozhanghu@phytium.com.cn  @Qsmtool 23.09-0001', 0)
        self.statusbar.show()

    def openWithCode(self):
        self.openFileBrowser("vscode")

    def creat_rightmenu(self):
        self.treeView_menu=QMenu(self)

        self.actionA = QAction(u'Open With Gvim',self)
        self.actionA.triggered.connect(self.openWithGvim)

        self.actionCode = QAction(u'Open With Code',self)
        self.actionCode.triggered.connect(self.openWithCode)

        self.treeView_menu.addAction(self.actionA)
        self.treeView_menu.addAction(self.actionCode)
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
