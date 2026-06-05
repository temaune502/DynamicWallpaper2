import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from effects import BaseEffect

class NeuronNetwork1Effect(BaseEffect):
    EFFECT_NAME = "neuron_network1"

    def __init__(self):
        super().__init__()
        self.neurons = []
        self.pulses = [] # {start_idx, end_idx, progress, speed}
        self.connections = [] # tuples of (idx1, idx2, distance)
        
        # Create Neurons
        self.num_neurons = 80
        for _ in range(self.num_neurons):
            self.neurons.append({
                'x': random.uniform(50, 1870),
                'y': random.uniform(50, 1030),
                'vx': random.uniform(-0.2, 0.2), # Slow drift
                'vy': random.uniform(-0.2, 0.2),
                'activation': 0.0, # 0 to 1, decays
                'refractory': 0, # Frames until can fire again
                'outgoing': []
            })
            
        self._build_connections()

    def _build_connections(self):
        self.connections = []
        # Pre-init outgoing is done in initialization loop above or can be re-cleared
        for n in self.neurons:
            n['outgoing'] = []
            
        # Simple N^2 connect close ones
        for i in range(self.num_neurons):
            n1 = self.neurons[i]
            
            for j in range(i + 1, self.num_neurons):
                n2 = self.neurons[j]
                dx = n1['x'] - n2['x']
                dy = n1['y'] - n2['y']
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < 200*200: # Connection range
                    # Add bidirectional connection
                    dist = math.sqrt(dist_sq)
                    self.connections.append((i, j, dist))
                    n1['outgoing'].append(j)
                    n2['outgoing'].append(i) # undirected graph

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(0, 5, 10)) # Dark biological background
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # 1. Update Neurons
        for i, n in enumerate(self.neurons):
            # Drift
            n['x'] += n['vx']
            n['y'] += n['vy']
            
            # Bounce
            if n['x'] < 0 or n['x'] > w: n['vx'] *= -1
            if n['y'] < 0 or n['y'] > h: n['vy'] *= -1
            
            # Decay activation
            n['activation'] *= 0.95
            if n['refractory'] > 0: n['refractory'] -= 1
            
            # Mouse Stimulus
            dx = mx - n['x']
            dy = my - n['y']
            if dx*dx + dy*dy < 150*150:
                 n['activation'] = min(1.0, n['activation'] + 0.1)
                 
            # Fire logic
            if n['activation'] > 0.8 and n['refractory'] == 0:
                self._fire_pulse(i)
                n['refractory'] = 30 # Cooldown
                n['activation'] = 0.5 # Reset partial
                
        # 2. Update Pulses
        # Filter out finished pulses
        active_pulses = []
        for pulse in self.pulses:
            pulse['progress'] += pulse['speed']
            if pulse['progress'] < 1.0:
                active_pulses.append(pulse)
            else:
                # Reached target! Stimulate target neuron
                target_idx = pulse['end']
                self.neurons[target_idx]['activation'] += 0.3
        self.pulses = active_pulses
        
        # 3. Draw Connections
        p.setBrush(Qt.NoBrush)
        base_color = QColor(0, 100, 255, 30) # Faint blue
        p.setPen(QPen(base_color, 1))
        
        for i, j, _ in self.connections:
            n1 = self.neurons[i]
            n2 = self.neurons[j]
            p.drawLine(QPointF(n1['x'], n1['y']), QPointF(n2['x'], n2['y']))
            
        # 4. Draw Pulses
        p.setPen(Qt.NoPen)
        for pulse in self.pulses:
            n1 = self.neurons[pulse['start']]
            n2 = self.neurons[pulse['end']]
            
            # Lerp
            t = pulse['progress']
            px = n1['x'] + (n2['x'] - n1['x']) * t
            py = n1['y'] + (n2['y'] - n1['y']) * t
            
            # Draw glowy blob
            p.setBrush(QColor(100, 200, 255, 200))
            p.drawEllipse(QPointF(px, py), 3, 3)
            
        # 5. Draw Neurons
        for n in self.neurons:
            # Color based on activation
            # Clamp alpha
            act_clamped = min(1.0, max(0.0, n['activation']))
            
            r = 4 + act_clamped * 4
            
            if act_clamped > 0.1:
                # Active glow
                r_val = min(255, 100 + int(155*act_clamped))
                g_val = min(255, 100 + int(155*act_clamped))
                b_val = 255
                alpha_val = min(255, 150 + int(100*act_clamped))
                
                color = QColor(r_val, g_val, b_val)
                color.setAlpha(alpha_val)
                p.setBrush(color)
            else:
                p.setBrush(QColor(50, 50, 150, 100))
                
            p.drawEllipse(QPointF(n['x'], n['y']), r, r)

    def _fire_pulse(self, idx):
        # Fire to all connected neighbors
        n = self.neurons[idx]
        if 'outgoing' in n:
            for target_idx in n['outgoing']:
                n2 = self.neurons[target_idx]
                dist = math.sqrt((n['x']-n2['x'])**2 + (n['y']-n2['y'])**2)
                if dist > 0:
                    speed = 5.0 / dist # 5 pixels per frame effectively
                    self.pulses.append({
                        'start': idx,
                        'end': target_idx,
                        'progress': 0.0,
                        'speed': speed
                    })
