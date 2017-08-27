import getpass
import json
import logging
import os
import pkg_resources
from datetime import datetime

from packergen.preparers.file import File
from packergen.preparers.iso import ISO
from packergen.preparers.template import Template
from packergen.preparers.virtio import VirtioWinDrivers
from packergen.preparers.windows_answer_file import WindowsAnswerFile
from packergen.utils import make_autovivified_dict, merge_dict

class PackerGen(object):
  def __init__(self, config_path):
    try:
      version = pkg_resources.get_distribution('packergen').version
    except pkg_resources.DistributionNotFound:
      version = '-1'
    
    try:
      user = getpass.getuser()
    except Exception:
      user = 'unknown'
  
    defaults = {
      'basedir' : os.getcwd(),
      'workdir': os.path.join(os.getcwd(), 'work'),
      'packer': {
        '_packergen_version': version,
        '_packergen_build_time': str(datetime.now()),
        '_packergen_build_user': user,
      },
    }
    PackerGen.config = make_autovivified_dict()
    merge_dict(PackerGen.config, defaults)
    
    config = make_autovivified_dict()
    with open(config_path, 'r') as c:
      exec(c.read())
    merge_dict(PackerGen.config, config)
  
  def run_preparers(self):
    if not os.path.exists(PackerGen.config['workdir']):
      os.mkdir(PackerGen.config['workdir'])
    
    for p in PackerGen.config['preparers']:
      p.prepare()
  
  def build_packer_config(self):
    with open(os.path.join(PackerGen.config['workdir'], 'packer.json'), 'w') as f:
      json.dump(PackerGen.config['packer'], f, sort_keys=True, indent=2)
  
  def get_packer_config(self):
    return json.dumps(PackerGen.config['packer'], sort_keys=True, indent=2)
      
def main():
  import sys

  p = PackerGen(sys.argv[1])
  p.run_preparers()
  p.build_packer_config()
  
  print('All done! Run: ')
  print("$ cd %s" % PackerGen.config['workdir'])
  print("$ PACKER_LOG=1 packer build packer.json")
  print('to start your build.')
  
if __name__ == '__main__':
  main()
