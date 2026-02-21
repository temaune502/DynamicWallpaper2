from shader_effect import ShaderEffect

class FractalJulia1Effect(ShaderEffect):
    EFFECT_NAME = "fractal_julia1"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        void main() {
            vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
            
            // Audio influence
            float bass = iAudio.x;
            float mid = iAudio.y;
            
            // Zoom pulses with bass
            float zoom = 1.5 - bass * 0.2;
            uv *= zoom;
            
            // Julia seed changes with time and mid frequencies
            float t = iTime * 0.3;
            vec2 c = vec2(cos(t), sin(t)) * 0.7885;
            
            // Warp seed with audio
            c += vec2(sin(mid * 3.0), cos(mid * 2.0)) * 0.1;

            vec2 z = uv;
            float iter = 0.0;
            const float max_iter = 64.0;
            
            for(float i=0.0; i<max_iter; i++) {
                // Complex square z = z^2 + c
                // (x+iy)^2 = x^2 - y^2 + 2ixy
                z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
                
                if(length(z) > 4.0) break;
                iter++;
            }
            
            // Color mapping
            float f = iter / max_iter;
            
            // Palette
            vec3 col = vec3(0.0);
            if(iter < max_iter) {
                col = 0.5 + 0.5 * cos(3.0 + f * 10.0 + iTime + vec3(0.0, 0.6, 1.0));
                
                // Add glow based on audio
                col *= (1.0 + bass * 0.5);
            } else {
                // Interior color (black or deep blue)
                col = vec3(0.0, 0.0, 0.1 * bass);
            }

            fragColor = vec4(col, 1.0);
        }
        """
