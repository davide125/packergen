import jinja2
import os.path

from packergen.preparer import Preparer, PreparerException
from packergen.utils import path_to_absolute

class Template(Preparer):
  def __init__(self, source, destination=None, params={}):
    from packergen.packergen import PackerGen
    
    self.source = path_to_absolute(source, PackerGen.config['basedir'])
    if destination:
      self.destination = path_to_absolute(destination, PackerGen.config['workdir'])
    else:
      self.destination = os.path.join(PackerGen.config['workdir'], os.path.basename(self.source))
    self.params = params
  
  def prepare(self):
    with open(self.source, 'r') as s:
      t = jinja2.Template(s.read(), lstrip_blocks=True, trim_blocks=True)
      out = t.render(self.params)
      with open(self.destination, 'w') as d:
        d.write(out)
