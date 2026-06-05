import sys
import os

_preset_root = None

def set_preset_root(path):
    global _preset_root
    _preset_root = path

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

def resolve_path(path):
    """ Resolve path relative to preset bundle if active, otherwise default resource path """
    if os.path.isabs(path):
        return path
        
    if _preset_root:
        bundle_path = os.path.join(_preset_root, path)
        if os.path.exists(bundle_path):
            return bundle_path
            
    return get_resource_path(path)
