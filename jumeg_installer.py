#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 07:58:13 2020

@author: lkurth
"""

import subprocess
import sys,os,argparse,glob
import logging
from copy import deepcopy

import collections,pprint

"""try:
   from ruamel.yaml import YAML as yaml
except:
   import yaml"""
import yaml
   
logger = logging.getLogger('jumeg')
logging.basicConfig(level=logging.DEBUG)

DEVNULL=subprocess.DEVNULL


remote_name={
   "jumeg_cuda":"https://gist.githubusercontent.com/pravsripad/7bb8f696999985b442d9aca8ade19f19/raw/5f88b0493a4037b880d05e95e52f1c9ce9463af8/jumeg_cuda.yml",
   "jumeg":"https://gist.githubusercontent.com/pravsripad/0361ffee14913487eb7b7ef43c9367fe/raw/8299c6bff6386a037af046cab5483af45c037c4f/jumeg.yml",
   "mne":"https://raw.githubusercontent.com/mne-tools/mne-python/master/environment.yml"
   }


def check_conda():
   if subprocess.run(["which","conda"],stdout=DEVNULL).returncode==1:
      logger.error("You need to hav anaconda installed!")
      sys.exit(0)


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
   h_cuda="Downloads jumeg file with cuda support"
   h_name="Sets the name of the new environment file"
   h_fjumeg="Can set a file used as jumeg file instead of downloading"
   h_fmne="Can set a file used as mne file instead of downloading"
   h_verbose="Makes the installation more verbose"
   h_save="Saves the merged environment file"
   h_sorted="Sorts the new environment file"
   h_show="Shows the new environment file in the shell"
   h_install="Installs a new conda environment"
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
   if len(argv)<2:
       parser.print_help()
       sys.exit(-1)
   parser.add_argument("--cuda",action="store_true",help=h_cuda,default=defaults.get("cuda"))
   parser.add_argument("--name",help=h_name,default=defaults.get("name"))
   parser.add_argument("--fjumeg",help=h_fjumeg,default=defaults.get("fjumeg"))
   parser.add_argument("--fmne",help=h_fmne,default=defaults.get("fmne"))
   parser.add_argument("-v,--verbose",action="store_true",help=h_verbose,default=defaults.get("verbose"))
   parser.add_argument("--save",action="store_true",help=h_save,default=defaults.get("save"))
   parser.add_argument("--sorted",action="store_true",help=h_sorted,default=defaults.get("sorted"))
   parser.add_argument("--show",action="store_true",help=h_show,default=defaults.get("show"))
   parser.add_argument("--install",action="store_true",help=h_install,default=defaults.get("install"))
   opt=parser.parse_args()
   return opt

def _load_env_file(name):
    subprocess.run(["curl","--remote-name",remote_name.get(name)])
    fname = os.path.basename( remote_name.get(name) )
    return fname

def _file_to_dict(fname):
   env_dict=dict()
   with open(fname,"r") as f:
        env_dict= yaml.safe_load(f)
   return env_dict

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
   if opt.fjumeg:
      fname = opt.fjumeg
   elif opt.cuda:
      fname=_load_env_file("jumeg_cuda")
   else:
      fname=_load_env_file("jumeg")

   return _file_to_dict(fname)

def check_version(data=dict()):
    result=dict()
    for key in data.keys():
        akt=data.get(key)
        if type(akt)==list:
            for elem in akt:
                if type(elem)==dict:
                    result[elem]=check_version(elem)
                elif type(elem)==str:
                    pass
       
def merge_dicts(mne=dict(),jumeg=dict()):
    pass
  
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
   if opt.fmne:
      fname = opt.fmne
   else:
      fname=_load_env_file("mne")
   
   return _file_to_dict(fname)


def save_env(opt,env=dict()):
   """
   saves the new environment file with the filename opt.name + .yaml if save is true or overwrites an existing file
   
   Parameters
   ----------
   opt : list of given parameters
   env : dict to save
   """
   if opt.save and bool(env):
      fname=opt.name + ".yaml"
      with open(fname,"w") as f:
         yaml.dump(env,f)


def show(opt,env):
   """
   shows the new generated environment file if show is true
   
   Parameters
   ----------
   opt : list of given parameters
   env : dict with values of new environment file
   """
   if opt.show and env:
      logger.info(dict2str(env))
   elif opt.show:
      logger.error("No environment file found")
      
      
def sort_data(opt,env):
   """
   sorts env dict and returns the sorted dict if sort=true
   
   Parameters
   ----------
   opt : list of given parameters
   env : dict with values of environment file
   
   Returns
   -------
   env : sorted dict 
   """
   if opt.sorted and env:
      result=dict()
      for key in sorted(env):
         result[key]=env.get(key)
      return result
   else:
       return env
   # ToDo
   # eventual special sorting method


def install(opt):
    """
    function to install the new conda environment
    """
    if opt.install:
        fname=opt.name + ".yaml"
        if check_envs(opt.name):
            subprocess.run(["conda","deactivate"],stdout=DEVNULL)
            subprocess.run(["conda","env","update","-n",opt.name,"--file",fname])
            subprocess.run(["conda","activate",opt.name],stdout=DEVNULL)
        else:
            subprocess.run(["conda","env","create","-f",fname])
            subprocess.run(["conda","activate",opt.name],stdout=DEVNULL)


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
 
   
def update_and_merge(din, u, depth=-1,do_copy=True):
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
           if isinstance(v, collections.abc.Mapping) and not depth == 0:
              r = update_and_merge(d.get(k, {}), v, depth=max(depth - 1, -1))
              d[k] = r
           elif isinstance(d, collections.abc.Mapping):
              d[k] = u[k]
           else:
              d = {k: u[k]}
        
       return d 
 
   
def run():
   check_conda()
   opt = get_args(sys.argv)
   mne = load_mne(opt)
   mne["name"] = opt.name
   jumeg = load_jumeg(opt)
   data = update_and_merge(jumeg,mne)
   data = sort_data(opt,data)
   show(opt,data)
   save_env(opt,data)
   install(opt)

def check_envs(name):
   envs = subprocess.check_output(["conda","env","list"]).splitlines()
   for lines in envs:
      lines=lines.decode("utf-8")
      if lines == name:
         return True
   return False   
   
   


'''
Function examples 
       
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
   run()


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

