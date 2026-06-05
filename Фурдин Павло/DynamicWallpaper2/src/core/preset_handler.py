import os
import json
from PySide6.QtCore import QTimer
from src.core.resources import get_resource_path, set_preset_root

def load_preset(app, preset_name):
    # Check if full path provided or just name
    if os.path.exists(preset_name):
        target_path = preset_name
    else:
        target_path = get_resource_path(os.path.join('presets', preset_name))
        
    # Handle Bundle (Directory)
    if os.path.isdir(target_path):
        config_path = os.path.join(target_path, 'preset.json')
        if not os.path.exists(config_path):
             # Try adding .json to dir name if user missed it? No, strict.
             print(f"Bundle missing preset.json: {target_path}")
             return
        set_preset_root(target_path)
        
        # Load Bundle Plugins
        if hasattr(app, 'effect_registry'):
            app.effect_registry.load_bundle_effects(target_path)
        if hasattr(app, 'widget_registry'):
            app.widget_registry.load_bundle_widgets(target_path)
            
    else:
        # Handle simple JSON file
        if not target_path.endswith('.json'):
             target_path += '.json'
        config_path = target_path
        set_preset_root(None) # Reset for single files

    if not os.path.exists(config_path):
        print(f"Preset not found: {config_path}")
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            new_config = json.load(f)
        
        print(f"Loading preset: {preset_name}")
        
        # 1. Update Effect
        effect_name = new_config.get("effect")
        effect_config = new_config.get("effect_config", {})
        
        if effect_name:
            app.next_effect = app.effect_registry.get_effect(effect_name) or app.effect_registry.get_effect("none")
            
            if effect_config:
                app.next_effect.configure(effect_config)

            app.is_transitioning = True
            app.transition_alpha = 0.0
            
            show_bg = new_config.get("show_background", True)
            if app.next_effect:
                app.next_effect.set_show_background(show_bg)

        # 2. Update FPS
        app.fps = new_config.get("fps", 22)
        app.set_target_fps(app.fps)
        print(f"Preset loaded with FPS: {app.fps}")

        # 3. Update Background
        bg_conf = new_config.get("background")
        if bg_conf:
            app.set_background_source(bg_conf)

        # 4. Update Widgets
        widget_configs = new_config.get("widgets", [])
        for w in app.active_widgets:
            if hasattr(w, 'cleanup'): w.cleanup()
        app.active_widgets = []
        for i, w_conf in enumerate(widget_configs):
            w_type = w_conf.get("type")
            widget = app.widget_registry.create_widget(w_type, w_conf)
            if widget:
                if not hasattr(widget, 'id') or not widget.id:
                    widget.id = w_conf.get('id', f"widget_{i}")
                app.active_widgets.append(widget)
        
        # 5. Update Playlist
        app.playlist = new_config.get("effects_playlist", [])
        app.playlist_interval = new_config.get("playlist_interval", 30000)
        app.current_playlist_idx = 0 
        
        if not hasattr(app, 'playlist_timer'):
            app.playlist_timer = QTimer(app)
            app.playlist_timer.timeout.connect(app.next_playlist_effect)
        
        app.playlist_timer.setInterval(app.playlist_interval)
        if app.playlist:
            app.playlist_timer.start()
        else:
            app.playlist_timer.stop()

        # 6. Update overall config
        app.config.update(new_config)
        
    except Exception as e:
        print(f"Error loading preset {preset_name}: {e}")
