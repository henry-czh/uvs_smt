#!/bin/env python2
# _*_ coding: UTF-8 _*_

testSel = """
<option value="Defaullt" selected>Defaullt</option>
<option value="XXX">XXX</option>
<option value="YYY">YYY</option>
"""
testUl = """
<ul id="first-ul">
    <li>
        <span class="caret">CONFIG_1</span>
        <select id="CONFIG_1">
            <option value="1">123 - children</option>
            <option value="2" selected>456 - children</option>
            <option value="0">789</option>
        </select>
        <ul>
            <li>
                <span>CONFIG_1.1</span>
                <select>
                    <option value="0">123</option>
                    <option value="0">456</option>
                    <option value="0">789</option>
                </select>
            </li>
            <li>
                <span>CONFIG_1.2</span>
                <select>
                    <option value="0">123</option>
                    <option value="0">456</option>
                    <option value="0">789</option>
                </select>
            </li>
        </ul>
        <ul>
            <li>
                <span>CONFIG_1.1-2</span>
                <select>
                    <option value="0">123-2</option>
                    <option value="0">456-2</option>
                    <option value="0">789-2</option>
                </select>
            </li>
            <li>
                <span>CONFIG_1.2-2</span>
                <select>
                    <option value="0">123-2</option>
                    <option value="0">456-2</option>
                    <option value="0">789-2</option>
                </select>
            </li>
        </ul>
    </li>
    <li>
        <span class="caret">CONFIG_2</span>
        <select>
            <option value="1">123 - children</option>
            <option value="0">456</option>
            <option value="0">789</option>
        </select>
        <ul>
            <li>
                <span>CONFIG_2.1</span>
                <select>
                    <option value="0">123</option>
                    <option value="0">456</option>
                    <option value="0">789</option>
                </select>
            </li>
            <li>
                <span class="caret">CONFIG_2.2</span>
                <select>
                    <option value="1">123 - children</option>
                    <option value="0">456</option>
                    <option value="0">789</option>
                </select>
                <ul>
                    <li>
                        <span>CONFIG_2.2.1</span>
                        <select>
                            <option value="0">123</option>
                            <option value="0">456</option>
                            <option value="0">789</option>
                        </select>
                    </li>
                    <li>
                        <span>CONFIG_2.2.1</span>
                        <select>
                            <option value="0">123</option>
                            <option value="0" selected>456</option>
                            <option value="0">789</option>
                        </select>
                    </li>
                </ul>
            </li>
        </ul>
    </li>
</ul>
"""

testConfigs = """
CONFIG_1 = 456 - children
CONFIG_1.1-2 = 123-2
CONFIG_1.2-2 = 123-2
CONFIG_2 = 123 - children
CONFIG_2.1 = 123
CONFIG_2.2 = 123 - children
CONFIG_2.2.1 = 123
CONFIG_2.2.1 = 456
"""

testLog = """
{
    "success": true,
    "change_caonfig": {"CONFIG0":"Y"},
    "depend_change": {"CONFIG1":"Y","CONFIG2":"N"},
    "depend_change_multiple": {"CONFIG3":["Y","N"],"CONFIG4":["Y","N"]},
    "message": "XXX<i>YYY</i>ZZZ"
}
"""

import readConfiguration
import parseConfig
import copy
import os
import re
import json
from lxml import etree
import sys
from log import log
from imp import reload

reload(sys)
#sys.setdefaultencoding('utf-8')

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        """
        判断是否为bytes类型的数据是的话转换成str
        :param obj:
        :return:
        """
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

def CollectSkts(cfg_dict):
    temp_skt= set()
    sockets = ''
    for item in cfg_dict:
        if "unit_" in item:
            # sys.stderr.write("find item[%s]\n" % item)
            skt = re.findall(r'unit_(SKT.+?)_', item)
            if skt:
                skt_name = skt[0]
            else:
                skt_name = ''
            if skt_name!='':
                temp_skt.add(skt_name)
    if not temp_skt:
        # 嵌入式没有 skt 仅仅返回一个 TOP
        temp_skt = ['TOP']
    temp_skt = sorted(list(temp_skt))
    for skt in temp_skt:
        sockets = sockets + '<option value=\"'+skt+'\">'+skt+'</option>\n'
    return temp_skt,sockets

def GenUlHtml(tdict, topUl, ulHtml, cfg_dict, load_dict, mode_en):
    ulHtml["treeUl"]  = readConfiguration.genTreeUl(tdict,topUl,True,1, load_dict, mode_en)
    ulHtml["treeUl"]  = etree.tostring(ulHtml["treeUl"],pretty_print=True,encoding="utf-8")
    # ulHtml["treeUl"]  = ulHtml["treeUl"].decode('utf-8')
    ulHtml["zebu"]    = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "zebu_")
    ulHtml["pld"]     = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "pld_")
    ulHtml["protium"] = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "protium_")
    ulHtml["simu"]    = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "simu_")
    ulHtml["emu"]     = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "emu_")
    ulHtml["image"]   = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "image_")
    ulHtml["peripheral"] = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "peri_")
    ulHtml["checker"] = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "checker_")
    ulHtml["monitor"] = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "monitor_")
    ulHtml["macroUl"] = readConfiguration.genMacroUl(cfg_dict, load_dict, True, "macro_")

# return a json {
#     "modes":   "...",
#     "sockets": "...",
#     "skts":    ['skt0', 'skt1', ...],
#     "treeUl":  "...",
#     "macroUl": "...",
#     "BaremetalConfig": "...",
#     "mess":    "..."
# }
def GetHtml(mode):
    ulHtml = {}
    topUl    = etree.XML('<ul/>')
    testSel  = ''
    sockets  = ''
    modeInfo = ''

    base_cfg_file = os.getenv("BASE_CONFIG_FILE")
    emu_cfg_file  = os.getenv("EMU_CONFIG_FILE")
    usr_cfg_file  = os.getenv("USER_CONFIG_FILE")
    default_mode = os.getenv("DEFAULT_MODE")
    if os.environ.get("DEFAULT_MODE"):
        default_mode = os.getenv("DEFAULT_MODE")
        os.environ.pop("DEFAULT_MODE")
        os.environ["LOAD_DEFAULT_MODE"]=default_mode
    else:
        default_mode = mode

    config_dict = parseConfig.parseConfig(base_cfg_file,usr_cfg_file)
    cfg_dict    = config_dict['cfg']
    mode_dict   = config_dict['mode']
    soft_dict   = config_dict['soft']

    init_cfg_dict = readConfiguration.genOutPutCfg(cfg_dict)

    for key in mode_dict:
        if key==default_mode:
            testSel=testSel + '<option value=\"'+key+'\" selected>'+key+'</option>\n'
            # modify config according to mode selected
            for item in mode_dict[key]:
                init_cfg_dict[item] = mode_dict[key][item]
        else:
            testSel=testSel + '<option value=\"'+key+'\">'+key+'</option>\n'
    ulHtml["modes"] = testSel
    ulHtml["default_mode"] = default_mode

    ##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ## Generate BootLocation and BoardInit config
    ##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for item in soft_dict:
        if item != 'project':
            soft_dict[item] = cfg_dict[item]['default']
    BaremetalConfig = readConfiguration.genSoftUl(cfg_dict.copy(),soft_dict)
    BaremetalConfig  = etree.tostring(BaremetalConfig,pretty_print=True,encoding="utf-8")
    ulHtml["BaremetalConfig"] = BaremetalConfig.decode('utf-8')

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Generate Mode Information
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if len(mode_dict[default_mode])>0:
        modeInfo = '\t 当前选择的模式 : %s \n' % (default_mode)
        for item in mode_dict[default_mode]:
            modeInfo = modeInfo + '\t 该模式下对应锁定的配置项 : %s -> %s \n' % (item,mode_dict[default_mode][item])

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Generate SKT Info
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ulHtml["skts"],ulHtml["sockets"]=CollectSkts(cfg_dict)
    #sys.stderr.write("find all skts%s\n" % ulHtml["skts"])

    # check dependency for the initial sets
    checkStatus,check_info = readConfiguration.checkDefaultSet(cfg_dict.copy(),init_cfg_dict)

    if checkStatus == 0 or checkStatus == 1 :
        tdict   = readConfiguration.genDesignTree(cfg_dict)
        GenUlHtml(tdict, topUl, ulHtml, cfg_dict, mode_dict[default_mode], True)
        ulHtml["mess"] = '<i success>[Sucess]</i> 初始化成功，但存在依赖不满足情况，引发静默修改！' + check_info + modeInfo + '<i success>\t Initial done!</i>\n'
        if checkStatus == 0:
            ulHtml["mess"] = '<i success>[Success] Initial done!</i>\n' + modeInfo + '<i success>\t 初始化成功!</i>\n'
    elif checkStatus==2:
        ulHtml["mess"] = "<i>[Error] </i>"+check_info
    return json.dumps(ulHtml, ensure_ascii=False, cls=MyEncoder, indent=4)

def PostModifySvg(links,cfg_dict,mode_dict,mode,load_dict,selected_skt):
    for link in links:
        link_name = link.attrib.get('xlink:href')
        skt = re.findall(r'unit_(SKT.+?)_', link_name)
        if skt:
            replaced_skt_name = skt[0]
            config_item_name = link_name.replace(replaced_skt_name,selected_skt)
        else:
            config_item_name = link_name
        if config_item_name in cfg_dict:
            if load_dict!=None:
                link.set('data-value',load_dict[config_item_name])
            elif config_item_name in mode_dict[mode]:
                link.set('data-value',mode_dict[mode][config_item_name])
            else:
                link.set('data-value',cfg_dict[config_item_name]['default'])
            link.set('data-values',json.dumps(cfg_dict[config_item_name]['options']))
            link.set('xlink:href','javascript:;')
            if 'instance' in cfg_dict[config_item_name]:
                titles = link.xpath('./g/title')
                display_info = ''
                if 'coreid' in cfg_dict[config_item_name]:
                    display_info = 'CoreID : ' + str(cfg_dict[config_item_name]['coreid']) + '\n'
                display_info = display_info + 'HDL_Path : ' + str(cfg_dict[config_item_name]['instance']) + '\n'
                display_info = display_info + 'Help : ' + str(cfg_dict[config_item_name]['help']) + '\n'
                titles[0].text = display_info
        skt = re.findall(r'unit_(SKT.+?)_', link_name)
        if skt:
            replaced_skt_name = skt[0]
            link_name = link_name.replace(replaced_skt_name,':')
        link.set('data-config',link_name)

def GetSvg(mode, skt):
    base_cfg_file = os.getenv("BASE_CONFIG_FILE")
    emu_cfg_file  = os.getenv("EMU_CONFIG_FILE")
    usr_cfg_file  = os.getenv("USER_CONFIG_FILE")
    svg_cfg_file  = os.getenv("SVG_FILE")

    config_dict = parseConfig.parseConfig(base_cfg_file,usr_cfg_file)
    cfg_dict    = config_dict['cfg']
    mode_dict   = config_dict['mode']
    soft_dict   = config_dict['soft']

    parser = etree.HTMLParser(encoding='utf-8')
    svg = etree.parse(svg_cfg_file,parser=parser)

    tdict    = readConfiguration.genDesignTree(cfg_dict)
    p2c_dict = readConfiguration.getParentChildRelative(tdict,{},'')
    
    init_cfg_dict = readConfiguration.genOutPutCfg(cfg_dict)               
    
    # 迭代所有配置项，确保所有父节点的子项都满足要求
    # 父节点为D、G时，子节点的值在fileContent中，不用关心；
    # 父节点非D、G时，子节点需要统一刷成N
    load_dict = traverseP2C(p2c_dict,init_cfg_dict,p2c_dict.keys(),False)
    
    for item in load_dict:
        cfg_dict[item]['default'] = load_dict[item]
    
    links = svg.xpath("//a")

    PostModifySvg(links,cfg_dict,mode_dict,mode,None,skt)

    return etree.tostring(svg,encoding='utf-8',pretty_print=True,method='html')

# configs: 当前所有配置, {"CONFIG1":"Y","CONFIG2":"N"}
def Apply(configs):
    return testConfigs

# configs: 当前所有配置, {"CONFIG1":"Y","CONFIG2":"N"}
# config: 被改动的一个配置, {"CONFIG1":"Y"}
def GetLog(configs, config):

    base_cfg_file = os.getenv("BASE_CONFIG_FILE")
    emu_cfg_file  = os.getenv("EMU_CONFIG_FILE")
    usr_cfg_file  = os.getenv("USER_CONFIG_FILE")

    log_dict={}

    dependStatus,depend_dict,conflict_info = readConfiguration.genGetLog(base_cfg_file,usr_cfg_file,emu_cfg_file,configs,config)
    depend_dict.update(config)

    # 处理隐式的父子依赖
    # depend_dict_tree,depend_dict_multi = readConfiguration.unitDepend(base_cfg_file,usr_cfg_file,emu_cfg_file,depend_dict,configs,config)
    # depend_dict.update(depend_dict_tree)
    #log(config)
    readConfiguration.SetToDefault(depend_dict, configs, config)

    log_dict["success"]=dependStatus
    log_dict["message"]=conflict_info
    if dependStatus:
        log_dict["depend_change"]          = depend_dict
        # log_dict["depend_change_multiple"] = depend_dict_multi
        log_dict["depend_change_multiple"] = {}
    else:
        log_dict["depend_change"]          = {}
        log_dict["depend_change_multiple"] = {}

    return json.dumps(log_dict)


# configs: 当前所有配置, {"CONFIG1":"Y","CONFIG2":"N"}
# fileName: save file name
def Save(fileName, configs, overwrite):
    saveDir = os.getenv("CONFIG_SAVE_DIR")
    save_status_dict={}
    save_status = True

    # 判断文件是否已经存在
    if os.path.exists(str(saveDir)+'/%s.mk' % (fileName)):
        if overwrite:
            save_status_dict['message']='[警告] 该文件已覆盖保存!'
        else:
            save_status_dict['message']='[Error] 该文件已存在，确认覆盖保存吗？\请选择\"Overwrite\"开关覆盖保存，或给定新的保存文件名!'
            save_status = False

    save_status_dict['success']=save_status

    if save_status:
        outFile=open(str(saveDir)+'/%s.mk' % (fileName),'w')
        textOut = '#// Generated automatic by CMT,don\'t change!'
        key_list = sorted(configs.keys(),reverse=False)
        for key in key_list:
            context = configs[key].strip('\n').replace('\n',',')

            textOut += '\n' + key + ' = ' + context + '\n'
        outFile.write(textOut)
        outFile.close()
        save_status_dict['message']='[Success] 文件已保存!\n位置: '+saveDir+'/%s.mk' % (fileName)

    return json.dumps(save_status_dict)

# fileContent: file content string
def LoadHtml(fileContent):
    ulHtml          = {}
    topUl           = etree.XML('<ul/>')
    testSel         = ''
    load_soft_dict  = {}
    load_dict       = readConfiguration.loadExistCfg(fileContent.split('\n'))

    base_cfg_file = os.getenv("BASE_CONFIG_FILE")
    emu_cfg_file  = os.getenv("EMU_CONFIG_FILE")
    usr_cfg_file  = os.getenv("USER_CONFIG_FILE")
    default_mode  = os.environ.get("LOAD_DEFAULT_MODE")

    config_dict = parseConfig.parseConfig(base_cfg_file,usr_cfg_file)
    cfg_dict    = config_dict['cfg']
    mode_dict   = config_dict['mode']
    soft_dict   = config_dict['soft']

    tdict   = readConfiguration.genDesignTree(cfg_dict)

    check_status,load_dict,check_info = readConfiguration.compareDismatchCfg(cfg_dict,load_dict,tdict)

    for key in mode_dict:
        if key==default_mode:
            testSel=testSel + '<option value=\"'+key+'\" selected>'+key+'</option>\n'
        else:
            testSel=testSel + '<option value=\"'+key+'\">'+key+'</option>\n'
    ulHtml["modes"] = testSel

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Generate SKT Info
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ulHtml["skts"],ulHtml["sockets"]=CollectSkts(cfg_dict)

    GenUlHtml(tdict, topUl, ulHtml, cfg_dict, load_dict, False)

    if 'project' in soft_dict:
        load_soft_dict['project'] = soft_dict['project']
    else:
        load_soft_dict['project'] = ''
    for item in soft_dict:
        if item in load_dict:
            load_soft_dict[item] = load_dict[item]
        else:
            load_soft_dict[item] = ''
    ulHtml["BaremetalConfig"] = readConfiguration.genSoftUl(cfg_dict,load_soft_dict)
    ulHtml["BaremetalConfig"] = etree.tostring(ulHtml["BaremetalConfig"],pretty_print=True,encoding="utf-8")
    ulHtml["BaremetalConfig"] = ulHtml["BaremetalConfig"].decode('utf-8')

    if check_status:
        ulHtml["mess"] = "<i success>[Success] Load done!</i>"
    else:
        ulHtml["mess"] = "<i success>[Success]</i> 加载成功，但是存在以下静默修改：\n"+check_info

    return json.dumps(ulHtml, ensure_ascii=False, cls=MyEncoder, indent=4)

# 在初始化阶段或Load阶段，完成父子节点间的天然依赖
def traverseP2C(p2c_dict,load_dict,key_list,forceN):
    for item in key_list:
        #if p2c_dict.has_key(item):
        if item in p2c_dict:
            if forceN:
                for key in p2c_dict[item]:
                        load_dict[key] = 'N'
                        #if p2c_dict.has_key(key):
                        if key in p2c_dict:
                            load_dict = traverseP2C(p2c_dict,load_dict,p2c_dict[key],True)
            else:
                for key in p2c_dict[item]:
                    if item in load_dict:
                        if load_dict[item] not in ['D','G']:
                            load_dict[key] = 'N'
                            #if p2c_dict.has_key(key):
                            if key in p2c_dict:
                                load_dict = traverseP2C(p2c_dict,load_dict,p2c_dict[key],True)
                        else:
                            #if p2c_dict.has_key(key):
                            if key in p2c_dict:
                                load_dict = traverseP2C(p2c_dict,load_dict,p2c_dict[key],False)
                    else:
                        load_dict[key] = 'N'

    return load_dict

# fileContent: file content string
def LoadSvg(fileContent, skt):
    load_dict = readConfiguration.loadExistCfg(fileContent.split('\n'))

    base_cfg_file = os.getenv("BASE_CONFIG_FILE")
    emu_cfg_file  = os.getenv("EMU_CONFIG_FILE")
    usr_cfg_file  = os.getenv("USER_CONFIG_FILE")
    svg_cfg_file  = os.getenv("SVG_FILE")

    parser = etree.HTMLParser(encoding='utf-8')
    svg = etree.parse(svg_cfg_file,parser=parser)

    config_dict = parseConfig.parseConfig(base_cfg_file,usr_cfg_file)
    cfg_dict    = config_dict['cfg']
    mode_dict   = config_dict['mode']
    soft_dict   = config_dict['soft']

    tdict    = readConfiguration.genDesignTree(cfg_dict)
    p2c_dict = readConfiguration.getParentChildRelative(tdict,{},'')

    # fileContent是隐藏不必要子项后的最终配置，load操作后要将所有的差异找到
    # 1. 缺少的补上 
    # 2. 同一配置项的值保留
    # 3. 多余的配置项删除
    # 4. 有依赖关系的重新计算解决
    check_status,load_dict,check_info = readConfiguration.compareDismatchCfg(cfg_dict,load_dict,tdict)


    # 迭代所有配置项，确保所有父节点的子项都满足要求
    # 父节点为D、G时，子节点的值在fileContent中，不用关心；
    # 父节点非D、G时，子节点需要统一刷成N
    load_dict = traverseP2C(p2c_dict,load_dict,p2c_dict.keys(),False)
    
    links = svg.xpath("//a")

    PostModifySvg(links,cfg_dict,None,None,load_dict,skt)

    return etree.tostring(svg,encoding='utf-8',pretty_print=True,method='html')


