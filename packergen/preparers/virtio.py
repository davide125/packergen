import os
import shutil

from packergen.preparer import Preparer, PreparerException
from packergen.utils import path_to_absolute

class InvalidArchException(PreparerException):
  def __init__(self, arch):
    message = "%s is not a valid architecture" % arch
    super().__init__(message)

class InvalidOSException(PreparerException):
  def __init__(self, os):
    message = "%s is not a valid OS" % os
    super().__init__(message)

class VirtioWin(Preparer):  
  def __init__(self, path='/usr/share/virtio-win'):
    from packergen.packergen import PackerGen

    self.path = path_to_absolute(path, PackerGen.config['basedir'])

class VirtioWinDrivers(VirtioWin):
  known_os = [
    'Win7',
    'Win8',
    'Win8.1',
    'Win10',
    'Win2003',
    'Win2008',
    'Win2008R2',
    'Win2012',
    'Win2012R2',
    'Win2016',
  ]
  
  known_arch = [
    'amd64',
    'i386',
  ]

  def __init__(self, os, arch='amd64', path='/usr/share/virtio-win'):
    super().__init__(path)

    if os in self.known_os:
      self.os = os
    else:
      raise InvalidOSException(os)
      
    if arch in self.known_arch:
      self.arch = arch
    else:
      raise InvalidArchException(arch)

  def prepare(self):
    from packergen.packergen import PackerGen
    
    dst = os.path.join(PackerGen.config['workdir'], 'virtio-win-floppy')
    if os.path.exists(dst):
      shutil.rmtree(dst)
    
    os.mkdir(dst)
    src_path = os.path.join(self.path, 'drivers', self.arch, self.os)
    drivers = []
    for f in os.listdir(src_path):
      drivers.append(f)
      shutil.copy(os.path.join(src_path, f), dst)
    
    for builder in PackerGen.config['packer']['builders']:
      if 'floppy_files' not in builder:
        builder['floppy_files'] = [] 
      for driver in drivers:
        builder['floppy_files'].append(os.path.join(dst, driver))
    
    # TODO: add a:\ to driverpaths for windowsanswerfile
