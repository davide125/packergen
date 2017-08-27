import collections
import os.path
import pathlib

def path_to_absolute(path, base):
  if path[0] == '/':
    return path
  else:
    return os.path.join(base, path)

def path_to_url(path, base):
  if '://' in path:
    return path
  else:
    return pathlib.Path(path_to_absolute(path, base)).as_url()
    
def make_autovivified_dict():
  return collections.defaultdict(lambda : collections.defaultdict(dict))
  
def merge_dict(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            merge_dict(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
