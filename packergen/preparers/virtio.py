import os
import shutil

from packergen.preparer import Preparer, PreparerException
from packergen.preparers.windows_answer_file import WindowsAnswerFile
from packergen.utils import path_to_absolute

class InvalidArchException(PreparerException):
  def __init__(self, arch):
    message = "%s is not a valid architecture" % arch
    super().__init__(message)

class InvalidDriverException(PreparerException):
  def __init__(self, driver):
    message = "%s is not a valid driver" % driver
    super().__init__(message)

class InvalidOSException(PreparerException):
  def __init__(self, os):
    message = "%s is not a valid OS" % os
    super().__init__(message)

class VirtioWin(Preparer):  
  def __init__(self, path='/usr/share/virtio-win'):
    from packergen.packergen import PackerGen

    self.path = path_to_absolute(path, PackerGen.config['basedir'])

DEFAULT_PATH = '/usr/share/virtio-win'

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

  def __init__(self, os, arch='amd64', path=DEFAULT_PATH):
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
    
    for p in PackerGen.config['preparers']:
      if isinstance(p, WindowsAnswerFile):
        p.params['driver_paths'].append('A:\\')

class VirtioWinFloppy(VirtioWin):
  known_arch = [
    'amd64',
    'x86',
  ]

  def __init__(self, arch='amd64', path=DEFAULT_PATH):
    super().__init__(path)

    if arch in self.known_arch:
      self.arch = arch
    else:
      raise InvalidArchException(arch)
  
  def prepare(self):
    from packergen.packergen import PackerGen
    
    vfd = "virtio-win_%s.vfd" % self.arch
    dst = os.path.join(PackerGen.config['workdir'], vfd)
    shutil.copy(os.path.join(self.path, vfd), dst)
    
    for builder in PackerGen.config['packer']['builders']:
      if builder['type'] != 'qemu':
        continue
      builder['qemuargs'].append(['-fdb', dst])
    
    for p in PackerGen.config['preparers']:
      if isinstance(p, WindowsAnswerFile):
        p.params['driver_paths'].append('B:\\')

class VirtioWinISO(VirtioWin):
  known_os = [
    '2k12',
    '2k12R2',
    '2k16',
    '2k3',
    '2k8',
    '2k8R2',
    'w10',
    'w8',
    'w8.1',
    'xp',
  ]
  
  known_arch = [
    'amd64',
    'x86',
  ]
  
  known_drivers = [
    'Balloon',
    'NetKVM',
    'pvpanic',
    'qemufwcfg',
    'qemupciserial',
    'qxl',
    'smbus',
    'vioinput',
    'viorng',
    'vioscsi',
    'vioserial',
    'viostor',
  ]
  
  def __init__(self, os, arch='amd64', drivers=known_drivers, path=DEFAULT_PATH):
    super().__init__(path)

    if os in self.known_os:
      self.os = os
    else:
      raise InvalidOSException(os)
      
    if arch in self.known_arch:
      self.arch = arch
    else:
      raise InvalidArchException(arch)

    for driver in drivers:
      if driver not in self.known_drivers:
        raise InvalidDriverException(driver)
    self.drivers = drivers

  def prepare(self):
    from packergen.packergen import PackerGen
    
    iso = 'virtio-win.iso'
    dst = os.path.join(PackerGen.config['workdir'], iso)
    shutil.copy(os.path.join(self.path, iso), dst)

    for builder in PackerGen.config['packer']['builders']:
      if builder['type'] != 'qemu':
        continue

      # This is nasty hack. Packer internally uses -drive to pass the main disk
      # image, but if -drive is added to qemuargs that takes precedence. So we
      # add an extra -drive for the disk image mimicking what packer would
      # have done. Which means reading half a dozen attributes :(
      if 'output_directory' in PackerGen.config['packer']:
        output_dir = PackerGen.config['packer']['output_directory']
      else:
        output_dir = 'output-qemu'
      if 'vm_name' in PackerGen.config['packer']:
        output_file = PackerGen.config['packer']['vm_name']
      elif 'name' in PackerGen.config['packer']:
        output_file = "packer-%s" % PackerGen.config['packer']['name']
      else:
        output_file = 'packer-qemu'
      if 'disk_interface' in PackerGen.config['packer']:
        disk_interface = PackerGen.config['packer']['disk_interface']
      else:
        disk_interface = 'virtio'
      if 'disk_cache' in PackerGen.config['packer']:
        disk_cache = PackerGen.config['packer']['disk_cache']
      else:
        disk_cache = 'writeback'
      if 'disk_discard' in PackerGen.config['packer']:
        disk_discard = PackerGen.config['packer']['disk_discard']
      else:
        disk_discard = 'ignore'
      if 'format' in PackerGen.config['packer']:
        disk_format = PackerGen.config['packer']['format']
      else:
        disk_format = 'qcow2'
      
      builder['qemuargs'].append(["-drive", "file=%s,if=%s,cache=%s,discard=%s,format=%s" % (os.path.join(output_dir, output_file), disk_interface, disk_cache, disk_discard, disk_format)])
      # index=3 is to ensure this shows up after the OS install ISO
      builder['qemuargs'].append(['-drive', "file=%s,index=3,media=cdrom" % dst])      
    
    for p in PackerGen.config['preparers']:
      if isinstance(p, WindowsAnswerFile):
        for driver in self.drivers:
          p.params['driver_paths'].append('E:\\%s\\%s\\%s' % (driver, self.os, self.arch))
          
        # schedule install of the qemu guest tools
        qemu_arch = self.arch
        if qemu_arch == 'amd64':
          # of course this is named using yet another convention...
          qemu_arch =  'x64'
        p.params['first_logon_commands'].insert(0, 'msiexec /package e:\guest-agent\qemu-ga-%s.msi /passive' % qemu_arch)
