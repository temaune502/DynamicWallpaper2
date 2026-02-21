import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor, QRadialGradient

from effects import BaseEffect

class NeuronNetworkEffect(BaseEffect):
    EFFECT_NAME = "neuron_network2"

    def __init__(self):
        super().__init__()
        self.neurons = []
        self.pulses = [] # {start_idx, end_idx, progress, speed}
        self.connections = [] # tuples of (idx1, idx2, distance, weight)
        
        # Create Neurons
        self.num_neurons = 80
        for _ in range(self.num_neurons):
            self.neurons.append({
                'x': random.uniform(50, 1870),
                'y': random.uniform(50, 1030),
                'vx': 0, 
                'vy': 0,
                'activation': 0.0, # 0 to 1, decays
                'refractory': 0 # Frames until can fire again
            })
            
        self._build_connections()

    def _build_connections(self):
        self.connections = []
        # Pre-init outgoing for all
        for n in self.neurons:
            n['outgoing'] = []
            
        # N^2 connect close ones
        for i in range(self.num_neurons):
            n1 = self.neurons[i]
            
            for j in range(i + 1, self.num_neurons):
                n2 = self.neurons[j]
                dx = n1['x'] - n2['x']
                dy = n1['y'] - n2['y']
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < 250*250: # Increased range
                    dist = math.sqrt(dist_sq)
                    # (idx1, idx2, length, weight)
                    # Use a mutable list or dict for connection to update weight?
                    # Let's use a dict for the connection object
                    conn = {'n1': i, 'n2': j, 'len': dist, 'weight': 0.5}
                    self.connections.append(conn)
                    n1['outgoing'].append({'target': j, 'conn': conn})
                    n2['outgoing'].append({'target': i, 'conn': conn})

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(0, 2, 8)) # Darker background
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # 1. Physics (Force Directed) & Update
        for i, n in enumerate(self.neurons):
            fx, fy = 0, 0
            
            # Repulsion (from all other nodes)
            # Optimization: 80 nodes is small enough for N^2
            for j, n2 in enumerate(self.neurons):
                if i == j: continue
                dx = n['x'] - n2['x']
                dy = n['y'] - n2['y']
                dist_sq = dx*dx + dy*dy
                if dist_sq < 10000 and dist_sq > 1: # 100px repulsion
                    dist = math.sqrt(dist_sq)
                    force = 100 / dist_sq # Inverse square?
                    fx += (dx / dist) * force
                    fy += (dy / dist) * force
            
            # Center attraction (gravity) to keep them on screen
            dx = w/2 - n['x']
            dy = h/2 - n['y']
            fx += dx * 0.0001
            fy += dy * 0.0001
            
            # Apply Force
            n['vx'] = (n['vx'] + fx) * 0.9 # Damping
            n['vy'] = (n['vy'] + fy) * 0.9
            
            # Move
            n['x'] += n['vx']
            n['y'] += n['vy']
            
            # Hard Clamp
            n['x'] = max(20, min(w-20, n['x']))
            n['y'] = max(20, min(h-20, n['y']))
            
            # Decay activation
            n['activation'] *= 0.92
            if n['refractory'] > 0: n['refractory'] -= 1
            
            # Spontaneous Firing
            if random.random() < 0.005 and n['refractory'] == 0:
                n['activation'] = 1.0
            
            # Mouse Stimulus
            dx = mx - n['x']
            dy = my - n['y']
            if dx*dx + dy*dy < 200*200:
                 n['activation'] = min(1.0, n['activation'] + 0.15)
                 # Mouse also attracts/repels?
                 # Let's make mouse attract lightly to "guide" thought
                 n['vx'] += dx * 0.005
                 n['vy'] += dy * 0.005

            # Fire logic
            if n['activation'] > 0.8 and n['refractory'] == 0:
                self._fire_pulse(i)
                n['refractory'] = 20
                n['activation'] = 0.4 

        # Spring forces (Attraction along connections)
        for c in self.connections:
            n1 = self.neurons[c['n1']]
            n2 = self.neurons[c['n2']]
            dx = n2['x'] - n1['x']
            dy = n2['y'] - n1['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Spring target length = 100?
            target_len = 100
            if dist > 0:
                force = (dist - target_len) * 0.005
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                
                n1['vx'] += fx
                n1['vy'] += fy
                n2['vx'] -= fx # Newton's 3rd law
                n2['vy'] -= fy
                
            # Decay connection weight
            c['weight'] = max(0.5, c['weight'] * 0.999) # Slow decay to baseline 0.5
        
        # 2. Update Pulses
        active_pulses = []
        for pulse in self.pulses:
            pulse['progress'] += pulse['speed']
            if pulse['progress'] < 1.0:
                active_pulses.append(pulse)
            else:
                # Reached target
                target_idx = pulse['end']
                self.neurons[target_idx]['activation'] += 0.4
                
                # Strengthen Connection (Hebbian Learning)
                pulse['conn']['weight'] = min(5.0, pulse['conn']['weight'] + 0.5)
                
        self.pulses = active_pulses
        
        # 3. Draw Connections
        for c in self.connections:
            n1 = self.neurons[c['n1']]
            n2 = self.neurons[c['n2']]
            
            # Width based on weight
            width = c['weight']
            alpha = min(255, 30 + int(c['weight'] * 40))
            
            color = QColor(0, 100, 255, alpha)
            p.setPen(QPen(color, width))
            p.drawLine(QPointF(n1['x'], n1['y']), QPointF(n2['x'], n2['y']))
            
        # 4. Draw Pulses
        p.setPen(Qt.NoPen)
        for pulse in self.pulses:
            n1 = self.neurons[pulse['start']]
            n2 = self.neurons[pulse['end']]
            
            t = pulse['progress']
            px = n1['x'] + (n2['x'] - n1['x']) * t
            py = n1['y'] + (n2['y'] - n1['y']) * t
            
            p.setBrush(QColor(200, 230, 255, 200))
            p.drawEllipse(QPointF(px, py), 4, 4)
            
        # 5. Draw Neurons
        for n in self.neurons:
            r = 5 + n['activation'] * 5
            
            val = int(min(255, n['activation'] * 255))
            color = QColor(val, val, 255)
            color.setAlpha(min(255, 100 + val))
            
            p.setBrush(color)
            p.drawEllipse(QPointF(n['x'], n['y']), r, r)

    def _fire_pulse(self, idx):
        n = self.neurons[idx]
        if 'outgoing' in n:
            for out in n['outgoing']:
                target_idx = out['target']
                conn = out['conn']
                n2 = self.neurons[target_idx]
                dist = math.sqrt((n['x']-n2['x'])**2 + (n['y']-n2['y'])**2)
                
                if dist > 0:
                    speed = 8.0 / dist
                    self.pulses.append({
                        'start': idx,
                        'end': target_idx,
                        'progress': 0.0,
                        'speed': speed,
                        'conn': conn # Pass conn ref to update weight
                    })
