from shader_effect import ShaderEffect

class FractalPyramidEffect(ShaderEffect):
    EFFECT_NAME = "fractal_pyramid"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        #define STEPS 64
        #define EPSILON 0.001
        
        // Rotation
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }
        
        // Palette
        vec3 palette(float t) {
            return vec3(0.5) + vec3(0.5)*cos( 6.28318*(vec3(1.0)*t+vec3(0.0,0.33,0.67)) );
        }

        // Sierpinski Pyramid DE
        float de(vec3 p) {
            float scale = 2.0;
            float offset = 1.0;
            
            float bass = iAudio.x;
            
            // Audio distortion
            p.y += sin(p.x*10.0 + iTime)*0.02 * bass;

            for(int n=0; n<4; n++) { // Iterations
                p.xy = (p.x+p.y < 0.0) ? -p.yx : p.xy;
                p.xz = (p.x+p.z < 0.0) ? -p.zx : p.xz;
                p.zy = (p.z+p.y < 0.0) ? -p.yz : p.zy;
                
                p = p*scale - offset*(scale-1.0);
            }
            
            return length(p) * pow(scale, -float(4));
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;
            
            float bass = iAudio.x;
            float mid = iAudio.y;

            vec3 ro = vec3(0.0, 0.0, -2.5);
            vec3 rd = normalize(vec3(uv, 1.5));
            
            // Camera rotation based on audio + time
            float angle = iTime * 0.2 + bass * 0.2;
            ro.xz *= rot(angle);
            rd.xz *= rot(angle);
            
            // Vertical slight tilt
            ro.yz *= rot(0.5);
            rd.yz *= rot(0.5);

            vec3 col = vec3(0.0);
            
            float t = 0.0;
            float glow = 0.0;
            
            for(int i=0; i<STEPS; i++) {
                vec3 p = ro + rd * t;
                float d = de(p);
                
                // Accumulate glow near surface
                glow += 0.02 / (abs(d) + 0.02);
                
                if(d < EPSILON) break;
                t += d;
                if(t > 10.0) break;
            }
            
            // Coloring based on glow + audio
            vec3 glowCol = palette(length(uv) + iTime * 0.5);
            col += glow * glowCol * 0.05;
            
            // Audio boost
            col *= (1.0 + mid * 2.0);

            // Background subtle gradient
            col += vec3(0.1, 0.0, 0.2) * (1.0 - length(uv));

            fragColor = vec4(col, 1.0);
        }
        """
