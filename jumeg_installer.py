#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 07:58:13 2020

@author: lkurth
"""

import subprocess
import sys,os,argparse,glob

import collections,pprint

try:
   from ruamel.yaml import YAML
except:
   import yaml


remote_name={
   "jumeg_cuda":"https://gist.githubusercontent.com/pravsripad/7bb8f696999985b442d9aca8ade19f19/raw/5f88b0493a4037b880d05e95e52f1c9ce9463af8/jumeg_cuda.yml",
   "jumeg":"https://gist.githubusercontent.com/pravsripad/0361ffee14913487eb7b7ef43c9367fe/raw/8299c6bff6386a037af046cab5483af45c037c4f/jumeg.yml",
   "mne":"https://raw.githubusercontent.com/mne-tools/mne-python/master/environment.yml"
   }

def get_args(argv,parser=None,defaults=None,version=None):
   """
   function to parse the given parameters from the shell
   
   Parameters
   ----------
   argv : given parameters
   parser : ArgumentParser
   defaults : list with default parameters
   version : str version name
   
   Returns
   -------
   opt : list of parsed parameters
   """
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
   """
   function to load the jumeg environment file as a python dict
   
   Parameters
   ----------
   opt : list of given parameters
   
   Returns
   -------
   dict_jumeg : dict filled with values from jumeg environment file
   """
   dict_jumeg=dict()
   if opt.fjumeg:
      fname = opt.fjumeg
   elif opt.cuda:
      subprocess.run(["curl","--remote-name",remote_name.get("jumeg_cuda")])
      fname = os.path.basename( remote_name.get("jumeg_cuda") )
   else:
      subprocess.run(["curl","--remote-name",remote_name.get("jumeg")])
      fname = os.path.basename( remote_name.get("jumeg") )

   with open(fname,"r") as f:
        dict_jumeg = yaml.load(f)
   return dict_jumeg
       
  
def load_mne(opt):
   """
   function to load the mne environment file as a python dict
   
   Parameters
   ----------
   opt : list of given parameters
   
   Returns
   -------
   dict_mne : dict filled with values from mne environment file
   """
   dict_mne=dict()
   if opt.fmne:
      fname = opt.fmne
   else:
      subprocess.run(["curl","--remote-name",remote_name.get("mne")])
      fname = os.path.basename( remote_name.get("mne") )
   with open(fname,"r") as f:
         dict_mne=yaml.load(f)

   return dict_mne


def save_env(opt,env):
   """
   saves the new environment file with the filename opt.name + .yaml if save is true or overwrites an existing file
   
   Parameters
   ----------
   opt : list of given parameters
   env : dict to save
   """
   if opt.save and env:
      fname=opt.name
      if not fname.endswith(".yaml"):
         fname=fname + ".yaml"
      with open(fname,"w") as f:
         yaml.dump(env,f)

def merge_dicts(opt,mne,jumeg):
   env=dict()
   for key in mne.keys():
      env[key]=mne.get(key)
   for key in jumeg.keys():
      if not env.get(key):
         env[key]=jumeg.get(key)
   return env



#=== FB stuff examples

def dict2str(d,intend=2):
    """
    wrapper / helper for pretty printing
 
    Parameters
    ----------
    d : dict to pretty print
    intend: int, 2
     
    Returns
    -------
    dict as string
    """
    pp = pprint.PrettyPrinter(indent=intend)
    return ''.join(map(str,pp.pformat(d)))     


'''
Function examples 
 
   def _update_and_merge(self, din, u, depth=-1,do_copy=True):
       """ update and merge dict parameter overwrite defaults
        
       Parameters
       ----------
       dict with defaults parameter
       dict with parameter to merge or update
       depth: recusive level <-1>
                
       Result
       -------
       dict with merged and updated parameters
        
       Example
       -------
       copy from:
       http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        
       Recursively merge or update dict-like objects. 
       >>> update({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
       {'k1': {'k2': {'k3': 3}}, 'k4': 4}
       return dict
       """
        
       if do_copy:
          d = deepcopy(din)
       else:
          d = din 
       for k, v in u.items():
           if isinstance(v, collections.Mapping) and not depth == 0:
              r = self._update_and_merge(d.get(k, {}), v, depth=max(depth - 1, -1))
              d[k] = r
           elif isinstance(d, collections.Mapping):
              d[k] = u[k]
           else:
              d = {k: u[k]}
        
       return d    
       
   def _check_keys_in_config(self,config=None,keys_to_check=None):
       """
       

       Parameters
       ----------
       config : TYPE, optional
           DESCRIPTION. The default is None.
       keys_to_check : TYPE, optional
           DESCRIPTION. The default is None.

       Returns
       -------
       config : dict, config dict 
       missing_keys : dict, <missing keys> in config dict

       """
       if not config:
          config = self.config 
       k = config.keys()
       
       if not keys_to_check:
          keys_to_check = self.keys_to_check
       
       missing_keys = dict() 
       #-- ToDo make recursive
       for k in keys_to_check.keys():
           if k in config:
               
              kdefaults = keys_to_check[k]
              if isinstance(config[k],dict):
                 kcfg = config[k].keys()
              else:
                 kcfg = config[k] 
              kdiff     = ( set( kdefaults) - set( kcfg ) )
              if kdiff:
                 missing_keys[k] = kdiff  
           else:
              missing_keys[k] = []  
              
       if missing_keys:  
          msg = ["ERROR  missing keys in config"]
          for k in missing_keys:
              msg.append(" --> {}:\n  -> {}".format(k,missing_keys))
          logger.error("\n".join(msg))
       
       return config,missing_keys     
 
'''






if __name__=="__main__":
   opt=get_args(sys.argv)
   mne=load_mne(opt)
   jumeg=load_jumeg(opt)
   data = merge_dicts(opt,mne,jumeg)
   
   print("\n---> Merged Files:\n")
   print( dict2str(data) )


   # ToDo
   #-> check dict key for pip 
   #-> save merged dict in new file with env-name => opt.name +.yml
   # - -> sort keys
   #---
   # -> install with conda
   # - -> if opt.install ...
   # - - -> subprocess.run() ...

   # ToDo
   # more infos use logging no print
   # doc strings for def()

