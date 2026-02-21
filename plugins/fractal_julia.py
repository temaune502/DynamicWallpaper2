from shader_effect import ShaderEffect

class FractalJuliaEffect(ShaderEffect):
    EFFECT_NAME = "fractal_julia"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        // Palette
        vec3 palette( float t ) {
            vec3 a = vec3(0.5, 0.5, 0.5);
            vec3 b = vec3(0.5, 0.5, 0.5);
            vec3 c = vec3(1.0, 1.0, 1.0);
            vec3 d = vec3(0.263,0.416,0.557);
            return a + b*cos( 6.28318*(c*t+d) );
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;
            vec2 uv0 = uv;
            
            float bass = iAudio.x;
            float mid = iAudio.y;
            
            vec3 finalColor = vec3(0.0);
            
            // Fractal iteration
            for (float i = 0.0; i < 4.0; i++) {
                uv = fract(uv * 1.5) - 0.5;

                float d = length(uv) * exp(-length(uv0));

                vec3 col = palette(length(uv0) + i*.4 + iTime*.4);

                d = sin(d*8. + iTime)/8.;
                d = abs(d);

                d = pow(0.01 / d, 1.2);

                finalColor += col * d;
            }
            
            // Audio reactivity
            finalColor *= (0.8 + bass * 0.5);
            
            // Add a Julia-like twist in the center
            vec2 z = uv0;
            vec2 c = vec2(sin(iTime*0.5)*0.5, cos(iTime*0.3)*0.5);
            c += vec2(mid*0.1, bass*0.1); // Audio distorts the set
            
            float iter = 0.0;
            for(int i=0; i<32; i++) {
                z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
                if(length(z) > 2.0) break;
                iter++;
            }
            
            float f = iter / 32.0;
            vec3 juliaCol = 0.5 + 0.5*cos(3.0 + f*10.0 + iTime + vec3(0,0.6,1.0));
            
            // Blend the neon fractal background with the Julia set
            finalColor = mix(finalColor, juliaCol, smoothstep(0.0, 1.5, length(z)*0.1));

            fragColor = vec4(finalColor, 1.0);
        }
        """
