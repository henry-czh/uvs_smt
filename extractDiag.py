#!/usr/bin/env python3

import re
import sys
import os

'''
Author  : chaozhanghu
Date    : 2023-10-07
Version : v0.1
'''

def continuation_lines(fin):
    with open(fin) as f:
        for line in f:
            line = line.rstrip('\n')
            while line.endswith('\\'):
                line = line[:-1] + next(f).rstrip('\n')
            yield line

def extractDiag(diag_file):
    diag_dict = {}
    diag_item = []
    testcase_pattern    = re.compile(r"tc=(.*?)\ ")
    testdir_pattern     = re.compile(r"path=(.*?)\ ")
    config_pattern      = re.compile(r"config=(.*?)\ ")
    scp_pattern         = re.compile(r"scp=(.*?)\ ")
    argvs_pattern       = re.compile(r"argv='(.*?)'")
    cargvs_pattern      = re.compile(r"comp_argvs='(.*?)'")
    rargvs_pattern      = re.compile(r"run_argvs='(.*?)'")
    boards_pattern      = re.compile(r"run_boards='(.*?)'")
    comment_pattern     = re.compile(r'^[ \t]*?[//#$]')
    tab_pattern         = re.compile(r'[\t]')

    if not os.path.exists(diag_file):
        #raise Exception("Diag file not exits!")
        print("Diag file not exits!")
        return

    for line in continuation_lines(diag_file):
        line = line.strip('\t')

        if not re.match(comment_pattern, line):
            line = ' '.join(line.strip('\t').split())
            diag_item = line.strip().split(' ')

            if diag_item[0] in diag_dict:
                sys.exit("<*Error> Testcase [%s] duplicate in your diag file!")

            if diag_item[0] == '' or len(diag_item) < 3:
                continue
            else:
                diag_dict[diag_item[0]] = {}

            line = line + " "

            diag_dict[diag_item[0]]['argvs']    = argvs_pattern.findall(line)
            diag_dict[diag_item[0]]['testcase'] = testcase_pattern.findall(line)
            diag_dict[diag_item[0]]['testdir']  = testdir_pattern.findall(line)
            diag_dict[diag_item[0]]['config']   = config_pattern.findall(line)
            diag_dict[diag_item[0]]['cargvs']   = cargvs_pattern.findall(line)
            diag_dict[diag_item[0]]['rargvs']   = rargvs_pattern.findall(line)
            diag_dict[diag_item[0]]['scp']      = scp_pattern.findall(line)
            diag_dict[diag_item[0]]['boards']   = boards_pattern.findall(line)

    diag_info = []
    for test in diag_dict:
        single_item = [test]
        single_item.append(' '.join(diag_dict[test]['testdir']))
        single_item.append(' '.join(diag_dict[test]['config']))
        single_item.append(' '.join(diag_dict[test]['scp']))
        single_item.append(' '.join(diag_dict[test]['cargvs']))
        single_item.append(' '.join(diag_dict[test]['rargvs']))
        single_item.append(' '.join(diag_dict[test]['boards']))
        single_item.append(' '.join(diag_dict[test]['argvs']))

        diag_info.append(single_item)

    return diag_info
    