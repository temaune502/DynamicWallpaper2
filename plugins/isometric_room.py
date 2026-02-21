from shader_effect import ShaderEffect

class IsometricRoomEffect(ShaderEffect):
    EFFECT_NAME = "isometric_room"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        #define STEPS 64
        #define EPSILON 0.002
        
        // Rotation
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }
        
        // SDF Primitives
        float sdBox(vec3 p, vec3 b) {
            vec3 q = abs(p) - b;
            return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
        }
        
        float sdCylinder(vec3 p, vec2 h) {
            vec2 d = abs(vec2(length(p.xz),p.y)) - h;
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }

        // Scene Map
        float map(vec3 p) {
            float d = 100.0;
            
            // Floor (y = -1.0)
            float floorD = p.y + 1.0;
            d = min(d, floorD);
            
            // Walls are implicit boundaries for shadows, but let's make them real
            // Back Wall (z = 2.0)
            float wallBack = sdBox(p - vec3(0.0, 1.0, 2.1), vec3(2.5, 2.0, 0.1));
            d = min(d, wallBack);
            // Side Wall (x = -2.0)
            float wallSide = sdBox(p - vec3(-2.1, 1.0, 0.0), vec3(0.1, 2.0, 2.5));
            d = min(d, wallSide);
            
            // Window in Side Wall
            if (abs(p.x - (-2.1)) < 0.2 && abs(p.z) < 1.0 && abs(p.y - 0.5) < 0.6) {
                 // Cutout for window
                 d = max(d, -sdBox(p - vec3(-2.1, 0.5, 0.0), vec3(0.2, 0.5, 0.8)));
                 // Add Glass pane
                 d = min(d, sdBox(p - vec3(-2.05, 0.5, 0.0), vec3(0.01, 0.5, 0.8)));
                 // Window Bars
                 d = min(d, sdBox(p - vec3(-2.0, 0.5, 0.0), vec3(0.05, 0.5, 0.05)));
            }

            // Bed
            vec3 bedPos = p - vec3(1.2, -0.6, 1.0);
            float bedFrame = sdBox(bedPos, vec3(0.6, 0.1, 0.8));
            float mattress = sdBox(p - vec3(1.2, -0.4, 1.0), vec3(0.55, 0.1, 0.75));
            float pillow = sdBox(p - vec3(1.2, -0.25, 0.4), vec3(0.3, 0.05, 0.15));
            d = min(d, min(bedFrame, min(mattress, pillow)));
            
            // Desk (L-Shape)
            // Main part
            float desk1 = sdBox(p - vec3(-0.8, -0.4, -1.0), vec3(1.0, 0.05, 0.4));
            // Side part
            float desk2 = sdBox(p - vec3(-1.4, -0.4, 0.0), vec3(0.4, 0.05, 1.0));
            d = min(d, min(desk1, desk2));
            
            // PC Tower
            float pc = sdBox(p - vec3(-1.5, -0.1, 0.5), vec3(0.15, 0.25, 0.25));
            d = min(d, pc);
            
            // Monitors (Double setup)
            float mon1 = sdBox(p - vec3(-0.8, -0.1, -1.2), vec3(0.4, 0.22, 0.02));
            float mon2 = sdBox(p - vec3(-1.6, -0.1, -0.4), vec3(0.02, 0.22, 0.4));
            d = min(d, min(mon1, mon2));
            
            // Chair
            vec3 chairPos = p - vec3(-0.5, -0.6, -0.3);
            chairPos.xz *= rot(0.5); // Angled
            float seat = sdBox(chairPos, vec3(0.2, 0.05, 0.2));
            float back = sdBox(chairPos - vec3(0.0, 0.3, -0.2), vec3(0.2, 0.25, 0.02));
            float stand = sdCylinder(chairPos - vec3(0.0, -0.2, 0.0), vec2(0.03, 0.2));
            d = min(d, min(seat, min(back, stand)));

            // Rug
            float rug = sdBox(p - vec3(0.0, -0.99, 0.0), vec3(0.8, 0.01, 1.2));
            d = min(d, rug);
            
            // Floating Hologram
            vec3 holoPos = p - vec3(0.0, 0.5, 0.0);
            holoPos.y -= sin(iTime)*0.1;
            holoPos.xz *= rot(iTime);
            float holo = sdBox(holoPos, vec3(0.15)); // Wireframe cube?
            // Actually just a cube for now
            d = min(d, holo);

            return d;
        }

        vec3 calcNormal(vec3 p) {
            const vec2 h = vec2(EPSILON, 0);
            return normalize(vec3(map(p+h.xyy) - map(p-h.xyy),
                                  map(p+h.yxy) - map(p-h.yxy),
                                  map(p+h.yyx) - map(p-h.yyx)));
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;
            
            // Orthographic Camera (Isometric View)
            // Look from corner
            vec3 ro = vec3(10.0, 10.0, 10.0); 
            vec3 ta = vec3(0.0, 0.0, 0.0);
            
            vec3 cw = normalize(ta - ro);
            vec3 cp = vec3(0.0, 1.0, 0.0);
            vec3 cu = normalize(cross(cw, cp));
            vec3 cv = normalize(cross(cu, cw));
            
            float zoom = 3.0; // Fixed zoom
            vec3 rd = cw;
            ro = ro + (cu * uv.x + cv * uv.y) * zoom;
            
            // Audio Impact
            float bass = iAudio.x;
            
            vec3 col = vec3(0.05, 0.05, 0.08); // Dark background
            
            float t = 0.0;
            for(int i=0; i<STEPS; i++) {
                vec3 p = ro + rd * t;
                float d = map(p);
                
                if(d < EPSILON) {
                    vec3 n = calcNormal(p);
                    vec3 ld = normalize(vec3(-1.0, 2.0, 1.0)); // Main Light
                    
                    float diff = max(dot(n, ld), 0.0);
                    float amb = 0.5 + 0.5 * n.y;
                    
                    // Material ID by Position check (hacky but works for simple scenes)
                    vec3 mate = vec3(0.5); // Grey default
                    
                    // Floor (Wood/Dark)
                    if (p.y < -0.95) {
                        mate = vec3(0.2, 0.15, 0.15); // Dark wood
                        // Check rug
                        if (abs(p.x) < 0.8 && abs(p.z) < 1.2 && p.y > -0.995) {
                            mate = vec3(0.3, 0.1, 0.4); // Purple rug
                        }
                    }
                    else if (p.x < -1.9 || p.z > 1.9) mate = vec3(0.3, 0.35, 0.4); // Walls (Concrete)
                    
                    // Bed
                    else if (p.x > 0.5 && p.z > 0.0) {
                        if (p.y > -0.3) mate = vec3(0.8, 0.8, 0.9); // Pillow
                        else if (p.y > -0.5) mate = vec3(0.1, 0.3, 0.6); // Sheets (Blue)
                        else mate = vec3(0.2, 0.1, 0.05); // Wood frame
                    }
                    
                    // Desk
                    else if (p.x < -0.3 && (p.z < -0.5 || p.x < -1.1)) mate = vec3(0.1, 0.1, 0.1); // Black Desk
                    
                    // Monitors
                    else if (p.y > -0.2 && (p.z < -1.1 || p.x < -1.5)) {
                         // Screen glow
                         if ((p.x > -1.2 && p.z < -1.18) || (p.x < -1.58)) {
                             mate = vec3(0.0, 0.8, 1.0); // Cyan Screen
                             diff = 2.0; // Glow
                             // Flicker
                             mate *= 0.8 + 0.2*sin(iTime * 10.0);
                         } else {
                             mate = vec3(0.1); // Bezel
                         }
                    }
                    
                    // PC Tower
                    else if (p.x < -1.3 && p.y < 0.2 && p.z > 0.2) {
                        mate = vec3(0.1); 
                        // RGB Lighting Strip
                        if (p.z > 0.3 && p.z < 0.35) {
                            mate = vec3(1.0, 0.0, 1.0); // Magenta
                            diff = 2.0;
                        }
                    }
                    
                    // Hologram
                    else if (abs(p.x) < 0.2 && p.y > 0.0 && abs(p.z) < 0.2) {
                        mate = vec3(0.0, 1.0, 0.5); // Green Holo
                        mate *= 0.5 + 0.5*sin(p.y * 50.0 + iTime * 10.0); // Scanlines
                        diff = 2.0; 
                    }

                    // Window Glow (Purple Neon outside)
                    if (p.x < -1.95 && p.y > 0.0 && abs(p.z) < 1.0) {
                       vec3 neon = vec3(0.8, 0.0, 1.0);
                       diff += 0.5; // Ambient bloom
                       mate = mix(mate, neon, 0.2);
                    }
                    
                    col = mate * diff * vec3(1.0, 0.95, 0.9) + mate * amb * vec3(0.2, 0.2, 0.4);
                    
                    // Fog/Distance
                    // float dist = length(p - ro); -- Ortho doesn't use dist the same way
                    
                    break;
                }
                
                t += d;
                if(t > 30.0) break;
            }
            
            col = pow(col, vec3(0.8)); // Gamma

            fragColor = vec4(col, 1.0);
        }
        """
