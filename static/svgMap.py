#!/bin/env python

import os
import json
from lxml import etree
import readConfiguration

base_cfg_file = os.getenv("BASE_CONFIG_FILE")
usr_cfg_file  = os.getenv("USER_CONFIG_FILE")

cfg_dict,mode_dict = readConfiguration.readConfiguration(base_cfg_file,usr_cfg_file)

parser = etree.HTMLParser(encoding='utf-8')
svg = etree.parse("S5000-arch.svg",parser=parser)

links = svg.xpath("//a")

for link in links:
    link_name = link.attrib.get('xlink:href')
    #print(link_name)
    if len(link.xpath("./g/desc"))>0:
        for rect in link.xpath("./g/rect"):
            if link_name in cfg_dict:
                rect.set('data-config','')
                rect.set('data-value',cfg_dict[link_name]['default'])
                rect.set('data-values',json.dumps(cfg_dict[link_name]['options']))

output = open('../s5000svg.html','w')
output.write(etree.tostring(svg,encoding='utf-8',pretty_print=True,method='html').decode('utf-8'))
#print(etree.tostring(svg,encoding='utf-8',pretty_print=True,method='html'))

