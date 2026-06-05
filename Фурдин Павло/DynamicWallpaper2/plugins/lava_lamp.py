from shader_effect import ShaderEffect

class LavaLampEffect(ShaderEffect):
    EFFECT_NAME = "lava_lamp"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        #define STEPS 90
        #define EPSILON 0.002
        
        // Smooth Min (Soft Blending)
        float smin(float a, float b, float k) {
            float h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0);
            return mix(b, a, h) - k*h*(1.0-h);
        }

        // Domain Repetition / Noise
        float hash(float n) { return fract(sin(n) * 43758.5453); }

        float map(vec3 p) {
            float d = 10.0;
            
            // Container bound (Cylinder)
            float container = max(length(p.xz) - 1.2, abs(p.y) - 2.8);
            
            // Blobs
            float t = iTime * 0.8;
            float bass = iAudio.x;
            
            // Base blob (bottom)
            float base = length(p - vec3(0.0, -2.5, 0.0)) - 0.8;
            d = base;
            
            // Floating blobs
            for(int i=0; i<5; i++) {
                float fi = float(i);
                float offset = fi * 2.0;
                
                // Vertical movement loop
                float y = -2.5 + 5.0 * fract(t * 0.1 + offset * 0.13);
                
                // Horizontal sway
                float x = sin(t * 0.5 + offset) * 0.5;
                float z = cos(t * 0.4 + offset * 1.5) * 0.5;
                
                // Audio reaction (size pulse)
                float r = 0.35 + 0.1 * sin(fi);
                if (i==0) r += bass * 0.2;
                
                // Shape deformation
                vec3 blobPos = p - vec3(x, y, z);
                float blob = length(blobPos) - r;
                
                // Stretch when moving up
                // Approximated by non-uniform scaling distance
                
                d = smin(d, blob, 0.6);
            }
            
            // Cut off outside container
            d = max(d, container - 0.1); 
            
            return d;
        }

        vec3 calcNormal(vec3 p) {
            vec2 e = vec2(EPSILON, 0.0);
            return normalize(vec3(
                map(p+e.xyy) - map(p-e.xyy),
                map(p+e.yxy) - map(p-e.yxy),
                map(p+e.yyx) - map(p-e.yyx)
            ));
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;
            
            vec3 ro = vec3(0.0, 0.0, -4.5);
            vec3 rd = normalize(vec3(uv, 1.5));
            
            // Background Gradient (Dark Blue/Purple)
            vec3 col = mix(vec3(0.05, 0.0, 0.1), vec3(0.0, 0.05, 0.15), uv.y + 0.5);
            
            // Glass container visual
            if (abs(uv.x) < 0.85) {
                // Glass refraction/tint
                col += vec3(0.05, 0.0, 0.1) * 0.5;
                // Edges
                float edge = smoothstep(0.8, 0.85, abs(uv.x));
                col += edge * vec3(0.5, 0.5, 1.0) * 0.3;
            }

            // Raymarching
            float t = 0.0;
            for(int i=0; i<STEPS; i++) {
                vec3 p = ro + rd * t;
                float d = map(p);
                
                if(d < EPSILON) {
                    vec3 n = calcNormal(p);
                    vec3 ld = normalize(vec3(2.0, 5.0, -3.0));
                    
                    // Lighting
                    float diff = max(dot(n, ld), 0.0);
                    float spec = pow(max(dot(reflect(-ld, n), -rd), 0.0), 16.0);
                    float fresnel = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);
                    
                    // Wax Material (Subsurface Scattering approximation)
                    // Bright orange/pink core, darker edges
                    vec3 baseCol = vec3(1.0, 0.1, 0.4); // Pinkish Red
                    vec3 warmCol = vec3(1.0, 0.6, 0.0); // Orange/Yellow
                    
                    // Height gradient
                    vec3 objCol = mix(baseCol, warmCol, p.y * 0.2 + 0.5);
                    
                    // SSS: Emulate light passing through (thinner parts brighter)
                    // We don't have thickness, so use normal.y or similar trick
                    float sss = smoothstep(-0.5, 0.5, n.y) * 0.5 + 0.5;
                    
                    col = objCol * (diff * 0.5 + 0.5) * sss;
                    col += vec3(1.0, 0.8, 0.6) * spec; // Sticky highlight
                    col += vec3(0.5, 0.0, 0.5) * fresnel; // Rim
                    
                    break;
                }
                
                t += d * 0.8; // Safe step
                if(t > 10.0) break;
            }
            
            // Post-processing glass reflections
            if (abs(uv.x) < 0.85) {
               // Fake vertical highlight
               float highlight = smoothstep(0.02, 0.0, abs(abs(uv.x) - 0.6));
               col += highlight * 0.1;
            }
            
            col = pow(col, vec3(0.9)); // Gamma

            fragColor = vec4(col, 1.0);
        }
        """
