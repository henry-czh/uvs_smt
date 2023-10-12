#!/usr/bin/env python2
# _*_ coding: UTF-8 _*_

import os
import json
import sys
from imp import reload
reload(sys)
#sys.setdefaultencoding('utf-8')
import re
from os import system
from lxml import etree
import parseConfig
import collections
from log import log

def create_dict(tdict,inst_list,module_list,hdl_path,help_info,item_name,default):
    if len(inst_list)==1:
        if inst_list[0] not in tdict:
            # 如果该节点不在tree上，则该节点应该是叶节点
            tdict[inst_list[0]] = dict()
            # 如果该节点已经在tree上且为支干，则应该保留其子节点
            tdict[inst_list[0]]['sub_tree']=[]

        tdict[inst_list[0]]['modules']=module_list
        tdict[inst_list[0]]['hdl_path']=hdl_path
        tdict[inst_list[0]]['help']=help_info
        tdict[inst_list[0]]['item_name']=item_name
        default_opt = ''
        for item in module_list:
            #if item.split(':')[0] == default:
            if item == default:
                default_opt = item
        if default_opt=='':
            raise Exception('[%s] default opt [%s] not in options list!!!' % (module_list,default))
        else:
            tdict[inst_list[0]]['default']=default_opt
    else:
        if not inst_list[0] in tdict:
            tdict[inst_list[0]] = dict()
            tdict[inst_list[0]]['sub_tree'] = dict()
        else:
            if not type(tdict[inst_list[0]]['sub_tree']) is dict:
                tdict[inst_list[0]]['sub_tree']=dict()
        create_dict(tdict[inst_list[0]]['sub_tree'],inst_list[1:],module_list,hdl_path,help_info,item_name,default)
    return tdict

def genDesignTree(cfg_dict):
    tree_dict = dict()

    for item in cfg_dict.keys():
        if 'instance' in cfg_dict[item]:
            instance_list = cfg_dict[item]['instance'][0].strip().split('.')
            if len(instance_list)==0:
                raise Exception('%s has \"instance\",but its value is null!! check the config file' % (item))
            #module_list = list(cfg_dict[item]['module'].values())
            module_list = list(cfg_dict[item]['module'])
            hdl_path = cfg_dict[item]['instance'][0]
            help_info = cfg_dict[item]['help']
            default = cfg_dict[item]['default']
            tree_dict=create_dict(tree_dict,instance_list,module_list,hdl_path,help_info,item,default)
        else:
            continue
            print ('[%s] is a macro item' % (item))
    return tree_dict

def genSoftUl(cfg_dict,soft_dict):
    allUl = etree.XML('<fieldset/>')
    allUl.set('id','BaremetalConfig')
    allUl.set('class','long-select config_tr')

    titleUl = etree.XML('<legend/>')
    if 'project' in soft_dict:
        titleUl.text = soft_dict['project']+' Software Config'
        del soft_dict['project']

    topUl = etree.XML('<ul/>')
    topUl.set('class','show')

    allUl.append(titleUl)
    allUl.append(topUl)

    for item in sorted(soft_dict.keys()):
        li = etree.XML('<li/>')
        topUl.append(li)
        span = etree.XML('<span/>')
        span.text = item

        if 'type' in cfg_dict[item] :
            if cfg_dict[item]['type']=='LineEdit':
                lineEdit= etree.XML('<input/>')
                lineEdit.set('id',item)
                lineEdit.set('class','set')
                lineEdit.set('value',soft_dict[item].replace(" ",'\n'))
                li.append(span)
                li.append(lineEdit)
            elif cfg_dict[item]['type']=='TextEdit':
                compUl = etree.XML('<fieldset/>')
                compLegend = etree.XML('<legend/>')
                compLegend.text = item.strip('soft_')
                compUl.append(compLegend)

                textArea = etree.XML('<textarea/>')
                textArea.set('class','set')
                options = '\n'.join(soft_dict[item].split(" "))
                textArea.text = options
                textArea.set('id',item)
                compUl.append(textArea)
                allUl.append(compUl)
            continue

        li.append(span)
        select = etree.XML('<select/>')
        select.set('id',item)
        select.set('class','set')
        li.append(select)
        for opt in cfg_dict[item]['options']:
            option = etree.XML('<option/>')
            option.set('value',opt)
            option.text = opt
            select.append(option)
            if opt == soft_dict[item]:
                option.set('selected','selected')
    return allUl

GroupIdex = [
    'Boot',
    'Ddr',
    'Auto test',
    'Benchmark',
    'Frequent change',
    'other',
]

def genMacroUl(cfg_dict,mode_dict,mode_en,cfg_type):
    global GroupIdex
    isr0 = len(GroupIdex) - 1
    item_group = {}
    for item in cfg_dict:
        if not item.startswith(cfg_type):
            continue
        group = re.findall(r'[a-z]+?_([a-z]+?)_', item)
        if group:
            group = group[0]
            isr = -1
        else:
            group = 'other'
        if 'group' in cfg_dict[item]:
            group = cfg_dict[item]['group']
            isr = isr0
        if group not in GroupIdex:
            GroupIdex.insert(isr, group)
            #log(isr)
            #log(GroupIdex)
        # log('item[%s] g[%s]' % (item, group))
        if group not in item_group:
            item_group[group] = []

        li = etree.XML('<li/>')
        item_group[group].append(li)
        span = etree.XML('<span/>')
        span.text = item
        li.append(span)

        if 'type' in cfg_dict[item]:
            lineEdit= etree.XML('<input/>')
            lineEdit.set('id',item)
            lineEdit.set('class','set')
            if mode_en and item in mode_dict:
                lineEdit.set('value',mode_dict[item])
            else:
                lineEdit.set('value',cfg_dict[item]['default'])
            li.append(lineEdit)
            continue

        select = etree.XML('<select/>')
        select.set('id', item)
        select.set('class', 'set')
        li.append(select)
        for opt in cfg_dict[item]['options']:
            option = etree.XML('<option/>')
            select.append(option)
            if item in mode_dict and opt == mode_dict[item]:
                option.text = mode_dict[item]
                option.set('value',mode_dict[item])
                option.set('selected', 'selected')
            else:
                option.text = opt
                option.set('value',opt)
                if cfg_dict[item]['default']==opt and not item in mode_dict:
                    option.set('selected', 'selected')

    allUl = etree.XML('<ul/>')
    allUl.set('id','first-ul')
    for gk in GroupIdex:
        if gk not in item_group:
            continue
        subUl = etree.XML('<fieldset/>')
        subUl.set('class', 'config_tr')
        subLegend = etree.XML('<legend/>')
        subLegend.text = '%s Options' % gk
        subUl.append(subLegend)
        allUl.append(subUl)
        for li in item_group[gk]:
            subUl.append(li)

    return etree.tostring(allUl,pretty_print=True,encoding="utf-8")

def genTreeUl(tdict,topUl,isTop,set_enable,constraint_dict,mode_en):

    if isTop:
        topUl.set('id','first-ul')

    for item in sorted(tdict.keys()):
        upper_set_enable = set_enable
        li = etree.XML('<li/>')
        span = etree.XML('<span/>')
        span.text = item
        li.append(span)
        #-----------------------------------------------------------------------------------
        # set select
        #-----------------------------------------------------------------------------------
        if 'modules' in tdict[item]:
            select = etree.XML('<select/>')
            li.append(select)
            select.set('id',tdict[item]['item_name'])

            if set_enable:
                select.set('class','set')

            for op in tdict[item]['modules']:
                option = etree.XML('<option/>')
                select.append(option)
                option.text = op

                if tdict[item]['item_name'] in constraint_dict:
                    if op.split(':')[0]==constraint_dict[tdict[item]['item_name']]:
                        option.set('selected','selected')
                elif tdict[item]['default']==op:
                    option.set('selected','selected')
                if mode_en and tdict[item]['item_name'] in constraint_dict:
                    if op.split(':')[0]==constraint_dict[tdict[item]['item_name']]:
                        option.set('value',op.split(':')[0])
                else:
                    option.set('value',op.split(':')[0])
        #--------------------------------------------------------------------------------------
        # node set
        #--------------------------------------------------------------------------------------
        topUl.append(li)
        if (type(tdict[item]['sub_tree']).__name__=='dict'):
            if 'default' in tdict[item]:
                if tdict[item]['item_name'] in constraint_dict:
                    if constraint_dict[tdict[item]['item_name']] in ['D','G']:
                        span.set('class','caret')
                        if set_enable:
                            upper_set_enable = 1
                    else:
                        upper_set_enable = 0
                elif tdict[item]['default'].split(':')[0] in ['D','G']:
                    span.set('class','caret')
                    if set_enable:
                        upper_set_enable = 1
                else:
                    upper_set_enable = 0
            else:
                span.set('class','caret')

            htmlUl = etree.XML('<ul/>')
            childUl = genTreeUl(tdict[item]['sub_tree'],htmlUl,False,upper_set_enable,constraint_dict,mode_en)
            li.append(childUl)

    return topUl

#create temp config database
def genOutPutCfg(cfg_dict):
    cfg_temp_dict = dict()
    for item in cfg_dict:
        if 'default' in cfg_dict[item]:
            cfg_temp_dict[item] = cfg_dict[item]['default']
        else:
            cfg_temp_dict[item] = '*'
    return cfg_temp_dict

def loadExistCfg(cfg_file):
    load_cfg_dict=dict()
    valid_entry_pattern = re.compile('^[a-zA-Z0-9]')
    for item in cfg_file:
        if re.match(valid_entry_pattern,item):
            try:
                item = item.strip().strip(' ').split(' = ')
                load_cfg_dict[item[0].strip()] = item[1].replace('\n',',')
            except:
                raise Exception('*ERROR %s format is error!' % (item))
    return load_cfg_dict

def checkDependence(init_key_list,item_name,item_value,cfg_dict,current_cfgs,status,has_depend,depend_info,depend_dict):
    if item_name not in cfg_dict:
        status = 1
        depend_info = '<i>Fatal,该配置项与当前配置文件不匹配，请删除该配置，重新生成！</i>'
        return status,has_depend,depend_info,depend_dict,current_cfgs

    if 'depends on' not in cfg_dict[item_name] or item_value not in cfg_dict[item_name]['depends on']:
        return status,has_depend,depend_info,depend_dict,current_cfgs

    #sys.stderr.write("cfg_dict \n %s \n" % (json.dumps(cfg_dict,indent=2)))
    depend_list = cfg_dict[item_name]['depends on'][item_value]
    for item in depend_list:
        #判断是否有因依赖关系发生的默认修改
        for k in item:
            if k in current_cfgs:
                # 2022-06-06 By chaozhanghu
                # 当前配置值在被依赖列表中既合法，举个例子:
                # {A:item1=A,B,C}, 则当前配置项等于A时，item1等于A、B、C中任何值均合法，不做任何改动；
                if not current_cfgs[k] in item[k]:
                    status = 1
                    has_depend = 1
                    depend_info = depend_info + item_name + ' = ' + item_value + ' 要求 ' + k + ' = ' + str(item[k]) + '\n\t '

                    # 被依赖项的取值是一个列表，则以第一个项为静默修改值；
                    depend_info += '依赖项是列表，选取第一项为静默修改值，' + '更新为' + k + ' = ' + str(item[k][0]) + '\n\t '
                    item[k] = item[k][:1]
                else:
                    # log(current_cfgs[k])
                    item[k] = [current_cfgs[k]]
            else:
                # 静默修改项不在当前配置项中，则需要从依赖关系中设定默认值
                status = 1
                has_depend = 1
                depend_info = depend_info + item_name + ' = ' + item_value + ' 要求 ' + k + ' = ' + str(item[k]) + '\n\t '

                # 被依赖项的取值是一个列表，则以第一个项为静默修改值；
                depend_info += k + '是新增配置项，选择依赖列表中的第一项为静默修改值，' + '更新为' + k + ' = ' + str(item[k][0]) + '\n\t '
                item[k] = item[k][:1]

            depend_dict.update(item)
            # log("item item %s %s" % (k, item))
            if k not in current_cfgs or not current_cfgs[k] in item[k]:
                current_cfgs[k] = item[k][0]  # 这里是在干嘛?

            if k in init_key_list:
                info=depend_info
            else:
                init_key_list.append(k)
                s,d,info,dpd_dict,tmp_dict = checkDependence(init_key_list,k,current_cfgs[k],cfg_dict,current_cfgs,status,has_depend,depend_info,depend_dict)
            depend_info = info

    return status,has_depend,depend_info,depend_dict,current_cfgs

def checkConflict(changed_item,changed_value,cfg_dict,cfg_temp_dict,depend_dict,conflict,conflict_info):
    #检查当前项的conflict情况
    # log('%s' % depend_dict)
    temp_depend_dict = depend_dict.copy()
    temp_depend_dict[changed_item]=changed_value

    for item in cfg_dict:
        #检查静默修改部分的conflict情况
        for key,value in temp_depend_dict.items():
            if key not in cfg_dict:
                conflict = 1
                conflict_info += '\t 配置项 %s 在你的配置文件 all.cfg或usr.cfg 中不存在.\n' % (key)
                break
            if 'depends on' in cfg_dict[item] and item in cfg_temp_dict:
            	#option_has_depend: 有依赖关系的本item的option
                option_has_depend = cfg_temp_dict[item]
                if option_has_depend in cfg_dict[item]['depends on']:
                    depend_list = cfg_dict[item]['depends on'][option_has_depend]
                    #be_depend_dict: 具体的依赖关系
                    for be_depend_dict in depend_list:
                        #判断配置冲突的主要条件：
                        #1. 配置项确实被依赖；
                        #2. 当前要改变的值与依赖关系中要求的值不一致；
                        # unicode 和str都存在，导致使用type判断类型失败
                        if not isinstance(value, list):
                            value = [value]
                        if key in be_depend_dict and not set(value).intersection(set(be_depend_dict[key])):
                            #排除对自身的检查，防止进入死循环
                            #log('checkConflict %s ?= %s' % (item, changed_item))
                            if item != changed_item:
                              conflict = 1
                              conflict_info = conflict_info + '\n\t %s = %s 依赖于 %s = %s,\n\t 但你正在改变 %s 的值为 %s.\n ' % (item,option_has_depend,key,be_depend_dict[key],key,value)
        else:
            continue
        break
    return conflict,conflict_info

def treeDepend(tdict,parent_item,tree_depend_dict):
    for item in tdict:
        temp_parent_item = parent_item
        if 'item_name' in tdict[item]:
            if temp_parent_item != '':
                tree_depend_dict[tdict[item]['item_name']] = temp_parent_item
            temp_parent_item = tdict[item]['item_name']
        if 'sub_tree' in tdict[item]:
            if type(tdict[item]['sub_tree']).__name__=='dict':
                treeDepend(tdict[item]['sub_tree'],temp_parent_item,tree_depend_dict)
    return tree_depend_dict

def mergeTreeDepend(current_cfgs,item,tree_depend_dict,new_depend_dict,multi_depend_dict,cfg_dict):
    if item in tree_depend_dict:
        if 'G' in cfg_dict[tree_depend_dict[item]]['options']:
            if current_cfgs[tree_depend_dict[item]] not in ['D','G']:
                multi_depend_dict[tree_depend_dict[item]] = ['D','G']
        else:
            if current_cfgs[tree_depend_dict[item]] not in ['D']:
                new_depend_dict[tree_depend_dict[item]] = 'D'
        sub_item = tree_depend_dict[item]
        del tree_depend_dict[item]
        mergeTreeDepend(current_cfgs,sub_item,tree_depend_dict,new_depend_dict,multi_depend_dict,cfg_dict)
    return new_depend_dict,multi_depend_dict

def getParentChildRelative(tdict,p2c_dict,parent_name):

    for item in tdict:
        if 'item_name' in tdict[item]:
            if parent_name in p2c_dict:
                p2c_dict[parent_name].append(tdict[item]['item_name'])
            if 'sub_tree' in tdict[item]:
                if type(tdict[item]['sub_tree']).__name__=='dict':
                    p2c_dict[tdict[item]['item_name']]=[]
                    p2c_dict=getParentChildRelative(tdict[item]['sub_tree'],p2c_dict,tdict[item]['item_name'])
        else:
            if 'sub_tree' in tdict[item]:
                if type(tdict[item]['sub_tree']).__name__=='dict':
                    p2c_dict=getParentChildRelative(tdict[item]['sub_tree'],p2c_dict,parent_name)
    return p2c_dict

#---------------------------------------------------------------------------------------------------------------------------
# Tree的依赖关系本身有天然约束，在没有外部macro或soft的依赖时，天然约束发挥作用，外部依赖不符合天然约束则报错
# 天然约束规则如下：
# 1. 父节点非D、G则子节点不存在，全部为N
# 2. 子节点为D或G，则逐级向上的父节点均为D或G
# 3. 发生改变的节点既有父节点也有子节点，按照1、2规则同时处理
#---------------------------------------------------------------------------------------------------------------------------
def traverseTree(value,target_dict,single_dict,multi_dict):
    for item in target_dict:
        # next_value用于记录上一级节点的取值，从而决定下一级节点的取值
        # 这里必须放在for循环内为父节点的每一个平级子节点传递正确的父节点取值
        next_value = value
        if target_dict[item].has_key('item_name'):
            if type(value).__name__!='str':
                added_item = {target_dict[item]['item_name']:value[target_dict[item]['item_name']]['default']}
                # 当前节点默认值为N，则其子节点取值均为N
                if value[target_dict[item]['item_name']]['default'] == 'N':
                    next_value = 'N'
            else:
                added_item = {target_dict[item]['item_name']:value}
            single_dict.update(added_item)
        if target_dict[item].has_key('sub_tree') and type(target_dict[item]['sub_tree']).__name__=='dict':
            single_dict,multi_dict = traverseTree(next_value,target_dict[item]['sub_tree'],single_dict,multi_dict)

    return single_dict,multi_dict

def downstreamTreeDepend(cfg_dict,target_dict,item_key,set_default):
    if item_key not in cfg_dict:
        return {},{}
    target_path = cfg_dict[item_key]['instance'][0].split('.')
    tree_depend_dict  = {}
    multi_depend_dict = {}

    # 定位到要修改的节点及其子节点
    for node in target_path:
        target_dict = target_dict[node]['sub_tree']

    # 遍历该字典，将每个节点添加进依赖列表中
    if set_default == False:
        tree_depend_dict,multi_depend_dict = traverseTree('N',target_dict,tree_depend_dict,multi_depend_dict)
    else:
        tree_depend_dict,multi_depend_dict = traverseTree(cfg_dict,target_dict,tree_depend_dict,multi_depend_dict)


    return tree_depend_dict,multi_depend_dict

def upstreamTreeDepend(cfg_dict,target_dict,item_key):
    if not item_key in cfg_dict.keys():
        return {},{}
    target_path = cfg_dict[item_key]['instance'][0].split('.')
    tree_depend_dict  = {}
    multi_depend_dict = {}

    # 找到所有父节点，并将他们设置为D或者G
    # 最低位不参与，最低位是当前用户点击位置不加入依赖列表
    for node in target_path[:-1]:
        if target_dict[node].has_key('item_name'):
            if 'G' in cfg_dict[target_dict[node]['item_name']]['options']:
                added_item = {target_dict[node]['item_name']:['D','G']}
                multi_depend_dict.update(added_item)
            else:
                added_item = {target_dict[node]['item_name']:'D'}
                tree_depend_dict.update(added_item)
        target_dict = target_dict[node]['sub_tree']

    return tree_depend_dict,multi_depend_dict

def SetToDefault(depend_dict, current_cfgs, changed_item):
    cfg_dict = parseConfig.config_dict['cfg']
    #log(depend_dict)
    update_default = {}
    for item in depend_dict:
        if not item.startswith('unit_'):
            continue
        if item not in current_cfgs or current_cfgs[item] == 'D' or current_cfgs[item] == 'G':
            continue
        #log(item)
        #log(depend_dict[item])
        if depend_dict[item] != 'D' and depend_dict[item] != 'G':
            #log(depend_dict[item])
            continue
        father_ins = cfg_dict[item]['instance'][0].strip()
        for ins in parseConfig.instance_map:
            if father_ins not in ins or father_ins == ins:
                continue
            #log('f s : %s %s %s' % (father_ins, ins, cfg_dict[item]['default']))
            child_item = parseConfig.instance_map[ins]
            update_default[child_item] = cfg_dict[child_item]['default']
    depend_dict.update(update_default)
    #log(update_default)


def unitDepend(base_cfg_file,usr_cfg_file,emu_cfg_file,depend_dict,current_cfgs,changed_item):

    config_dict = parseConfig.parseConfig(base_cfg_file,usr_cfg_file)
    cfg_dict    = config_dict['cfg']
    # mode_dict   = config_dict['mode']
    soft_dict   = config_dict['soft']

    tdict             = genDesignTree(cfg_dict)
    tree_depend_dict  = {}
    multi_depend_dict = {}
    up_tree_dict      = {}
    up_multi_dict     = {}
    down_tree_dict    = {}
    down_multi_dict   = {}

    # depend_dict是由changed_item触发的改变引起的所有关联配置项的依赖，以字典的形式，不带层次的组织起来的数据结构
    # 所以，本函数只需要处理由树结构隐含决定的依赖即可

    # 树形结构的隐含依赖有两个方向：向上、向下
    # 遍历所有depend_dict中的变化，向两个方向做默认修改

    for item_key,item_value in depend_dict.items():
        if 'unit_' in item_key:
            # item_value[0],选择0的原因：当前值不在依赖列表中时，默认从列表中第一项取值做静默修改
            if item_value[0] in ['D','G']:
                # 执行向下的默认修改，所有子项恢复为默认值
                down_tree_dict,down_multi_dict = downstreamTreeDepend(cfg_dict,tdict,item_key,True)
                # 执行向上的默认修改，所有父节点修改为D或G
                up_tree_dict,up_multi_dict = upstreamTreeDepend(cfg_dict,tdict,item_key)
            else:
                # 执行向下的默认修改，所有子项修改为N
                down_tree_dict,down_multi_dict = downstreamTreeDepend(cfg_dict,tdict,item_key,False)
                # 当前变化为N时，子节点的修改不会影响父节点的值
                if item_value[0] != 'N':
                    # 执行向上的默认修改，所有父节点修改为D或G
                    up_tree_dict,up_multi_dict = upstreamTreeDepend(cfg_dict,tdict,item_key)
        #
        tree_depend_dict.update(down_tree_dict)
        tree_depend_dict.update(up_tree_dict)
        multi_depend_dict.update(down_multi_dict)
        multi_depend_dict.update(up_multi_dict)


    # 如果当前的依赖已经满足，则从依赖列表中剔除
    for item_key,item_value in tree_depend_dict.items():
        if current_cfgs.has_key(item_key):
            if current_cfgs[item_key] == tree_depend_dict[item_key]:
                del tree_depend_dict[item_key]
    for item_key,item_value in multi_depend_dict.items():
        if current_cfgs.has_key(item_key):
            if current_cfgs[item_key] in multi_depend_dict[item_key]:
                del multi_depend_dict[item_key]


    return tree_depend_dict,multi_depend_dict

def genGetLog(base_cfg_file,usr_cfg_file,emu_cfg_file,current_cfgs,changed_item):
    config_dict = parseConfig.parseConfig(base_cfg_file,usr_cfg_file)
    cfg_dict    = config_dict['cfg']
    # mode_dict   = config_dict['mode']
    soft_dict   = config_dict['soft']


    base_info = ' 本次更新配置 : '+list(changed_item.keys())[0]+' -> '+list(changed_item.values())[0]

    for key,value in changed_item.items():
        #有依赖关系则打印提醒，有静默修改则发出警告
        status,has_depend,depend_info,depend_dict,cfg_temp_dict = checkDependence([key],key,value,cfg_dict,current_cfgs,0,0,'',{})
        #若无冲突，可正常更新配置；否则，取消本次修改，给出错误提示；可能发生在两个地方，1是当前修改项，2是静默修改项，均需要做check；
        conflict,conflict_info = checkConflict(key,value,cfg_dict,current_cfgs,depend_dict,0,'')

        if conflict:
            return False,depend_dict,'<i>[Error]' + base_info+'\n'+conflict_info + '</i>'
        else:
            if has_depend==1:
                base_info = '<i success>[Success]</i>' + base_info + '\n<i warning></i>\t 本次静默修改项:\n\t '+ depend_info+'静默修改完成！'
            else:
                base_info = '<i success>[Success]</i>' + base_info + depend_info
    return True,depend_dict,base_info

def checkDefaultSet(cfg_dict,cfg_out_dict):

    depend_info_all = ''
    has_depend = 0

    for key in list(cfg_out_dict.keys()):
        #有依赖关系则打印提醒，有静默修改则发出警告
        status,has_depend,depend_info,depend_dict,cfg_temp_dict = checkDependence([key],key,cfg_out_dict[key],cfg_dict,cfg_out_dict,0,0,'',{})

        #若无冲突，可正常更新配置；否则，取消本次修改，给出错误提示；可能发生在两个地方，1是当前修改项，2是静默修改项，均需要做check；
        conflict,conflict_info = checkConflict(key,cfg_out_dict[key],cfg_dict,cfg_out_dict,depend_dict,0,'')

        if conflict:
            return 2,conflict_info

        has_depend += status
        depend_info_all += depend_info

    if has_depend:
        return 1,'\n<i warning></i>\t 本次静默修改项:\n\t ' + depend_info_all

    return 0,''

#---------------------------------------------------------------------------------------------------------------------------
# Design Tree的扫描迭代器，需要遍历整个树，才能收集全部的ignore项
# - ignore_list:    ignore的item项列表
# - tdict：         根据instance生成的Design Tree的字典
# - load_dict:      cfg原始文件解析得到的包含全部信息的字典
# - can_ignore：    bool型，子节点是否需要加入ignore列表
#---------------------------------------------------------------------------------------------------------------------------
def searchIgnorItem(ignore_list,tdict,load_dict,can_ignore):

    upper_ignore = can_ignore

    for item in tdict:
        if 'item_name' in tdict[item]:
            if can_ignore:
                ignore_list.append(tdict[item]['item_name'])
            elif tdict[item]['item_name'] in load_dict:
                if load_dict[tdict[item]['item_name']] not in ['D','G']:
                    upper_ignore = True

        if type(tdict[item]['sub_tree']) is dict:
            searchIgnorItem(ignore_list,tdict[item]['sub_tree'],load_dict,upper_ignore)

        upper_ignore = can_ignore

    return ignore_list

def compareDismatchCfg(cfg_dict,load_cfg_dict,tdict):
    has_new_item    = 0
    has_del_item    = 0
    check_info      = ''
    cmp_status      = True
    after_deal_dict = {}
    new_item        = '\t 新增配置项设定以下值：\n\t '
    has_delete_item = '\t 以下配置项在新的配置下被删除：\n\t '

    ignore_list = []
    ignore_list = searchIgnorItem(ignore_list,tdict,load_cfg_dict,False)

    for cfg_item in cfg_dict:
        if cfg_item in load_cfg_dict:
            if cfg_item not in ignore_list:
                if 'type' in cfg_dict[cfg_item] and cfg_dict[cfg_item]['type'] in ['LineEdit','TextEdit']:
                    after_deal_dict[cfg_item] = load_cfg_dict[cfg_item]
                elif load_cfg_dict[cfg_item] in cfg_dict[cfg_item]['options']:
                    after_deal_dict[cfg_item] = load_cfg_dict[cfg_item]
                else:
                    after_deal_dict[cfg_item] = cfg_dict[cfg_item]['default']
                    new_item += ' -> '+cfg_item+': '+after_deal_dict[cfg_item]+'\n\t '

            del load_cfg_dict[cfg_item]
        elif cfg_item not in ignore_list:
            after_deal_dict[cfg_item] = cfg_dict[cfg_item]['default']
            new_item += ' -> '+cfg_item+': '+after_deal_dict[cfg_item]+'\n\t '
            has_new_item = 1

    if len(load_cfg_dict):
        has_del_item = 1
        for item in load_cfg_dict:
            has_delete_item += ' -> '+item+': '+load_cfg_dict[item]+'\n\t '

    if has_new_item:
        check_info = check_info + new_item
        cmp_status = False
    if has_del_item:
        check_info = check_info + has_delete_item
        cmp_status = False

    # 重新load文件后，首先确定配置项差异，然后对新的配置组合做依赖分析
    checkStatus,checkDefaultInfo = checkDefaultSet(cfg_dict,after_deal_dict.copy())

    if checkStatus == 2:
        cmp_status = False

    check_info = check_info + checkDefaultInfo

    return cmp_status,after_deal_dict,check_info

if __name__=='__main__':
    genDesignTree(sys.argv[1],sys.argv[2])


