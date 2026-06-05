from shader_effect import ShaderEffect

class CyberCircuitEffect(ShaderEffect):
    EFFECT_NAME = "cyber_circuit"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio;

        // 3D rotation
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
            
            float bass = iAudio.x;
            float mid = iAudio.y;

            // Camera movement
            vec3 ro = vec3(0.0, 0.0, -iTime * 2.0); // Move forward
            ro.z -= bass * 5.0; // Bass boost speed
            
            vec3 rd = normalize(vec3(uv, 1.0));
            
            // Rotation based on audio
            rd.xy *= rot(iTime * 0.2 + bass * 0.5);

            vec3 col = vec3(0.0);
            
            // Raymarch loop for a "tunnel" of square frames
            float t = 0.0;
            for(int i=0; i<32; i++) {
                vec3 p = ro + rd * t;
                
                // Domain repetition
                vec3 q = fract(p) - 0.5;
                vec3 id = floor(p);
                
                // Box SDF
                float d = max(abs(q.x), abs(q.y)) - 0.45; // Thin walls
                // Hollow out center (tunnel)
                d = max(d, -max(abs(q.x), abs(q.y)) + 0.4); 
                
                // Add some variation
                if (mod(id.z, 5.0) < 1.0) {
                     d = max(abs(q.x), abs(q.y)) - 0.3; // Thicker rings periodically
                }

                // Fog / Glow
                float dist = length(p.xy);
                float glow = 0.01 / (abs(d) + 0.001);
                
                vec3 glowCol = vec3(0.0, 0.8, 1.0); // Cyan
                if (mod(id.z + iTime*5.0, 10.0) < 1.0) glowCol = vec3(1.0, 0.2, 0.5); // Moving pulses (Red/Pink)
                
                col += glow * glowCol * 0.1;
                
                // Audio reaction
                col *= 1.0 + mid * 0.5;

                t += max(abs(d) * 0.5, 0.02); // Step forward
                if(t > 15.0) break;
            }
            
            // Fade out distance
            col *= 1.0 / (1.0 + t * 0.1);

            fragColor = vec4(col, 1.0);
        }
        """
