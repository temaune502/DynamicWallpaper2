from shader_effect import ShaderEffect

class PixelWavesEffect(ShaderEffect):
    EFFECT_NAME = "pixel_waves"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        float hash(vec2 p) {
            return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
        }

        float noise(vec2 p) {
            vec2 i = floor(p);
            vec2 f = fract(p);
            vec2 u = f * f * (3.0 - 2.0 * f);
            return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
                       mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
        }

        void main() {
            vec2 uv = gl_FragCoord.xy / iResolution.xy;
            
            // Pixelate
            float pixels = 100.0;
            uv = floor(uv * pixels) / pixels;
            
            float bass = iAudio.x;
            
            // Background gradient (Sunset)
            vec3 col = mix(vec3(1.0, 0.4, 0.6), vec3(0.2, 0.0, 0.3), uv.y);
            
            // Sun
            vec2 sunPos = vec2(0.5, 0.6);
            float sunDist = length(uv - sunPos);
            if(sunDist < 0.25) {
                // Sun stripes
                float stripe = sin(uv.y * 100.0 + iTime);
                if(stripe > 0.2 || uv.y > 0.6) {
                     col = mix(vec3(1.0, 0.9, 0.0), vec3(1.0, 0.2, 0.0), uv.y * 2.0);
                }
            }
            
            // Ocean waves
            float horizon = 0.3;
            if(uv.y < horizon) {
                // Perspective
                vec2 p = uv;
                p.x = (p.x - 0.5) / (p.y + 0.1) + 0.5;
                p.y = 1.0 / (p.y + 0.1);
                
                // Movement
                p.y += iTime * 2.0 + bass * 2.0;
                
                float wave = noise(p * vec2(1.0, 0.5));
                float wave2 = noise(p * vec2(2.0, 1.0) + iTime);
                
                float foam = step(0.6, wave + wave2 * 0.5);
                
                vec3 waterCol = vec3(0.1, 0.0, 0.3);
                vec3 foamCol = vec3(0.0, 0.8, 1.0);
                
                // Pulse foam with audio
                foamCol *= (1.0 + iAudio.y);
                
                col = mix(waterCol, foamCol, foam);
                
                // Reflection?
                if(abs(uv.x - 0.5) < 0.2 && uv.y > 0.1) {
                    col += vec3(0.5, 0.0, 0.2) * 0.5;
                }
            }

            fragColor = vec4(col, 1.0);
        }
        """
