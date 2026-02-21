import math
import random
import ctypes
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from effects import BaseEffect

# Ctypes for mouse polling
user32 = ctypes.windll.user32

def is_left_clicked():
    return user32.GetAsyncKeyState(0x01) & 0x8000 != 0

def is_right_clicked():
    return user32.GetAsyncKeyState(0x02) & 0x8000 != 0

class NeuronNetwork4Effect(BaseEffect):
    EFFECT_NAME = "neuron_network4"

    def __init__(self):
        super().__init__()
        self.neurons = []
        self.pulses = [] 
        # Connections are now stored PER NEURON to allow dynamic topology
        # n['outgoing'] = [ {'target_idx': int, 'weight': float, 'last_used': int} ]
        
        self.max_neurons = 120
        self.population_timer = 0
        
        self.color_excitatory = (255, 220, 100)
        self.color_inhibitory = (100, 220, 255)

        # Initial population
        self._init_network()

    def _init_network(self):
        self.neurons = []
        self.pulses = []
        self._init_population()

    @classmethod
    def get_schema(cls):
        return {
            "max_neurons": {
                "type": "int",
                "min": 10,
                "max": 300,
                "default": 80,
                "label": "Max Neurons"
            },
            "color_excitatory": {
                "type": "color",
                "default": (0, 255, 255),
                "label": "Excitatory Color"
            },
            "color_inhibitory": {
                "type": "color",
                "default": (255, 0, 255),
                "label": "Inhibitory Color"
            }
        }

    def configure(self, config: dict):
        if 'max_neurons' in config:
            self.max_neurons = int(config['max_neurons'])
            
        if 'color_excitatory' in config:
            # Expects list [r, g, b]
            self.color_excitatory = tuple(config['color_excitatory'])
            
        if 'color_inhibitory' in config:
            self.color_inhibitory = tuple(config['color_inhibitory'])

    def _init_population(self):
        for _ in range(60):
            self._spawn_neuron()

    def _spawn_neuron(self, x=None, y=None):
        if len(self.neurons) >= self.max_neurons:
            return

        if x is None: x = random.uniform(50, 1870)
        if y is None: y = random.uniform(50, 1030)
        
        n_type = 'EXCITATORY' if random.random() < 0.7 else 'INHIBITORY'
        
        self.neurons.append({
            'x': x,
            'y': y,
            'vx': random.uniform(-0.3, 0.3),
            'vy': random.uniform(-0.3, 0.3),
            'activation': 0.0,
            'threshold': random.uniform(0.7, 1.0),
            'refractory': 0,
            'type': n_type,
            'age': 0,
            'lifespan': random.randint(1000, 5000), # Frames of life
            'outgoing': [], # List of dicts
            'id': random.randint(0, 1000000) # Unique ID for stable connections? Index based is faster but breaks on removal.
            # We will use Index-based for speed, but handle removal carefully or just rebuild connections often.
            # Actually, robust system uses IDs. Let's stick to Index but do "Swap and Pop" removal? 
            # No, if we remove index 5, index 6 becomes 5. All connections pointing to >5 need update.
            # EASIER: Periodic connection rebuild or "soft death" (alpha=0 then reuse).
            # Let's use "Soft Death" -> Respawn in place or nearby to keep indices valid?
            # Or just FULL REBUILD of connections every 60 frames?
        })
        
        # Connect to neighbors immediately
        idx = len(self.neurons) - 1
        self._connect_neuron(idx)

    def _connect_neuron(self, idx):
        # Connect to k nearest
        n1 = self.neurons[idx]
        candidates = []
        for i, n2 in enumerate(self.neurons):
            if i == idx: continue
            dist_sq = (n1['x'] - n2['x'])**2 + (n1['y'] - n2['y'])**2
            if dist_sq < 250*250:
                candidates.append((i, dist_sq))
        
        # Sort by dist
        candidates.sort(key=lambda x: x[1])
        
        # Connect to closest 3-5
        for i, dist_sq in candidates[:random.randint(2, 5)]:
            weight = random.uniform(0.5, 1.0)
            n1['outgoing'].append({'target': i, 'weight': weight})
            # Bi-directional?
            if random.random() < 0.5:
                self.neurons[i]['outgoing'].append({'target': idx, 'weight': weight})

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(2, 2, 8))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        l_click = is_left_clicked()
        r_click = is_right_clicked()
        
        # --- 1. POPULATION CONTROL ---
        self.population_timer += 1
        
        # Birth (Slow trickle or Click)
        if self.population_timer % 60 == 0 and len(self.neurons) < self.max_neurons:
            if random.random() < 0.3: self._spawn_neuron()
            
        if l_click and self.population_timer % 5 == 0:
             # Click spawns neurons!
             self._spawn_neuron(mx + random.uniform(-20, 20), my + random.uniform(-20, 20))

        # Death & Pruning
        # We can't easily remove from list without breaking indices in 'outgoing'.
        # Solution: Mark as 'dead' and recycle slot.
        
        for i, n in enumerate(self.neurons):
            n['age'] += 1
            
            # Die if old
            if n['age'] > n['lifespan']:
                 self._recycle_neuron(i)
                 continue
                 
            # Die if clicked (Right Click = Destructive)
            if r_click:
                dx = mx - n['x']
                dy = my - n['y']
                if dx*dx + dy*dy < 100*100:
                    n['activation'] = -5.0 # Hyper-inhibit
                    n['lifespan'] = 1 # Kill next frame, but safe for division
            
            # --- 2. PHYSICS & LOGIC ---
            n['x'] += n['vx']
            n['y'] += n['vy']
            
            # Wall bounce
            if n['x'] < 0 or n['x'] > w: n['vx'] *= -1
            if n['y'] < 0 or n['y'] > h: n['vy'] *= -1
            
            # Decay
            n['activation'] *= 0.9
            if n['refractory'] > 0: n['refractory'] -= 1
            
            # Mouse Interaction (Field)
            dx = mx - n['x']
            dy = my - n['y']
            dist_sq = dx*dx + dy*dy
            if dist_sq < 200*200:
                # Left Click = Super Excite
                if l_click:
                    n['activation'] += 0.2
                # Hover = Mild Excite
                else:
                    n['activation'] += 0.02
                    
            # Fire?
            if n['activation'] > n['threshold'] and n['refractory'] == 0:
                self._fire(i)
                n['refractory'] = 45
                n['activation'] = -0.1
                
        # --- 3. PULSES ---
        active_pulses = []
        for pulse in self.pulses:
            pulse['progress'] += pulse['speed']
            if pulse['progress'] < 1.0:
                active_pulses.append(pulse)
            else:
                # Hit target
                t_idx = pulse['end']
                if t_idx < len(self.neurons):
                    target = self.neurons[t_idx]
                    if pixel_dist_sq(target, self.neurons[pulse['start']]) < 500*500: # Sanity check distance
                        
                        # Plasticity: Strengthen connection on successful hit
                        # Find connection in source
                        src = self.neurons[pulse['start']]
                        for conn in src['outgoing']:
                            if conn['target'] == t_idx:
                                conn['weight'] = min(2.0, conn['weight'] + 0.05)
                        
                        # Effect
                        if pulse['type'] == 'EXCITATORY':
                            target['activation'] += pulse['strength']
                        else:
                            target['activation'] -= pulse['strength'] * 2
        self.pulses = active_pulses
        
        # --- 4. DRAWING ---
        
        # Draw Connections
        p.setPen(Qt.NoPen)
        for i, n in enumerate(self.neurons):
            for conn in n['outgoing']:
                target_idx = conn['target']
                if target_idx >= len(self.neurons): continue
                n2 = self.neurons[target_idx]
                
                # Plasticity: Weak connections fade
                conn['weight'] *= 0.999 # Slow decay
                if conn['weight'] < 0.1: # Prune
                    n['outgoing'].remove(conn)
                    continue
                
                # Draw line
                # Alpha depends on weight + activation
                alpha = int(conn['weight'] * 50) + int(n['activation'] * 50)
                alpha = min(255, max(10, alpha))
                
                col = QColor(100, 150, 200)
                col.setAlpha(alpha)
                p.setPen(QPen(col, 1))
                p.drawLine(QPointF(n['x'], n['y']), QPointF(n2['x'], n2['y']))
                
        # Draw Pulses
        p.setPen(Qt.NoPen)
        for pulse in self.pulses:
            n1 = self.neurons[pulse['start']]
            if pulse['end'] >= len(self.neurons): continue
            n2 = self.neurons[pulse['end']]
            
            t = pulse['progress']
            px = n1['x'] + (n2['x'] - n1['x']) * t
            py = n1['y'] + (n2['y'] - n1['y']) * t
            
            col = QColor(255, 255, 100) if pulse['type'] == 'EXCITATORY' else QColor(0, 100, 255)
            col.setAlpha(200)
            p.setBrush(col)
            p.drawEllipse(QPointF(px, py), 3, 3)
            
        # Draw Neurons
        for n in self.neurons:
            # Color
            act = max(0, min(1.0, n['activation']))
            
            # Age effect: Old neurons dim?
            life_progress = n['age'] / float(n['lifespan'])
            
            if n['type'] == 'EXCITATORY':
                r, g, b = self.color_excitatory
            else:
                r, g, b = self.color_inhibitory
                
            # Flash white on fire
            if act > 0.8:
                r, g, b = 255, 255, 255
            
            alpha = 255
            if life_progress > 0.9: # Fade out dying
                alpha = int(255 * (1.0 - life_progress) * 10.0)
            if life_progress < 0.1: # Fade in born
                alpha = int(255 * (life_progress * 10.0))
                
            final_col = QColor(r, g, b)
            final_col.setAlpha(max(0, min(255, alpha)))
            
            p.setBrush(final_col)
            p.setPen(Qt.NoPen)
            size = 5 + act * 10
            p.drawEllipse(QPointF(n['x'], n['y']), size, size)

    def _recycle_neuron(self, idx):
        # Reset neuron properties to be "new"
        n = self.neurons[idx]
        n['x'] = random.uniform(50, 1870)
        n['y'] = random.uniform(50, 1030)
        n['age'] = 0
        n['lifespan'] = random.randint(1000, 5000)
        n['outgoing'] = [] # Clear connections
        n['activation'] = 0.0
        
        # New connections
        self._connect_neuron(idx)

    def _fire(self, idx):
        n = self.neurons[idx]
        for conn in n['outgoing']:
            target_idx = conn['target']
            if target_idx >= len(self.neurons): continue
            
            dist = 100 # Approx logic
            speed = 0.1 
            
            self.pulses.append({
                'start': idx,
                'end': target_idx,
                'progress': 0.0,
                'speed': speed,
                'type': n['type'],
                'strength': conn['weight'] * 0.5
            })

def pixel_dist_sq(n1, n2):
    return (n1['x'] - n2['x'])**2 + (n1['y'] - n2['y'])**2
