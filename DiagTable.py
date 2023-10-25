#!/bin/env python3
# _*_ coding: UTF-8 _*_
import os

import extractDiag
from workerThread import MutiWorkThread

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DiagTable():
    def __init__(self, smtui):
        super().__init__()
        self.smtui = smtui
        self.diag_file = smtui.diag_file
        self.diag_table = smtui.diag_table
        self.textBrowser = smtui.textBrowser
        self.web_view = smtui.web_view
        self.progressBar = smtui.progressBar
        self.mutiWorkThreads = smtui.mutiWorkThreads 
        self.treeView_filebrowser = smtui.treeView_filebrowser 
        self.dir_model = smtui.dir_model
        self.lineEdit = smtui.lineEdit

        self.reloadDiagEvent = False
        self.saveDiagEvent = False

        # 设置选择模式为整行选择
        self.diag_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 隐藏行序号
        self.diag_table.verticalHeader().setVisible(False)
        # 关闭自动sorting功能，只在点击header时sorting
        self.diag_table.setSortingEnabled(False)
        # 连接表头点击信号
        self.header = self.diag_table.horizontalHeader()
        self.header.sectionClicked.connect(self.onHeaderClicked)
        # 连接表头列宽调整信号
        #self.header.sectionResized.connect(self.onColumnResized)

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
        # 存储每列的原始大小
        self.original_sizes = [self.header.sectionSize(col) for col in range(self.header.count())]

        self.fillDataForTable()

        # 连接到itemChanged信号
        self.diag_table.itemChanged.connect(self.handleItemChanged)

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

        # 为表格添加右键菜单
        self.diag_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.diag_table.customContextMenuRequested.connect(self.diagTableContextMenu)

    #********************************************************
    # 填充diag table的内容
    #********************************************************
    def reloadDiagFile(self):
        current_progress = self.progressBar.value()
        if current_progress > 0 and current_progress < 100:
            self.textBrowser.consel('上次发布的任务还没有结束, 暂时无法执行刷新操作.', 'red')
            return

        self.mutiWorkThreads = MutiWorkThread(self.smtui)
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet("")  # 清空样式表

        self.textBrowser.consel("刷新diag表信息.","green")

        self.reloadDiagEvent = True
        #self.setSortingEnabled(False)
        self.diag_table.clearContents()
        self.diag_table.setRowCount(0)
        self.fillDataForTable()
        self.diag_table.repaint()
        #self.setSortingEnabled(True)
        self.reloadDiagEvent = False

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
            checkbox.setText(' '*2)
            checkbox.setFlags(checkbox.flags() | Qt.ItemIsUserCheckable)
            checkbox.setFlags(checkbox.flags() & ~Qt.ItemIsEditable)  # 移除 Qt.ItemIsEditable 标志
            checkbox.setCheckState(Qt.Unchecked)
            self.diag_table.setItem(row, 1, checkbox)

            # 设置元格Item
            statusItem = QTableWidgetItem()
            if path_exist:
                pixmap = QPixmap(":/ico/checkmark.png")
                statusItem.setText(' '*5)
            else:
                pixmap = QPixmap(":/ico/null.png")
                statusItem.setText(' '*6)
            statusItem.setIcon(QIcon(pixmap))
            statusItem.setFlags(statusItem.flags() & ~Qt.ItemIsEditable)  # 移除 Qt.ItemIsEditable 标志
            self.diag_table.setItem(row, 0, statusItem)

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()
        # 存储每列的原始大小
        self.original_sizes = [self.header.sectionSize(col) for col in range(self.header.count())]

    #********************************************************
    # 当click在header上时开启sorting，其余时间关闭，似乎没有起作用.
    #********************************************************
    def onColumnResized(self, logicalIndex, old_size, new_size):
        # 设置其他列的大小为原始大小
        for col in range(self.header.count()):
            if col != logicalIndex:
                self.header.resizeSection(col, self.original_sizes[col])

    #********************************************************
    # 当click在header上时开启sorting，其余时间关闭，似乎没有起作用.
    #********************************************************
    def onHeaderClicked(self, logicalIndex):
        # 在表头点击时启用排序功能，否则禁用
        if self.diag_table.isSortingEnabled():
            self.diag_table.setSortingEnabled(False)
        else:
            self.diag_table.setSortingEnabled(True)
            # 执行排序
            self.diag_table.sortItems(logicalIndex)

    #********************************************************
    # 当diag table发生编辑时，触发相关函数 1. 改变背景颜色；
    #********************************************************
    def handleItemChanged(self, item):
        if item.column() == 1:
            if item.checkState() == Qt.Unchecked:
                item.setText(' '*2)
            else:
                item.setText(' ')

        if item and item.column() < 2:
            return

        # 只在文本更改时更改背景颜色
        if not self.reloadDiagEvent and not self.saveDiagEvent:
            item.setBackground(QColor("orange"))

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()
        # 存储每列的原始大小
        self.original_sizes = [self.header.sectionSize(col) for col in range(self.header.count())]

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
        for row in range(self.diag_table.rowCount()):
            if self.diag_table.isRowHidden(row):
                continue
            current_state = self.diag_table.item(row, 1).checkState()
            break

        for row in range(self.diag_table.rowCount()):
            # 判断当前行是否是隐藏的，是则跳过check状态修改
            if self.diag_table.isRowHidden(row):
                continue
            item = self.diag_table.item(row, 1)
            if current_state == Qt.Unchecked:
                item.setCheckState(Qt.Checked)
                item.setText(' ')
            else:
                item.setCheckState(Qt.Unchecked)
                item.setText(' '*2)

    #********************************************************
    # 删除table项确认菜单
    #********************************************************
    def delete_dialog(self):
        # 创建一个确认对话框
        confirm_dialog = QMessageBox()
        confirm_dialog.setIcon(QMessageBox.Question)
        confirm_dialog.setWindowTitle("确认删除testcase")
        confirm_dialog.setText("是否确定删除该testcase? 如正在运行, 进程将被kill.")
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
    def filterTable(self, filter_text):
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
        context_menu    = QMenu(self.smtui)
        action_edit     = QAction("编辑", self.smtui)
        action_delete   = QAction("删除", self.smtui)
        action_add      = QAction("新增", self.smtui)
        action_run      = QAction("立即运行", self.smtui)
        action_stop     = QAction("立即停止", self.smtui)
        action_config   = QAction("查看配置详情", self.smtui)
        action_stimuli  = QAction("查看激励详情", self.smtui)
        action_simdir   = QAction("查看运行结果", self.smtui)
        action_testbench= QAction("查看testbench", self.smtui)

        # 连接菜单项的槽函数
        action_edit.triggered.connect(self.editTableItem)

        icon = QIcon()
        icon.addPixmap(QPixmap(":/ico/new_doc.png"), QIcon.Normal, QIcon.Off)
        action_add.setIcon(icon)
        action_add.triggered.connect(self.addTableItem)

        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/ico/trash.png"), QIcon.Normal, QIcon.Off)
        action_delete.setIcon(icon1)
        action_delete.triggered.connect(self.deleteTableItem)

        action_run.triggered.connect(self.smtui.SingleRunSimulate)
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(":/ico/play-button.png"), QIcon.Normal, QIcon.Off)
        action_run.setIcon(icon3)

        icon4 = QIcon()
        icon4.addPixmap(QPixmap(":/ico/pause.png"), QIcon.Normal, QIcon.Off)
        action_stop.setIcon(icon4)
        action_stop.triggered.connect(self.smtui.singleStopSimulateFunc)
        action_config.triggered.connect(self.showTableConfig)
        action_stimuli.triggered.connect(self.showSource)
        action_testbench.triggered.connect(self.showTB)
        action_simdir.triggered.connect(self.showSimdir)

        # 将菜单项添加到右键菜单
        #context_menu.addAction(action_edit)
        context_menu.addAction(action_add)
        context_menu.addAction(action_run)
        context_menu.addAction(action_stop)
        context_menu.addAction(action_delete)
        context_menu.addAction(action_config)
        context_menu.addAction(action_stimuli)
        context_menu.addAction(action_simdir)
        context_menu.addAction(action_testbench)

        # 显示右键菜单
        context_menu.exec_(self.diag_table.mapToGlobal(pos))

    def expandSubDir(self, subdir):
        # 折叠（收起）所有已展开的项
        self.treeView_filebrowser.collapseAll()

        if os.path.exists(subdir):
            #self.treeView_filebrowser.setRootIndex(self.dir_model.index(source_path))
            ## 获取子目录项（在此示例中为"Sub Directory"）
            sub_directory_index = self.dir_model.index(subdir)

            # 获取从根目录到特定索引的路径
            path_to_index = []
            while sub_directory_index.isValid():
                path_to_index.insert(0, sub_directory_index)
                sub_directory_index = sub_directory_index.parent()

            # 逐级展开路径
            current_index = self.smtui.root_index
            for index in path_to_index:
                current_index = index
                self.treeView_filebrowser.setExpanded(current_index, True)

            # 将最后一级目录设置为选中状态
            self.treeView_filebrowser.setCurrentIndex(current_index)
            self.treeView_filebrowser.scrollTo(current_index)
        else:
            self.textBrowser.consel("路径不存在: %s" % (subdir), 'red')

        self.treeView_filebrowser.setColumnWidth(0, 300)

    ##********************************************************
    ## 过滤table中的项
    ##********************************************************
    def filterTable(self):
        filter_text = self.lineEdit.text().strip()
        self.diag_table.filterTable(filter_text)

    def refreshFileBrowser(self):
        #source_path = os.getenv('CBS_HOME')
        source_path = os.getcwd()

        self.expandSubDir(source_path)


    def showSource(self):
        selected_item = self.getSelectedRow();
        if not selected_item:
            return

        path = self.diag_table.item(selected_item.row(), 3).text().strip()
        source_path = os.path.join(os.getcwd(), 'src/c', path)

        self.expandSubDir(source_path)

    def showSimdir(self):
        selected_item = self.getSelectedRow();
        if not selected_item:
            return

        path = self.diag_table.item(selected_item.row(), 2).text().strip()
        source_path = os.path.join(os.getcwd(), 'simdir', path)

        self.expandSubDir(source_path)

    def refreshFileBrowser(self):
        source_path = os.getenv('CBS_HOME')

        self.expandSubDir(source_path)

    def showTB(self):
        source_path = os.getenv('TB_HOME')

        self.expandSubDir(source_path)

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

        self.smtui.main_tabWidget.setCurrentIndex(0)
        
    def editTableItem(self):
        # 编辑选定的表格项
        selected_items = self.diag_table.selectedItems()
        if selected_items:
            item = selected_items[0]
            item.setText("编辑后的内容")

    def deleteTableItem(self):
        conform = self.delete_dialog()
        if not conform:
            return

        # 关闭正在进行的进程
        self.smtui.singleStopSimulateFunc()

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
            checkbox.setText(' '*2)
            self.diag_table.setItem(new_row, 1, checkbox)

            # 设置元格Item
            statusItem = QTableWidgetItem()
            pixmap = QPixmap(":/ico/null.png")
            statusItem.setText(' '*6)
            statusItem.setIcon(QIcon(pixmap))
            self.diag_table.setItem(new_row, 0, statusItem)

        # 调整列宽以适应内容
        self.diag_table.resizeColumnsToContents()

#    def findTestcaseRow(self, testcase):
#        for row in range(self.diag_table.rowCount()):
#            if testcase == self.diag_table.item(row, 2).text():
#                return row
#
#        return -1
#    
#    def collectSingleRunCMDs(self, forrun):
#        selected_items = []
#        # 新增一行并复制当前选中的行
#        selected_rows = set()
#        for item in self.diag_table.selectedItems():
#            selected_rows.add(item.row())
#        
#        for row in selected_rows:
#            selected_item = self.diag_table.item(row, 2).text()
#            if selected_item in self.task_record_running and self.task_record_running[selected_item] and forrun:
#                self.consol.consel(f"Task {selected_item} 已经在运行, 先stop它或者wait它.\n",'orange')
#                continue
#            else:
#                selected_items.append(selected_item)
#                if forrun:
#                    # 记录开始run的task
#                    self.task_record_running[selected_item] = True
#                    item = self.diag_table.item(row, 1)
#                    current_state = item.checkState()
#                    if current_state == Qt.Unchecked:
#                        item.setCheckState(Qt.Checked)
#                        item.setText(' '*2)
#
#        return selected_items
#
#    def collectCMDs(self):
#        # 遍历表格的行
#        selected_items = []
#        for row in range(self.diag_table.rowCount()):
#            status_item = self.diag_table.item(row, 0)
#            check_item = self.diag_table.item(row, 1)
#            if check_item.checkState() == Qt.Checked:
#                selected_item = self.diag_table.item(row, 2).text()
#                if selected_item in self.task_record_running and self.task_record_running[selected_item]:
#                    self.consol.consel(f"Task {selected_item} 已经在运行, 先stop它或者wait它.\n",'orange')
#                    continue
#                else:
#                    selected_items.append(selected_item)
#                    # 记录开始run的task
#                    self.task_record_running[selected_item] = True
#                    # 创建QPixmap对象并设置图像
#                    pixmap = QPixmap(":/ico/parcel.png")
#                    status_item.setText(' '*6)
#                    status_item.setIcon(QIcon(pixmap))
#                    check_item.setFlags(check_item.flags() & ~Qt.ItemIsUserCheckable)  # 移除 Qt.ItemIsUserCheckable 标志
#
#        return selected_items