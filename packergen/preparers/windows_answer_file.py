import os.path
from lxml import etree

from packergen.preparers.template import Template
from packergen.utils import merge_dict

class WindowsAnswerFile(Template):
  default_params = {
    'arch': 'amd64',
    'autologon': 'Administrator',
    'driver_paths': [],
    'first_logon_commands': [],
    'image_index': 1,
    'language': 'en-US',
    'partitions': [
      {
        # Windows RE Tools partition
        'label': 'WINRE',
        'type_id': 'de94bba4-06d1-4d40-a16a-bfd50179d6ac',
        'format': 'NTFS',
        'size': 300,
      },
      {
        # System partition (ESP)
        'label': 'System',
        'type': 'EFI',
        'format': 'FAT32',
        'size': 100,
      },
      {
        # Microsoft reserved partition (MSR)
        'type': 'MSR',
        'size': 128,
      },
      {
        # Windows partition
        'label': 'Windows',
        'format': 'NTFS',
        'letter': 'C',
      },
    ],
    'users': {
      'Administrator': {
        'password': '',
      },
    }
  }

  def __init__(self, params={}):
    source = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unattend.xml')
    p = self.default_params
    merge_dict(p, params)
    if 'key' in p and 'install_key' not in p:
      p['install_key'] = p['key']
    if 'key' in p and 'activation_key' not in p:
      p['activation_key'] = p['key']
    super().__init__(source, 'Autounattend.xml', p)
    
  def prepare(self):
    from packergen.packergen import PackerGen
    super().prepare()
    
    # validate xml
    parser = etree.XMLParser(dtd_validation=True)
    with open(self.destination, 'r') as f:
      etree.parse(f)
    
    for builder in PackerGen.config['packer']['builders']:
      if 'floppy_files' in builder:
        builder['floppy_files'].append(self.destination)
      else:
        builder['floppy_files'] = [self.destination]
