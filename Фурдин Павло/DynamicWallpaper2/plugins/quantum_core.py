from shader_effect import ShaderEffect

class QuantumCoreEffect(ShaderEffect):
    EFFECT_NAME = "quantum_core"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        // Rotation matrix
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }

        // Distance function for the core
        float map(vec3 p) {
            float bass = iAudio.x;
            
            // Rotate the whole world
            p.xz *= rot(iTime * 0.5);
            p.xy *= rot(iTime * 0.3);

            // Pulse deformation
            float pulse = sin(p.x * 10.0 + iTime * 5.0) * sin(p.y * 10.0 + iTime * 4.0) * sin(p.z * 10.0 + iTime * 3.0);
            pulse *= 0.1 * (1.0 + bass * 5.0); // Bass amplifies deformation

            // Base sphere
            float d = length(p) - 1.0;
            
            // Add complexity
            d += pulse;
            
            // Inner hollow
            d = max(d, -(length(p) - 0.8));
            
            return d * 0.5;
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
            
            vec3 ro = vec3(0.0, 0.0, -3.0); // Ray origin
            vec3 rd = normalize(vec3(uv, 1.0)); // Ray direction
            
            // Audio camera shake
            float bass = iAudio.x;
            if(bass > 0.4) {
                ro.x += sin(iTime * 50.0) * 0.02 * bass;
                ro.y += cos(iTime * 45.0) * 0.02 * bass;
            }

            float t = 0.0;
            float d = 0.0;
            vec3 p = vec3(0.0);
            
            // Acccumulate color (volumetric glow)
            vec3 glow = vec3(0.0);
            
            for(int i = 0; i < 64; i++) {
                p = ro + rd * t;
                d = map(p);
                
                // Glow accumulation based on proximity to surface
                float dist = length(p);
                float glowFactor = 0.02 / (abs(d) + 0.01);
                
                // Color palette
                vec3 pal = 0.5 + 0.5 * cos(iTime + dist * 2.0 + vec3(0.0, 0.2, 0.4));
                
                // Audio boosts glow
                glow += pal * glowFactor * (0.5 + iAudio.y * 2.0);
                
                if(d < 0.001 || t > 10.0) break;
                
                t += d;
            }
            
            // Background
            vec3 col = vec3(0.0);
            
            // Add core glow
            col += glow * 0.05;
            
            // Treble sparkles in background
            float stars = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
            if(stars > 0.98) {
                col += vec3(iAudio.z) * 2.0 * step(length(uv), 1.0); // Only outside center roughly
            }

            // Post processing
            col = pow(col, vec3(0.8)); // Gamma correct
            
            fragColor = vec4(col, 1.0);
        }
        """
