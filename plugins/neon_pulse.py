from shader_effect import ShaderEffect

class NeonPulseEffect(ShaderEffect):
    EFFECT_NAME = "neon_pulse"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        // Hexagon function
        float hex(vec2 p) {
            p = abs(p);
            float c = dot(p, normalize(vec2(1.0, 1.73)));
            c = max(c, p.x);
            return c;
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
            vec3 finalColor = vec3(0.0);
            
            float zoom = 3.0;
            
            // Audio influence
            float bass = iAudio.x;
            float mid = iAudio.y;
            float treble = iAudio.z;

            // Multiple layers
            for(float i=0.0; i<3.0; i++) {
                vec2 t_uv = uv * zoom + i;
                t_uv.x += iTime * 0.1 * (i + 1.0);
                t_uv.y += sin(iTime * 0.5 + i) * 0.2;
                
                // Audio warp
                t_uv += bass * 0.1;

                vec2 id = floor(t_uv);
                vec2 gv = fract(t_uv) - 0.5;
                
                float d = hex(gv);
                
                // Glow distance
                float glow = 0.02 / abs(d - 0.4 + sin(iTime + i)*0.1);
                
                // Pulse with bass
                glow *= (1.0 + bass * 3.0);
                
                vec3 col = vec3(0.5 + 0.5*sin(i + iTime), 0.5 + 0.5*cos(iTime), 1.0);
                col += mid * vec3(1.0, 0.5, 0.0); // Add orange on mids
                
                finalColor += col * glow * (1.0 / (i + 1.0));
            }
            
            fragColor = vec4(finalColor, 1.0);
        }
        """
