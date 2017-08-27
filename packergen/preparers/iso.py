from packergen.preparers.file import File

class ISO(File):  
  builders = [
    'hyperv-iso',
    'parallels-iso',
    'qemu',
    'virtualbox-iso',
    'vmware-iso',
  ]

  def __init__(self, source, destination=None, checksum=None):
    super().__init__(source, destination, checksum)
    
  def prepare(self):
    from packergen.packergen import PackerGen

    super().prepare()
    for builder in PackerGen.config['packer']['builders']:
      if builder['type'] not in ISO.builders:
        continue
      
      builder['iso_url'] = self.destination
      if self.checksum:
        builder['iso_checksum'] = self.checksum
        builder['iso_checksum_type'] = 'sha256'
