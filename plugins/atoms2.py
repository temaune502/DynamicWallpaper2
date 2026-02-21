from shader_effect import ShaderEffect

class Atoms2Effect(ShaderEffect):
    EFFECT_NAME = "atoms2"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        #define STEPS 64
        #define EPSILON 0.005
        
        // Rotation
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }
        
        // Smooth Min (Metaballs)
        float smin(float a, float b, float k) {
            float h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0);
            return mix(b, a, h) - k*h*(1.0-h);
        }

        // Scene Map
        float map(vec3 p) {
            float d = 100.0;
            float bass = iAudio.x;
            
            // --- NUCLEUS ---
            // Cluster of protons/neutrons
            // We can fake it with a distorted sphere or multiple spheres
            
            // Central Pulse
            float scale = 1.0 + bass * 0.2;
            
            vec3 pN = p / scale;
            
            // Metaball cluster
            float d1 = length(pN - vec3(0.1, 0.1, 0.1)) - 0.25;
            float d2 = length(pN - vec3(-0.1, -0.1, -0.1)) - 0.25;
            float d3 = length(pN - vec3(-0.1, 0.1, -0.05)) - 0.22;
            float d4 = length(pN - vec3(0.15, -0.2, 0.0)) - 0.2;
            
            float nucleus = smin(d1, d2, 0.15);
            nucleus = smin(nucleus, d3, 0.15);
            nucleus = smin(nucleus, d4, 0.15);
            
            d = nucleus * scale; // Restore scale
            
            // --- ELECTRONS ---
            // We won't raymarch the trails as solid objects, but as a glow field later.
            // Here we just map the electron spheres.
            
            float t = iTime * (1.0 + iAudio.y); // Speed up with mid/treble
            
            // Electron 1
            vec3 pE1 = p;
            pE1.xy *= rot(t * 2.0);
            pE1.xz *= rot(1.0); // Tilt
            float e1 = length(pE1 - vec3(1.2, 0.0, 0.0)) - 0.08;
            
            // Electron 2
            vec3 pE2 = p;
            pE2.yz *= rot(t * 2.5 + 1.0);
            pE2.xy *= rot(-0.5);
            float e2 = length(pE2 - vec3(1.3, 0.0, 0.0)) - 0.08;

             // Electron 3
            vec3 pE3 = p;
            pE3.xz *= rot(t * 1.8 + 2.0);
            pE3.yz *= rot(2.0);
            float e3 = length(pE3 - vec3(1.1, 0.0, 0.0)) - 0.08;
            
            d = min(d, e1);
            d = min(d, e2);
            d = min(d, e3);
            
            return d;
        }
        
        // Calculate orbit intensity for glow
        float orbitGlow(vec3 p) {
            float glow = 0.0;
            float t = iTime * (1.0 + iAudio.y);
            
            // Trace the orbits as thin toruses/rings
            // Orbit 1
            vec3 p1 = p;
            p1.xz *= rot(-1.0); // Undo tilt
            // Distance to ring on XY plane
            float d1 = length(vec2(length(p1.xy) - 1.2, p1.z));
            glow += 0.01 / (d1 * d1 + 0.01);
            
            // Orbit 2
            vec3 p2 = p;
            p2.xy *= rot(0.5);
            float d2 = length(vec2(length(p2.yz) - 1.3, p2.x));
            glow += 0.01 / (d2 * d2 + 0.01);
            
             // Orbit 3
            vec3 p3 = p;
            p3.yz *= rot(-2.0);
            float d3 = length(vec2(length(p3.xz) - 1.1, p3.y));
            glow += 0.01 / (d3 * d3 + 0.01);
            
            return glow;
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;
            
            vec3 ro = vec3(0.0, 0.0, -3.5);
            vec3 rd = normalize(vec3(uv, 1.5));
            
            // Slight camera movement
            float t = iTime * 0.2;
            ro.xy += vec2(sin(t), cos(t*1.2)) * 0.2;
            
            vec3 col = vec3(0.02, 0.02, 0.05); // Dark BG
            
            float t_march = 0.0;
            float at = 0.0; // Accumulated Glow
            
            for(int i=0; i<STEPS; i++) {
                vec3 p = ro + rd * t_march;
                float d = map(p);
                
                // Nucleus Glow (Orange/Red)
                float nDist = length(p) - 0.3; // Approx distance to center
                float nGlow = 0.05 / (nDist*nDist + 0.05);
                
                // Audio reaction color for nucleus
                vec3 nColor = mix(vec3(1.0, 0.3, 0.0), vec3(1.0, 0.9, 0.5), iAudio.x);
                at += nGlow * 0.1;
                col += nColor * nGlow * 0.01;
                
                // Orbit Trails Glow (Blue/Cyan)
                float oGlow = orbitGlow(p);
                col += vec3(0.0, 0.6, 1.0) * oGlow * 0.02;
                
                if(d < EPSILON) {
                    // Surface Hit
                    vec3 n = normalize(vec3(
                        map(p + vec3(EPSILON,0,0)) - map(p - vec3(EPSILON,0,0)),
                        map(p + vec3(0,EPSILON,0)) - map(p - vec3(0,EPSILON,0)),
                        map(p + vec3(0,0,EPSILON)) - map(p - vec3(0,0,EPSILON))
                    ));
                    
                    float diff = max(dot(n, normalize(vec3(1.0, 1.0, -1.0))), 0.0);
                    float fresnel = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);
                    
                    vec3 objCol = vec3(1.0);
                    
                    if (length(p) > 0.8) {
                        // Electron
                        objCol = vec3(0.2, 0.8, 1.0) * 2.0; // Bright Blue
                    } else {
                        // Nucleus
                        objCol = nColor;
                    }
                    
                    col += objCol * (diff + 0.5) + vec3(1.0)*fresnel;
                    break;
                }
                
                t_march += max(d * 0.6, 0.02); // Slower march for better glow integration
                if(t_march > 10.0) break;
            }
            
            // Bloom / Atmosphere
            col *= 1.2;
            
            // Gamma
            col = pow(col, vec3(0.9));

            fragColor = vec4(col, 1.0);
        }
        """
