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
   """
   function which checks if anaconda is installed, if not the programme stops and sends an error
   """
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
    """
    function to download an environment file with the name name 
    
    Parameters
    ----------
    name : name of the file to download
    
    Returns
    -------
    fname : name of the downloaded env file
    """
    subprocess.run(["curl","--remote-name",remote_name.get(name)])
    fname = os.path.basename( remote_name.get(name) )
    return fname

def _file_to_dict(fname):
   """
   function to build a python dict out of a file
   
   Parameters
   ----------
   fname : file which should be converted to a dict
   
   Returns
   -------
   env_dict : dict build out of the env file
   """
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
    """
    checks the verions of the parameters in the dict and returns them
    
    Parameters
    ----------
    data : dict which is checked
    
    Returns
    -------
    result : dict with the version names and numbers
    """
    result=dict()
    for key in data.keys():
        akt=data.get(key)
        if type(akt)==list:
            for elem in akt:
                if type(elem)==dict:
                    for key2 in elem.keys():
                       result[key2]=check_version(elem)
                elif type(elem)==str:
                    if len(elem.split(">"))>1:
                       result[elem.split(">")[0]]=elem
                    elif len(elem.split("<"))>1:
                       result[elem.split("<")[0]]=elem
                    elif len(elem.split("="))>1:
                       result[elem.split("=")[0]]=elem
                    else:
                       continue
    return result
 
def check_version2(data=dict()):
   result=list()
   for key in data.keys():
      pass
 
def compare_versions(mne=dict(),jumeg=dict()):
    """
    compares the two version dicts to delete the unnecessary ones
    and then return the updated dicts
    
    Parameters
    ----------
    mne : dict with the mne parameters
    jumeg : dict with the jumeg parameters
    
    Returns
    -------
    jumeg : updated dict
    """
    mne=check_version(mne)
    jumeg=check_version(jumeg)
    tmp=list()
    for key in jumeg.keys():
       if not key in mne.keys():
          tmp.append(key)
    for key in tmp:
       jumeg.pop(key)
    return jumeg

def compare_versions2(mne=dict(),jumeg=dict()):
   mne=check_version(mne)
   jumeg=check_version(jumeg)
   mne.update(jumeg)
   return mne
   

def merge_dicts(mne=dict(),jumeg=dict()):
    """
    function to merge two dicts with one priorised
    
    Parameters
    ----------
    mne : dict with mne parameters
    jumeg : dict with jumeg parameters
    
    Returns
    -------
    mne : merged dict
    """
    no_merge=compare_versions(mne,jumeg)
    for key in jumeg.keys():
       if not key in mne.keys():
          mne[key]=jumeg.get(key)
       elif type(jumeg.get(key))==list:
          for elem in jumeg.get(key):
             if type(elem)==dict:
                for key2 in elem.keys():
                   index=find_dict_in_list(mne.get(key), key2)
                   mne.get(key)[index]=merge_dicts(mne.get(key)[index],elem)
             else:
                if not elem in no_merge.values() and not elem in mne.get(key) and not elem.startswith("mne"):
                   mne.get(key).append(elem)
    return mne
 
def merge_dicts2(mne=dict(),jumeg=dict()):
   merge=compare_versions(mne,jumeg)
   for key in mne.keys():
      akt=mne.get(key)
      logger.info(type(akt))
      if type(akt)==dict:
         akt.update(jumeg.get(key))
      elif type(akt)==list:
         akt.extend(x for x in jumeg.get(key) if x not in akt)
   return mne

def merge_dicts3(mne=dict(),jumeg=dict()):
    for key in mne.keys():
        if not key in jumeg.keys():
            jumeg[key]=mne.get(key)
        elif type(mne.get(key))==list and type(jumeg.get(key))==list:
            jumeg[key]=merge_lists(mne.get(key),jumeg.get(key))
        elif type(mne.get(key))==dict and type(jumeg.get(key))==dict:
            jumeg[key]=merge_dicts3(mne.get(key),jumeg.get(key))
    pass

def merge_lists(mne=list(),jumeg=list()):
    pass
    
def find_dict_in_list(l,name):
   """
   function to find a dict in a list
   
   Parameters
   ----------
   l : list in which is searched
   name : name of the dict which is searched
   
   Returns
   -------
   index of the dict in the list if found
   otherwise None
   """
   for elem in l:
      if type(elem)==dict:
         if list(elem.keys())[0]==name:
            return l.index(elem)
   return None

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
   saves the new environment file with the filename opt.name + .yml if save is true or overwrites an existing file
   
   Parameters
   ----------
   opt : list of given parameters
   env : dict to save
   """
   if bool(env):
      fname=opt.name + ".yml"
      with open(fname,"w") as f:
         yaml.dump(env,f)
         
def delete_env_file(opt):
   """
   function to delete the generated env file if save is false
   
   Parameters
   ----------
   opt : list of given parameters
   """
   if not opt.save:
      fname=opt.name+".yml"
      subprocess.run(["rm",fname])

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
    
    Parameters
    ----------
    opt : list of given parameters
    """
    if opt.install:
        fname=opt.name + ".yml"
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
   data = merge_dicts(mne,jumeg)
   data = sort_data(opt,data)
   show(opt,data)
   save_env(opt,data)
   install(opt)
   delete_env_file(opt)
   
def run_test():
   opt=get_args(sys.argv)
   mne=load_mne(opt)
   jumeg=load_jumeg(opt)
   logger.info(check_version(mne))
   logger.info(check_version(jumeg))
   logger.info(compare_versions(mne,jumeg))
   #logger.info(merge_dicts(mne,jumeg))
   
def check_envs(name):
   """
   function to check if there is an environment with a specified name
   
   Parameters
   ----------
   name : name of the environment which is searched
   
   Returns
   -------
   True if environment is found
   else False
   """
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
   #run()
   run_test()


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

