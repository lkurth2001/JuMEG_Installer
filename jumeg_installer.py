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

def load_jumeg(fjumeg,cuda):
   """
   function to load the jumeg environment file as a python dict
   
   Parameters
   ----------
   fjumeg : name of the jumeg file
   cuda : bool if cuda support is needed
   
   Returns
   -------
   dict_jumeg : dict filled with values from jumeg environment file
   """
   if fjumeg:
      fname = fjumeg
   elif cuda:
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
                       result[elem]=elem
    return result
 
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
    for key in mne.keys():
       if not key in jumeg.keys() and not type(mne.get(key))==dict:
          tmp.append(key)
    for key in tmp:
       mne.pop(key)
    return mne

def merge_dicts(mne=dict(),jumeg=dict()):
    """
    function to merge two dicts with one priorised
    
    Parameters
    ----------
    mne : dict with data from mne env file
    jumeg : preferred dict with data from jumeg env file
    
    Returns
    -------
    jumeg : updated jumeg dict
    """
    no_merge=compare_versions(mne,jumeg)
    for key in mne.keys():
        if not key in jumeg.keys():
            jumeg[key]=mne.get(key)
        elif type(mne.get(key))==list and type(jumeg.get(key))==list:
            jumeg[key]=merge_lists(mne.get(key),jumeg.get(key),no_merge)
        elif type(mne.get(key))==dict and type(jumeg.get(key))==dict:
            jumeg[key]=merge_dicts(mne.get(key),jumeg.get(key))
        elif type(jumeg.get(key))==list:
           jumeg.get(key).append(mne.get(key))
    return jumeg

def merge_lists(mne=list(),jumeg=list(),no_merge=dict()):
    """
    function to merge two lists with one preferred
    
    Parameters
    ----------
    mne : list with the mne part
    jumeg : list with the jumeg part
    no_merge : dict with keys and values which should not be merged
    
    Returns
    -------
    jumeg : merged list
    """
    for elem in mne:
       if type(elem)==dict:
          for item in jumeg:
             if type(item)==dict:
                merge_dicts(elem,item)
       elif not elem in no_merge.values() and not elem in no_merge.keys() and not elem in jumeg:
          jumeg.append(elem)
    return jumeg
    
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

def load_mne(fmne):
   """
   function to load the mne environment file as a python dict
   
   Parameters
   ----------
   fmne : name of mne file
   
   Returns
   -------
   dict_mne : dict filled with values from mne environment file
   """
   if fmne:
      fname = fmne
   else:
      fname=_load_env_file("mne")
   return _file_to_dict(fname)

def save_env(name,env=dict()):
   """
   saves the new environment file with the filename opt.name + .yml if save is true or overwrites an existing file
   
   Parameters
   ----------
   name : name of the generated env file
   env : dict to save
   """
   if bool(env):
      fname=name + ".yml"
      with open(fname,"w") as f:
         yaml.dump(env,f)

def delete_env_file(save,name):
   """
   function to delete the generated env file if save is false
   
   Parameters
   ----------
   save : if save is true the file is saved else it is deleted
   """
   if not save:
      fname=name+".yml"
      subprocess.run(["rm",fname])

def show(bShow,env):
   """
   shows the new generated environment file if show is true
   
   Parameters
   ----------
   bShow : if true the file is shown in the shell
   env : dict with values of new environment file
   """
   if bShow and env:
      logger.info(dict2str(env))
   elif bShow:
      logger.error("No environment file found")
      
def sort_data(bSorted,env):
   """
   sorts env dict and returns the sorted dict if sort=true
   
   Parameters
   ----------
   bSorted : if true the dict gets sorted
   env : dict with values of environment file
   
   Returns
   -------
   env : sorted dict 
   """
   if bSorted and env:
      result=dict()
      for key in sorted(env):
         result[key]=env.get(key)
      return result
   else:
       return env

def install(bInstall,name):
    """
    function to install the new conda environment
    
    Parameters
    ----------
    opt : list of given parameters
    """
    if bInstall:
        fname=name + ".yml"
        if check_envs(name):
            subprocess.run(["conda","deactivate"],stdout=DEVNULL)
            subprocess.run(["conda","env","update","-n",name,"--file",fname])
            subprocess.run(["conda","activate",name],stdout=DEVNULL)
        else:
            subprocess.run(["conda","env","create","-f",fname])
            subprocess.run(["conda","activate",name],stdout=DEVNULL)

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
 
def structure(data=dict):
   """
   function to bring the data in the right order for creating an environment
   
   Parameters
   ----------
   data : dict with the merged datas
   
   Returns
   -------
   tmp : sorted dict
   """
   akt = data.get("dependencies")
   counter=0
   while type(akt[counter])!=dict:
       counter=counter+1
   tmp=akt[len(akt)-1]
   akt[len(akt)-1]=akt[counter]
   akt[counter]=tmp
   data["dependencies"]=akt
   return data
   
def run():
   check_conda()
   opt = get_args(sys.argv)
   mne = load_mne(opt.fmne)
   jumeg = load_jumeg(opt.fjumeg,opt.cuda)
   jumeg["name"] = opt.name
   data = merge_dicts(mne,jumeg)
   data = sort_data(opt.sorted,data)
   data = structure(data)
   show(opt.show,data)
   save_env(opt.name,data)
   install(opt.install,opt.name)
   delete_env_file(opt.save,opt.name)
   
def run_test():
   opt=get_args(sys.argv)
   mne=load_mne(opt.fmne)
   jumeg=load_jumeg(opt.fjumeg,opt.cuda)
   #logger.info(check_version(mne))
   #logger.info(check_version(jumeg))
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
   
if __name__=="__main__":
   run()
   #run_test()


   # ToDo
   #-> check dict key for pip 
   #-> save merged dict in new file with env-name => opt.name +.yml
