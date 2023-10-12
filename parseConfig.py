#!/usr/bin/env python2
#_*_ coding:UTF-8 _*_

'''
author  : Chao Zhanghu chaozhanghu@phytium.com.cn
version : v1.0
date    : 2022-08-03
function:
    解析配置文件.
'''

import os
import sys
import re
import getpass
import collections
from log import log

config_dict = {}
instance_map = {}

def continuation_line(fin1):
    # 去除所有注释
    # 拼接所有 \ 结尾
    f1_ct = open(fin1).read()
    # logger.Print('re0 %s\n%s', fin1, f1_ct)
    f1_ct = re.sub(r'/\*.*?\*/', '', f1_ct, flags=re.S)
    f1_ct = re.sub(r'\s*(//|# ).*?\n', '\n', f1_ct, flags=re.S)
    f1_ct = re.sub(r'\s*\\\s*\n\s*', ' ', f1_ct, flags=re.S)
    f1_ct = re.sub(r'\n{2,}', '\n\n', f1_ct, flags=re.S)
    # logger.Print('re1 %s\n%s', fin1, f1_ct)
    f1_ct = f1_ct.split('\n')
    if fin1.endswith('all.cfg') and '/testbench' in fin1:
        f1_ct.append('#include "../../../uvs_kernel/config/all_kernel.cfg"')
    return f1_ct

def extract_include(f,pre_context,parameter_dict):
    context = pre_context
    include_pattern = re.compile(r'^[ \t]*?#include ')
    file_pattern    = re.compile(r'".*?"')
    help_pattern    = re.compile(r'^[ \t]*?\[help\]')
    value_pattern   = re.compile(r'==(.*?)[\s\n]')
    cur_dir         = os.path.dirname(f)

    for line in continuation_line(f):
        line = line%parameter_dict

        # 支持在正在配置项找那个使用if，但是如果两个条件都满足，后面覆盖前面
        ifcondition = True
        if not re.match(help_pattern,line):
            if ' if ' in line:
                #参与运算的是if后面的表达式
                condition = line.split(' if ')[1]

                #Python中等价判断使用 双等号 
                condition=condition.replace('=','==') + '\n'

                #print('%s' % (re.findall(value_pattern,line)))
                
                #找到所有变量值，添加引号，变成字符串，参与python bool表达式计算
                condition = re.sub(value_pattern,r'=="\1" ',condition)

                #print("%s" % (parameter_dict))
                #print line.split(' if ')[1]

                ifcondition = eval(condition,parameter_dict)
                line = line.split(' if ')[0] + '\n'

        if ifcondition:
            context += line + '\n'

        if re.match(include_pattern,line):
            if len(line.split(' with '))==2:
                parameters = line.split(' with ')[1].strip().split(' ')
            elif len(line.split(' wiht '))==1:
                parameters = []
                parameter_dict = {}
            else:
                sys.exit('警告：include时with使用错误！')

            for p in parameters:
                para_key   = p.split('=')[0]
                para_value = p.split('=')[1]
                parameter_dict[para_key]=para_value

            include_f = re.findall(file_pattern,line)
            context = extract_include(os.path.join(cur_dir,include_f[0].strip('"')),context,parameter_dict)

    return context

def continuation_lines(fin1,fin2):
    f1 = extract_include(fin1,'',{})
    f2 = extract_include(fin2,'',{})

    usr = getpass.getuser()
    pid = os.getpid()
    pid = str(pid)
    debug_dir = os.path.join(os.getenv('HOME'),'.uvs')

    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    debug = open(debug_dir+'/f1_tmp.'+pid,'w')
    debug.write(f1)
    debug.close()
    debug = open(debug_dir+'/f2_tmp.'+pid,'w')
    debug.write(f2)
    debug.close()

    with open(debug_dir+'/f1_tmp.'+pid) as f1_ct,open(debug_dir+'/f2_tmp.'+pid) as f2_ct:
        os.system("cp %s/f1_tmp.%s /tmp/f1_tmp.%s" % (debug_dir,pid,usr))
        os.system("cp %s/f2_tmp.%s /tmp/f2_tmp.%s" % (debug_dir,pid,usr))
        os.system("rm %s/f1_tmp.%s" % (debug_dir,pid))
        os.system("rm %s/f2_tmp.%s" % (debug_dir,pid))
        return f1_ct.readlines()+f2_ct.readlines()

def parseConfig(config_src_path,config_usr_path):

    cbs_mode    = 0
    tb_top      = ''
    
    # dict天然无序,图形界面显示时有排序需求，通过collections转变为有序字典
    cfg_dict    = collections.OrderedDict()
    mode_dict   = {}
    lib_dict    = {}
    dpd_list    = []
    dpd_dict    = {}
    dpd_key_list= []

    overwrite_pattern       = re.compile(r'^[ \t]*?<overwrite_item=')
    item_pattern            = re.compile(r'^[ \t]*?<config_item=')
    # comment_pattern         = re.compile(r'^[ \t]*?[//|#|$]')
    dpd_pattern             = re.compile(r'{.*?}')
    top_pattern             = re.compile(r'^[ \t]*?<tb_top=')
    inst_pattern            = re.compile(r'^[ \t]*?\[instance\]')
    inst_pld_pattern        = re.compile(r'^[ \t]*?\[instance_pld\]')
    mdul_pattern            = re.compile(r'^[ \t]*?\[module\]')
    opts_pattern            = re.compile(r'^[ \t]*?\[options\]')
    deft_pattern            = re.compile(r'^[ \t]*?\[default\]')
    help_pattern            = re.compile(r'^[ \t]*?\[help\]')
    group_pattern            = re.compile(r'^[ \t]*?\[group\]')
    dpdon_pattern           = re.compile(r'^[ \t]*?\[depends on\]')
    mode_pattern            = re.compile(r'^[ \t]*?<config_mode=')
    type_pattern            = re.compile(r'^[ \t]*?\[type\]')
    extatt_pattern          = re.compile(r'^[ \t]*?\[ExtAtt\]')
    const_config_pattern    = re.compile(r'^[ \t]*?\[const_config\]')

    libmap_pattern          = re.compile(r'^[ \t]*?\<lib_map=')
    mem_type_pattern        = re.compile(r'\[.*?\]')
    mem_load_pattern        = re.compile(r'^[ \t]*?(\[dimm_load\]|\[flash_load\]|\[scp_rom_load\]|\[ap_rom_load\]|\[efuse_load\]|\[scto_rom_load\]|\[sim_load\])')
    uart_path_pattern       = re.compile(r'^[ \t]*?\[uart_path\]')
    uart_pattern            = re.compile(r'^[ \t]*?(\[uart_rx_path\]|\[uart_path\]|\[uart_tx_path\]|\[uart_cmd\]|\[uart_title\]|\[scp_uart_cmd\]|\[scp_uart_rx_path\]|\[scp_uart_tx_path\])')
    wrapper_type_pattern    = re.compile(r'^[ \t]*?\[wrapper_type\]')
    hdl_path_pattern        = re.compile(r'^[ \t]*?\[hdl_path\]')
    hdl_path_netlist_pattern= re.compile(r'^[ \t]*?\[hdl_path_netlist\]')

    cfg_key                 = ''
    soft_dict               = {}
    project_pattern         = re.compile(r'[ \t]*?<project=')
    soft_pattern            = re.compile(r'[ \t]*?<config_software=')
    include_pattern         = re.compile(r'[ \t]*?\[include\]')
    coreid_pattern          = re.compile(r'[ \t]*?\[CoreID\]')

    chk_keys                = []
    macro_keys              = ['options','default']
    unit_keys               = ['options','default','instance']

    #cfg_dict['keys_order'] = []

    for line in continuation_lines(config_src_path+'/all.cfg',config_usr_path+'/usr.cfg'):
        line = re.sub(' +',' ',line)

        if re.match(overwrite_pattern,line):
            cfg_key=re.sub('\<overwrite_item\=','',line).strip().strip('>')
            cfg_dict[cfg_key]={}

        elif re.match(item_pattern,line) or re.match(soft_pattern,line):
            #增加对上一个item项的必要配置内容完整性检查
            if cfg_key in cfg_dict:
                if 'unit_' in cfg_key:
                    chk_keys = unit_keys
                else:
                    chk_keys = macro_keys

                for chk_key in chk_keys:
                    if chk_key not in cfg_dict[cfg_key].keys():
                        sys.exit("<*Error> 配置项%s 缺少 %s 内容！" % (cfg_key,chk_key))

            if re.match(item_pattern,line):
                cfg_key=re.sub('\<config_item\=','',line).strip().strip('>')
            elif re.match(soft_pattern,line):
                cfg_key=re.sub('\<config_software\=','',line).strip().strip('>')

            if cfg_key in cfg_dict:
                sys.exit("<*Error> item [%s] 在你的cfg文件中多次出现." % (cfg_key))

            cfg_dict[cfg_key]={}

            if re.match(soft_pattern,line):
                soft_dict[cfg_key]=''
                cfg_dict[cfg_key]['soft_info'] = {}

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# hardware configs
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #------------------------------------------------------
        # 收集item的可选项，instance时包含module名和所属lib
        #------------------------------------------------------
        elif re.match(opts_pattern,line) and re.sub('\[options\]','',line).strip().split(' ') != '':
            options = re.sub('\[options\]','',line).strip().split(' ')
            cfg_dict[cfg_key]['options'] = []
            cfg_dict[cfg_key]['module'] = {}
            cfg_dict[cfg_key]['lib'] = {}
            cfg_dict[cfg_key]['zebu_lib'] = {}
            for op in options:
                if len(op.split(':'))>1:
                    cfg_dict[cfg_key]['module'][op.split(':')[0]]=op.split(':')[1]
                    cfg_dict[cfg_key]['lib'][op.split(':')[0]]=''
                if len(op.split(':'))>2:
                    cfg_dict[cfg_key]['lib'][op.split(':')[0]]=op.split(':')[2]
                if len(op.split(':'))>3:
                    cfg_dict[cfg_key]['zebu_lib'][op.split(':')[0]]=op.split(':')[3]
                cfg_dict[cfg_key]['options'].append(op.strip().split(':')[0])
            #cfg_dict[cfg_key]['options'].append('*')

        #------------------------------------------------------
        # 默认值
        #------------------------------------------------------
        elif re.match(deft_pattern,line) and re.sub('\[default\]','',line).strip() != '':
            cfg_dict[cfg_key]['default'] = re.sub('\[default\]','',line).strip()

        #------------------------------------------------------
        # help帮助信息，会在web界面的鼠标停留时显示
        #------------------------------------------------------
        elif re.match(help_pattern,line) and re.sub('\[help\]','',line).strip() != '':
            cfg_dict[cfg_key]['help'] = re.sub('\[help\]','',line).strip()

        #------------------------------------------------------
        # group分组信息
        #------------------------------------------------------
        elif re.match(group_pattern,line) and re.sub('\[group\]','',line).strip() != '':
            cfg_dict[cfg_key]['group'] = re.sub('\[group\]','',line).strip()

        #------------------------------------
        # 收集coreid信息，将用于裸机编译链
        #------------------------------------
        elif re.match(coreid_pattern,line) and re.sub('\[CoreID\]','',line).strip() != '':
            core_id = re.sub('\[CoreID\]','',line).strip()
            cfg_dict[cfg_key]['coreid']=core_id

        #------------------------------------------------------
        # item在web上显示的类型，分为下拉菜单、文本框、文本行
        #------------------------------------------------------
        elif re.match(type_pattern,line) and re.sub('\[type\]','',line).strip() != ' ':
            cfg_dict[cfg_key]['type'] = re.sub('\[type\]','',line).strip()

        elif re.match(extatt_pattern,line) and re.sub('\[ExtAtt\]','',line).strip() != ' ':
            extAtts = re.sub('\[ExtAtt\]','',line).strip().split(':')
            cfg_dict[cfg_key]['ExtAtt'] = {}
            try:
                cfg_dict[cfg_key]['ExtAtt'][extAtts[0]] = extAtts[1]
            except:
                raise Exception("*E [format error] \n%s \n The right format is \"OP:emu_ignore\"." % (line))

        #------------------------------------------------------
        # 依赖关系，该信息涉及复杂的后台算法
        #------------------------------------------------------
        elif re.match(dpdon_pattern,line):
            dpd_str = re.sub('','',line).strip()
            dpd_dict={}
            try:
                if dpd_str != '':
                    dpd_list = re.findall(dpd_pattern,dpd_str)
                    for item in dpd_list:
                        #首先将依赖项与被依赖项分开
                        to_relay = item.split(':')[0].strip()
                        be_relied = item.split(':')[1].strip()
                        #将依赖项和被依赖项分组
                        # 举个例子：
                        # {A,B:item1=A,B,C;item2=D}
                        # 当前项等于A或者B时，item1的值在A B C中任选其一，item2的值必须等于D
                        to_relay_list = to_relay.split(',')
                        be_relied_list = be_relied.split(';')

                        #为每个依赖项建立字典
                        for relay_item in to_relay_list:
                            relay_item = relay_item.strip('{').strip()
                            if relay_item in dpd_dict.keys():
                                dpd_key_list = dpd_dict[relay_item]
                                #逐一增加被依赖项
                                for be_relied_item in be_relied_list:
                                    be_relied_item = re.sub('.options','',be_relied_item)
                                    be_relied_item_name = be_relied_item.split('=')[0].strip('}').strip()
                                    be_relied_item_value= be_relied_item.split('=')[1].strip('}').strip()
                                    #2022-06-06 被依赖项的可选配置值可能是一个范围，而不是某个特定值，值之间以‘,’分割
                                    be_relied_item_value=be_relied_item_value.split(',')
                                    dpd_key_list.append({be_relied_item_name:be_relied_item_value})
                            else:
                                dpd_key_list=[]
                                #逐一增加被依赖项
                                for be_relied_item in be_relied_list:
                                    be_relied_item = re.sub('.options','',be_relied_item)
                                    be_relied_item_name = be_relied_item.split('=')[0].strip('}').strip()
                                    be_relied_item_value= be_relied_item.split('=')[1].strip('}').strip()
                                    #2022-06-06 被依赖项的可选配置值可能是一个范围，而不是某个特定值，值之间以‘,’分割
                                    be_relied_item_value=be_relied_item_value.split(',')
                                    dpd_key_list.append({be_relied_item_name:be_relied_item_value})
                            dpd_dict[relay_item]=dpd_key_list
                    cfg_dict[cfg_key]['depends on'] = dpd_dict
            except:
                raise Exception("*E [format error] at line : %s " % (line))


        #------------------------------------------------------
        # 收集instance信息，有instance说明环境当前选择cbs模式
        #------------------------------------------------------
        elif re.match(inst_pattern,line) and re.sub('\[instance\]','',line).strip() != '':
            cfg_dict[cfg_key]['instance'] = re.sub('\[instance\]','',line).strip().split(' ')
            cbs_mode = 1

        elif re.match(inst_pld_pattern, line) and re.sub('\[instance_pld\]', '', line).strip() != '':
            cfg_dict[cfg_key]['instance_pld'] = re.sub('\[instance_pld\]', '', line).strip()

        #---------------------------
        # collect uart model info
        #---------------------------
        elif re.match(uart_pattern,line):
            uart_type = re.findall(uart_pattern,line)[0].strip('[|]')
            search_text = '\[%s\]' % (uart_type)
            cfg_dict[cfg_key][uart_type] = re.sub(search_text,'',line).strip()

        #---------------------------
        # 收集wrapper type信息
        #---------------------------
        elif re.match(wrapper_type_pattern,line) and re.sub('\[wrapper_type\]','',line).strip() != '':
            cfg_dict[cfg_key]['wrapper_type'] = re.sub('\[wrapper_type\]','',line).strip()

        elif re.match(hdl_path_netlist_pattern, line) and re.sub('\[hdl_path_netlist\]', '', line).strip() != '':
            items = re.sub('\[hdl_path_netlist\]', '', line).strip()
            items = re.findall(r'\{(\w+?):(.+?)\}', items)
            hdl_path = {}
            for item in items:
                hdl_path[item[0]] = item[1]
            # print(hdl_path)
            cfg_dict[cfg_key]['hdl_path_netlist'] = hdl_path

        #------------------------------------
        # 收集与speedbridge相关的hdl路径
        #------------------------------------
        elif re.match(hdl_path_pattern,line) and re.sub('\[hdl_path\]','',line).strip() != '':
            line_list = re.findall(dpd_pattern,line)
            for hdl in line_list:
                wrap_key,hdl_path = hdl.strip('{').strip('}').split(':')
                if 'wrap_keys' not in cfg_dict[cfg_key]:
                    cfg_dict[cfg_key]['wrap_keys'] = {}
                if wrap_key not in cfg_dict[cfg_key]['wrap_keys']:
                    cfg_dict[cfg_key]['wrap_keys'][wrap_key] = []
                cfg_dict[cfg_key]['wrap_keys'][wrap_key].append(hdl_path)

        #---------------------------
        # collect uart model info
        #---------------------------
        elif re.match(uart_path_pattern,line) and re.sub('\[uart_path\]','',line).strip() != '':
            cfg_dict[cfg_key]['uart_path'] = re.sub('\[uart_path\]','',line).strip()

        #---------------------------
        # collect memory load info
        #---------------------------
        elif re.match(mem_load_pattern,line):
            mem_type = re.findall(mem_type_pattern,line)[0].strip('[|]')
            cfg_dict[cfg_key][mem_type] = {}
            mem_loads_list = re.findall(dpd_pattern,line)
            for item in mem_loads_list:
                valid_item   = item.strip().strip('{|}')
                #if cfg_dict[cfg_key][mem_type].has_key(valid_item.split(':')[0]):
                if valid_item.split(':')[0] in cfg_dict[cfg_key][mem_type]:
                    cfg_dict[cfg_key][mem_type][valid_item.split(':')[0]].append(valid_item.split(':')[1])
                else:
                    valid_item_dict = {valid_item.split(':')[0]:[valid_item.split(':')[1]]}
                    cfg_dict[cfg_key][mem_type].update(valid_item_dict)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# software configs
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif re.match(project_pattern,line):
            project=re.sub('\<project\=','',line).strip().strip('>')
            soft_dict['project']=project

        elif re.match(include_pattern,line) and len(re.sub('\[include\]','',line).strip().split(' ')) > 0:
            cfg_dict[cfg_key]['include'] = re.sub('\[include\]','',line).strip().split(' ')

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# globle configs 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif re.match(mode_pattern,line):
            mode_name = re.sub('\<config_mode\=','',line).strip().strip('>')
            mode_dict[mode_name]={}

        elif re.match(const_config_pattern,line):
            const_config=re.sub('\[const_config\]','',line).strip().strip('{').strip('}')
            const_list = const_config.split(',')
            for item in const_list:
                mode_dict[mode_name][item.split('=')[0].strip()] = item.split('=')[1].strip()

        elif re.match(top_pattern,line):
            top_context=re.sub('\<tb_top\=','',line).strip().strip('>')
            tb_top=top_context

        elif re.match(libmap_pattern,line):
            line = ' '.join(line.split())
            libr=re.sub('\<lib_map\=','',line.split('>')[0]).strip().strip('>')
            lib_dict[libr]=line.split(' ')[1]

        if cfg_key in soft_dict:
            if 'options' in cfg_dict[cfg_key]:
                for opt in cfg_dict[cfg_key]['options']:
                    keyword = re.findall(r'^[ ]*?\[(.+?)\]',line)
                    if len(keyword)>0 and opt == keyword[0]:
                        soft_info_m = re.sub('\[%s\]' % (opt),'',line).strip().split(' ')
                        cfg_dict[cfg_key]['soft_info'][opt] = []
                        if len(soft_info_m)>0:
                            for item_i in soft_info_m:
                                cfg_dict[cfg_key]['soft_info'][opt].append(eval(item_i))
    
    global config_dict
    config_dict = {}
    config_dict['cbs']  = cbs_mode
    config_dict['top']  = tb_top
    config_dict['cfg']  = cfg_dict
    config_dict['lib']  = lib_dict
    config_dict['soft'] = soft_dict
    config_dict['mode'] = mode_dict
    
    #debug = open('/tmp/debug','w')
    #debug.write("%s" % (cfg_dict))
    #debug.close()

    # 将父子依赖加入[depends on]
    global instance_map
    instance_map = {}
    for item in cfg_dict:
        if 'instance' not in cfg_dict[item]:
            continue
        ins = cfg_dict[item]['instance'][0].strip()
        instance_map[ins] = item
        # log('%s -> %s' % (ins,item))
        # log('%s' % cfg_dict[item]['depends on'])
        # chip_tb.skt1.die3.top.noc_wrapper.NOC.u_tomahawk.u_cha_nid92 -> unit_SKT1DIE3_CHA_NID92
        # {'D': [{'unit_SKT1DIE3_CHA_NID93': ['D']},{'unit_SKT1DIE3_CHA_NID93': ['G']}],'N': [{'unit_SKT1DIE3_CHA_NID93': ['N']}]}
    for ins,child in instance_map.items():
        paths = ins.split('.')
        i = -1
        while len(paths[:i]) > 1:
            father_ins = '.'.join(paths[:i])
            if father_ins not in instance_map:
                i -= 1
                continue
            father = instance_map[father_ins]

            if 'N' not in cfg_dict[father]['depends on']:
                cfg_dict[father]['depends on']['N'] = []
            cfg_dict[father]['depends on']['N'].append({child: ['N']})

            if 'D' not in cfg_dict[child]['depends on']:
                cfg_dict[child]['depends on']['D'] = []
            cfg_dict[child]['depends on']['D'].append({father: ['D','G']})

            if 'G' not in cfg_dict[child]['depends on']:
                cfg_dict[child]['depends on']['G'] = []
            cfg_dict[child]['depends on']['G'].append({father: ['D','G']})
            # log('%s -> %s' % (father,child))
            break

    return config_dict

if __name__=="__main__":
    config_dict = parseConfig(sys.argv[1],sys.argv[2])
    if config_dict['cbs']:
        print(1)
