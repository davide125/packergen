import hashlib
import os.path
import urllib.request

from packergen.preparer import Preparer, PreparerException
from packergen.utils import path_to_url, path_to_absolute

class BadChecksumException(PreparerException):
  def __init__(self, path, expected, found):
    message = "Wrong checksum for %s: expected %s, found %s." % (path, expected, found)
    super().__init__(message)

class File(Preparer):
  def __init__(self, source, destination=None, checksum=None):
    from packergen.packergen import PackerGen
    
    self.source = path_to_url(source, PackerGen.config['basedir'])
    if destination:
      self.destination = path_to_absolute(destination, PackerGen.config['workdir'])
    else:
      s = path_to_absolute(source, PackerGen.config['basedir'])
      self.destination = os.path.join(PackerGen.config['workdir'], os.path.basename(s))
    self.checksum = checksum
  
  def prepare(self):
    if os.path.exists(self.destination):
      if self.checksum:
        with open(self.destination, 'rb') as f:
          digest = hashlib.sha256(f.read()).hexdigest()
          if self.checksum == digest:
            return
      else:
        pass
          
    urllib.request.urlretrieve(self.source, filename=self.destination)
    if self.checksum:
      with open(self.destination, 'rb') as f:
        digest = hashlib.sha256(f.read()).hexdigest()
        if self.checksum != digest:
          raise BadChecksumException(self.destination, self.checksum, digest)
