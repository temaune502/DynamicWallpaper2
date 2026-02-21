import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor
from effects import BaseEffect
class NeuronNetworkEffect(BaseEffect):
    EFFECT_NAME = "neuron_network3"
    def __init__(self):
        super().__init__()
        self.neurons = []
        self.pulses = [] # {start_idx, end_idx, progress, speed, type}
        self.connections = [] # (idx1, idx2, distance, weight)
        
        # Create Neurons
        self.num_neurons = 100
        for _ in range(self.num_neurons):
            # 80% Excitatory, 20% Inhibitory
            n_type = 'EXCITATORY' if random.random() < 0.8 else 'INHIBITORY'
            
            self.neurons.append({
                'x': random.uniform(50, 1870),
                'y': random.uniform(50, 1030),
                'vx': random.uniform(-0.1, 0.1),
                'vy': random.uniform(-0.1, 0.1),
                'activation': 0.0,
                'refractory': 0,
                'type': n_type,
                'threshold': random.uniform(0.7, 0.9),
                'outgoing': [] 
            })
            
        self._build_connections()
    def _build_connections(self):
        self.connections = []
        # Pre-init outgoing done in __init__ implicitly by list creation, but let's clear if rebuilding
        for n in self.neurons:
            n['outgoing'] = []
            
        for i in range(self.num_neurons):
            n1 = self.neurons[i]
            for j in range(i + 1, self.num_neurons):
                n2 = self.neurons[j]
                dx = n1['x'] - n2['x']
                dy = n1['y'] - n2['y']
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < 180*180:
                    dist = math.sqrt(dist_sq)
                    # Weight: how strong is this connection?
                    weight = random.uniform(0.5, 1.0)
                    self.connections.append({'n1': i, 'n2': j, 'dist': dist, 'weight': weight})
                    n1['outgoing'].append({'target': j, 'weight': weight})
                    n2['outgoing'].append({'target': i, 'weight': weight})
    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(5, 5, 10))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # 1. Update Neurons
        for i, n in enumerate(self.neurons):
            # Drift
            n['x'] += n['vx']
            n['y'] += n['vy']
            # Bounds
            if n['x'] < 0 or n['x'] > w: n['vx'] *= -1
            if n['y'] < 0 or n['y'] > h: n['vy'] *= -1
            
            # Decay
            n['activation'] *= 0.92
            if n['refractory'] > 0: n['refractory'] -= 1
            
            # Spontaneous firing (Background noise)
            if random.random() < 0.005: 
                n['activation'] += 0.3
            
            # Mouse Stimulus (Excites all types)
            dx = mx - n['x']
            dy = my - n['y']
            if dx*dx + dy*dy < 150*150:
                 n['activation'] += 0.05
                 
            # Clamp activation
            n['activation'] = max(-0.5, min(2.0, n['activation'])) # Can go negative (hyperpolarized)
            
            # Fire?
            if n['activation'] > n['threshold'] and n['refractory'] == 0:
                self._fire_pulse(i)
                n['refractory'] = 40
                n['activation'] = -0.2 # Hyperpolarization after firing
        # 2. Update Pulses
        active_pulses = []
        for pulse in self.pulses:
            pulse['progress'] += pulse['speed']
            if pulse['progress'] < 1.0:
                active_pulses.append(pulse)
            else:
                # Deliver payload
                target = self.neurons[pulse['end']]
                strength = pulse['strength']
                
                if pulse['type'] == 'EXCITATORY':
                    target['activation'] += strength
                else:
                    target['activation'] -= strength * 2.0 # Inhibition is strong
                    
        self.pulses = active_pulses
        
        # 3. Draw Connections
        p.setPen(Qt.NoPen)
        for conn in self.connections:
            n1 = self.neurons[conn['n1']]
            n2 = self.neurons[conn['n2']]
            
            # Brightness depends on activation of both
            act = max(0, (n1['activation'] + n2['activation']) / 2)
            alpha = int(20 + act * 100)
            alpha = min(255, alpha)
            
            col = QColor(50, 100, 150)
            col.setAlpha(alpha)
            p.setPen(QPen(col, max(1, int(conn['weight'] * 2))))
            p.drawLine(QPointF(n1['x'], n1['y']), QPointF(n2['x'], n2['y']))
            
        # 4. Draw Pulses
        p.setPen(Qt.NoPen)
        for pulse in self.pulses:
            n1 = self.neurons[pulse['start']]
            n2 = self.neurons[pulse['end']]
            
            t = pulse['progress']
            px = n1['x'] + (n2['x'] - n1['x']) * t
            py = n1['y'] + (n2['y'] - n1['y']) * t
            
            if pulse['type'] == 'EXCITATORY':
                p.setBrush(QColor(255, 255, 100, 200)) # Yellow pulse
            else:
                p.setBrush(QColor(0, 100, 255, 200)) # Blue pulse (inhibitory)
            
            p.drawEllipse(QPointF(px, py), 4, 4)
        # 5. Draw Neurons
        for n in self.neurons:
            # Color logic
            val = max(0, min(1.0, n['activation']))
            
            if n['type'] == 'EXCITATORY':
                # Green/Yellow base
                r, g, b = 100, 255, 100
                if val > 0.5: r = 255 # Turn yellow
            else:
                # Red/Purple base (Inhibitory)
                r, g, b = 255, 50, 100
                if val > 0.5: b = 255 # Turn purple
            
            # Brightness boost on fire
            brightness = 100 + int(155 * val)
            alpha = 150 + int(105 * val)
            
            col = QColor(r, g, b)
            col.setAlpha(min(255, alpha))
            
            # Size pulses
            size = 6 + val * 6
            p.setBrush(col)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(n['x'], n['y']), size, size)
    def _fire_pulse(self, idx):
        n = self.neurons[idx]
        for conn in n['outgoing']:
            target_idx = conn['target']
            n2 = self.neurons[target_idx]
            
            dist = math.sqrt((n['x']-n2['x'])**2 + (n['y']-n2['y'])**2)
            if dist > 0:
                speed = 8.0 / dist 
                self.pulses.append({
                    'start': idx,
                    'end': target_idx,
                    'progress': 0.0,
                    'speed': speed,
                    'type': n['type'],
                    'strength': conn['weight'] * 0.4
                })
