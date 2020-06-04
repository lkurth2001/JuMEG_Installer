#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 07:58:13 2020

@author: lkurth
"""

import subprocess
import sys,os,argparse,glob
try:
   from ruamel.yaml import YAML
except:
   import yaml

def get_args(argv,parser=None,defaults=None,version=None):
   description="jumeg_installer start parameters"
   h_cuda=""
   h_name=""
   h_fjumeg=""
   h_fmne=""
   h_verbose=""
   h_save=""
   h_sorted=""
   h_show=""
   h_install=""
   if not parser:
      parser = argparse.ArgumentParser(description=description)
   else:
      parser.description=description
   if not defaults:
      defaults={
         "cuda":False,
         "name":"jumeg",
         "fjumeg":None,
         "fmne":None,
         "verbose":False,
         "save":False,
         "sorted":False,
         "show":False,
         "install":False
         }
   parser.add_argument("--cuda",action="store_true",help=h_cuda,default=defaults.get("cuda"))
   parser.add_argument("--name",help=h_name,default=defaults.get("name"))
   parser.add_argument("--fjumeg",help=h_fjumeg,default=defaults.get("fjumeg"))
   parser.add_argument("--fmne",help=h_fmne,default=defaults.get("fmne"))
   parser.add_argument("--verbose",action="store_true",help=h_verbose,default=defaults.get("verbose"))
   parser.add_argument("--save",action="store_true",help=h_save,default=defaults.get("save"))
   parser.add_argument("--sorted",action="store_true",help=h_sorted,default=defaults.get("sorted"))
   parser.add_argument("--show",action="store_true",help=h_show,default=defaults.get("show"))
   parser.add_argument("--install",action="store_true",help=h_install,default=defaults.get("install"))
   opt=parser.parse_args()
   return opt

def load_jumeg(opt):
   dict_jumeg=dict()
   if opt.fjumeg:
      with open(opt.fjumeg,"r") as f:
         dict_jumeg=yaml.load(f)
   else:
      if opt.cuda:
         subprocess.run(["curl","--remote-name","https://gist.githubusercontent.com/pravsripad/7bb8f696999985b442d9aca8ade19f19/raw/5f88b0493a4037b880d05e95e52f1c9ce9463af8/jumeg_cuda.yml"])
         with open("jumeg_cuda.yml","r") as f:
            dict_jumeg=yaml.load(f)
      else:
         subprocess.run(["curl","--remote-name","https://gist.githubusercontent.com/pravsripad/0361ffee14913487eb7b7ef43c9367fe/raw/8299c6bff6386a037af046cab5483af45c037c4f/jumeg.yml"])
         with open("jumeg.yml","r") as f:
            dict_jumeg=yaml.load(f)
   return dict_jumeg
         
def load_mne(opt):
   dict_mne=dict()
   if opt.fmne:
      with open(opt.fmne,"r") as f:
         dict_mne=yaml.load(f)
   else:
      subprocess.run(["curl","--remote-name","https://raw.githubusercontent.com/mne-tools/mne-python/master/environment.yml"])
      with open("environment.yml","r") as f:
         dict_mne=yaml.load(f)
   return dict_mne

opt=get_args(sys.argv)
fmne=load_mne(opt)
print(type(fmne))
print(fmne)
