import os
import json
import shutil
from src.core.resources import get_resource_path, set_preset_root

class PresetManager:
    def __init__(self):
        self.presets_dir = get_resource_path("presets")
        
    def list_presets(self):
        items = []
        if not os.path.exists(self.presets_dir):
            return items
            
        for f in os.listdir(self.presets_dir):
            full_path = os.path.join(self.presets_dir, f)
            if f.endswith(".json"):
                items.append({"name": f[:-5], "type": "json", "path": full_path})
            elif os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "preset.json")):
                items.append({"name": f, "type": "bundle", "path": full_path})
        return sorted(items, key=lambda x: x["name"])

    def load_preset(self, name):
        # Find path
        target = None
        is_bundle = False
        
        # Check standard paths
        json_path = os.path.join(self.presets_dir, name + ".json")
        bundle_path = os.path.join(self.presets_dir, name)
        
        if os.path.exists(json_path):
            target = json_path
        elif os.path.isdir(bundle_path) and os.path.exists(os.path.join(bundle_path, "preset.json")):
            target = bundle_path
            is_bundle = True
            
        if not target: return None

        config_file = os.path.join(target, "preset.json") if is_bundle else target
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data, target, is_bundle
        except Exception as e:
            print(f"Error loading {name}: {e}")
            return None, None, False

    def save_preset(self, name, config, is_bundle=False):
        if not name: return False
        
        if is_bundle:
            bundle_dir = os.path.join(self.presets_dir, name)
            if not os.path.exists(bundle_dir):
                os.makedirs(bundle_dir)
                os.makedirs(os.path.join(bundle_dir, "effects"), exist_ok=True)
                os.makedirs(os.path.join(bundle_dir, "widgets"), exist_ok=True)
                os.makedirs(os.path.join(bundle_dir, "resources"), exist_ok=True)
            target = os.path.join(bundle_dir, "preset.json")
        else:
            target = os.path.join(self.presets_dir, name + ".json")
            
        try:
            with open(target, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving {name}: {e}")
            return False
