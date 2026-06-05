from shader_effect import ShaderEffect

class PlasmaOrbEffect(ShaderEffect):
    EFFECT_NAME = "plasma_orb"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        #define STEPS 40
        #define EPSILON 0.005
        
        // --- NOISE FUNCTIONS ---
        // Fast float hash (без sin)
        // Fast float hash (без sin)
        float hash(float n)
        {
            n = fract(n * 0.1031);
            n *= n + 33.33;
            n *= n + n;
            return fract(n);
        }

        float hash31(vec3 p)
        {
            p = fract(p * 0.1031);
            p += dot(p, p.yzx + 33.33);
            return fract((p.x + p.y) * p.z);
        }


        float noise(vec3 x) {
        vec3 i = floor(x);
        vec3 f = fract(x);

        f = f * f * (3.0 - 2.0 * f); // smooth interpolation

        float n000 = hash31(i + vec3(0,0,0));
        float n100 = hash31(i + vec3(1,0,0));
        float n010 = hash31(i + vec3(0,1,0));
        float n110 = hash31(i + vec3(1,1,0));
        float n001 = hash31(i + vec3(0,0,1));
        float n101 = hash31(i + vec3(1,0,1));
        float n011 = hash31(i + vec3(0,1,1));
        float n111 = hash31(i + vec3(1,1,1));

        return mix(
            mix(mix(n000,n100,f.x), mix(n010,n110,f.x), f.y),
            mix(mix(n001,n101,f.x), mix(n011,n111,f.x), f.y),
            f.z
        );
    }

        
        // Fractional Brownian Motion
        float fbm(vec3 p) {
            float f = 0.0;
            float w = 0.5;
            for(int i=0; i<5; i++) {
                f += w * noise(p);
                p *= 2.0;
                w *= 0.5;
            }
            return f;
        }
        
        // Rotation
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }

        // --- SCENE MAP ---
        float map(vec3 p)
{
    float bass = iAudio.x;
    float mid  = iAudio.y;

    float lenP = length(p);
    float d = lenP - 1.0;

    // Plasma distortion (менше scale)
    float n = fbm(p * 1.3 + vec3(0.0, iTime * 0.4, 0.0));

    // Audio distortion (дешевше)
    float dist = sin(p.x * 8.0 + iTime) * 0.015 * bass;

    // Branchless spikes
    float inside = smoothstep(1.2, 1.0, lenP);
    float spikes = noise(p * 4.0 + iTime * 2.0);
    spikes = spikes * spikes; // дешевше ніж smoothstep
    spikes *= 0.08 * mid * inside;

    d -= n * 0.25;
    d += dist;
    d -= spikes;

    return d * 0.7;
}


        void main() {
            vec2 uv = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;
            
            // Camera
            vec3 ro = vec3(0.0, 0.0, -2.8);
            vec3 rd = normalize(vec3(uv, 1.0));
            
            // Shake on heavy bass
            if (iAudio.x > 0.4) {
                ro.xy += (vec2(hash(iTime), hash(iTime+1.0))-0.5) * 0.05 * iAudio.x;
            }
            
            // Raymarch for Volumetric Glow
            vec3 col = vec3(0.0);
            float t = 0.0;
            
            vec3 orbitColor = vec3(0.2, 0.6, 1.0); // Cyan Blue
            vec3 coreColor = vec3(1.0, 0.2, 0.8); // Magenta Core
            
            float density = 0.0;
            
            for(int i=0; i<STEPS; i++) {
                vec3 p = ro + rd * t;
                
                // Rotation
                p.xz *= rot(iTime * 0.2);
                p.xy *= rot(iTime * 0.1);
                
                float d = map(p);
                
                // Volumetric accumulation
                // Instead of hitting a surface, we accumulate light when close to "surface" (d near 0)
                // or inside (d < 0)
                
                float dist = abs(d);
                
                // Glow falloff
                float glow = 0.03 / (dist + 0.05);
                
                // Inside "plasma"
                if (d < 0.1) {
                    glow += 0.1; // Core density
                    density += 0.05;
                }
                
                // Electric Arcs (High frequency noise)
                float arcs = smoothstep(0.6, 0.7, noise(p * 8.0 + iTime * 3.0));
                
                vec3 localCol = mix(orbitColor, coreColor, density * 0.5);
                localCol += vec3(1.0) * arcs * iAudio.y; // White arcs on mid/treble
                
                col += localCol * glow * 0.5;
                
                // Occlusion-ish
                if (density > 2.0) break; // opaque core
                
                t += max(d * 0.4, 0.02); // March slower near density
                if(t > 5.0) break;
            }
            
            // Audio Boost to overall brightness
            col *= (0.8 + iAudio.x * 0.4);
            
            // Background Stars
            float stars = pow(hash(dot(uv, vec2(123.4, 765.1))), 200.0) * 0.5;
            col += vec3(stars);

            // Vignette
            col *= 1.2 - length(uv);
            
            // Tone mapping
            col = 1.0 - exp(-col * 1.5);

            fragColor = vec4(col, 1.0);
        }
        """
