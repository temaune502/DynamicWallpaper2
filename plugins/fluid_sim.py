from shader_effect import ShaderEffect

class FluidSimEffect(ShaderEffect):
    EFFECT_NAME = "fluid_sim"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        void main() {
            vec2 uv = gl_FragCoord.xy / iResolution.xy;
            float time = iTime * 0.2;
            
            // Audio influence
            float speed = 1.0 + iAudio.x * 2.0;

            vec2 p = uv * 8.0 - vec2(4.0); // Center coordinates
            vec2 i = p;
            float c = 1.0;
            float inten = .05;

            for (int n = 0; n < 4; n++) {
                float t = time * speed * (1.0 - (3.0 / float(n+1)));
                i = p + vec2(cos(t - i.x) + sin(t + i.y), 
                             sin(t - i.y) + cos(t + i.x));
                c += 1.0 / length(vec2(p.x / (sin(i.x+t)/inten), 
                                       p.y / (cos(i.y+t)/inten)));
            }
            c /= 4.0;
            c = 1.5 - sqrt(c);
            c = clamp(c, 0.0, 1.0);
            
            vec3 col = vec3(pow(c, 4.0));
            col = mix(col, vec3(0.0, 0.3, 1.0), 0.3); // Blue tint
            col += vec3(0.0, iAudio.y * 0.5, iAudio.z); // Audio colors
            
            fragColor = vec4(col, 1.0);
        }
        """
