from shader_effect import ShaderEffect

class AuroraWavesEffect(ShaderEffect):
    EFFECT_NAME = "aurora_waves"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        mat2 rot(float a){
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }

        void main() {
            vec2 uv = gl_FragCoord.xy / iResolution.xy;
            float ratio = iResolution.x / iResolution.y;
            uv.x *= ratio;

            vec3 col = vec3(0.0);
            float t = iTime * 0.5;
            
            // Audio modulate
            float bass = iAudio.x;
            
            // Background
            col = vec3(0.0, 0.05, 0.1) * (1.0 - uv.y); // Deep blue fading up
            
            // Aurora layers
            for(float i=0.0; i<4.0; i++) {
                vec2 q = uv;
                
                // Animate position
                q.x += i * 0.5;
                q.y += sin(q.x * 2.0 + t + i) * 0.1;
                
                // Rotation per layer
                q -= vec2(1.0, 0.0);
                q *= rot(t * 0.1 + i);
                q += vec2(1.0, 0.0);
                
                float wave = sin(q.x * 5.0 + t * 2.0) * 0.5 + 0.5;
                wave *= sin(q.y * 3.0 - t);
                
                // Smooth band
                float band = smoothstep(0.1, 0.0, abs(wave - uv.y + 0.5));
                
                // Color per layer
                vec3 pal = 0.5 + 0.5 * cos(q.x + t + vec3(0.0, 2.0, 4.0)); // Rainbow shift
                // Add Green/Teal classic aurora tint
                pal = mix(pal, vec3(0.0, 1.0, 0.5), 0.5);
                
                // Audio brightness
                float brightness = 0.2 + bass * 0.3;
                col += band * pal * brightness;
            }
            
            // Stars
            float stars = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
            if(stars > 0.995) col += vec3(1.0) * (0.5 + 0.5*sin(t*5.0 + stars*100.0));

            fragColor = vec4(col, 1.0);
        }
        """
