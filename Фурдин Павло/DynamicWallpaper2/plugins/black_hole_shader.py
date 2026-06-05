from shader_effect import ShaderEffect

class BlackHoleShaderEffect(ShaderEffect):
    EFFECT_NAME = "black_hole_shader"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        // iAudio not used
        
        // Optimized for AMD HD 8500M
        #define STEPS 90
        #define STEPSIZE 0.1
        #define BH_RADIUS 0.5
        #define DISK_RADIUS 4.0
        
        mat2 rot(float a) {
            float s = sin(a);
            float c = cos(a);
            return mat2(c, -s, s, c);
        }
        
        // 3D Noise for stars
        float hash(float n) { return fract(sin(n) * 43758.5453); }
        float noise(vec3 x) {
            vec3 p = floor(x);
            vec3 f = fract(x);
            f = f * f * (3.0 - 2.0 * f);
            float n = p.x + p.y * 57.0 + 113.0 * p.z;
            return mix(mix(mix(hash(n + 0.0), hash(n + 1.0), f.x),
                           mix(hash(n + 57.0), hash(n + 58.0), f.x), f.y),
                       mix(mix(hash(n + 113.0), hash(n + 114.0), f.x),
                           mix(hash(n + 170.0), hash(n + 171.0), f.x), f.y), f.z);
        }

        // Procedural Starfield
        vec3 starField(vec3 rd) {
            vec3 col = vec3(0.0);
            
            // Layer 1: Bright stars
            float n1 = pow(noise(rd * 150.0), 30.0);
            col += vec3(n1);
            
            // Layer 2: Dim stars (more dense)
            float n2 = pow(noise(rd * 300.0), 20.0);
            col += vec3(n2) * 0.5;
            
            // Subtle Nebula (Purple/Blue) - Very faint
            float neb = noise(rd * 2.0 + iTime * 0.05);
            col += vec3(0.1, 0.0, 0.2) * neb * 0.2;
            
            return col;
        }

        // Accretion Disk Texture
        float diskTexture(vec3 p) {
            float r = length(p.xz);
            float angle = atan(p.z, p.x);
            
            // Spinning
            float speed = 3.0 / (r + 0.1); 
            float val = noise(vec3(r * 4.0 - iTime, angle * 3.0 - iTime * speed, 0.0));
            
            // Rings
            val += sin(r * 20.0) * 0.2;
            
            return smoothstep(0.2, 0.8, val);
        }

        void main() {
            vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
            
            // Camera position - Farther back as requested
            vec3 ro = vec3(0.0, 1.5, -8.0); // Moved from -4.5 to -8.0, and slightly higher up
            vec3 rd = normalize(vec3(uv, 1.5)); // Narrow FOV slightly for "telescope" feel
            
            // Slow orbit
            float angle = iTime * 0.05;
            ro.xz *= rot(angle);
            rd.xz *= rot(angle);
            
            // Look at center
            // Simple lookat matrix towards (0,0,0)
            vec3 f = normalize(-ro);
            vec3 r = normalize(cross(vec3(0.0, 1.0, 0.0), f));
            vec3 u = cross(f, r);
            rd = normalize(uv.x * r + uv.y * u + 2.0 * f); 

            vec3 col = vec3(0.0);
            
            // Background is NOT static, it's directional
            // Distorted by gravity at infinity
            // We'll calculate the bent ray direction at infinity later or just use standard
            // Standard skybox for now as background
            vec3 bg = starField(rd);
            
            // Raymarching
            float t = 0.0;
            vec3 p = ro;
            vec3 diskAccum = vec3(0.0);
            float alpha = 0.0;
            
            bool hitHorizon = false;
            
            for(int i=0; i<STEPS; i++) {
                p = ro + rd * t;
                float dist = length(p);
                
                // Event Horizon
                if (dist < BH_RADIUS) {
                    hitHorizon = true;
                    break;
                }
                
                // Gravity Bending
                // Newtonian approximation: Force = -p / r^3
                // Acceleration = Force
                // Velocity change = Accel * dt
                // Here we just bend the ray direction
                float gravityStrength = 0.05;
                vec3 force = -normalize(p) * gravityStrength / (dist * dist + 0.01);
                rd += force * STEPSIZE; // Bend the ray
                rd = normalize(rd);
                
                // Accretion Disk
                // Y-plane check
                float diskH = 0.05; // Thickness
                if (abs(p.y) < diskH) {
                    float r = length(p.xz);
                    if (r > BH_RADIUS * 1.5 && r < DISK_RADIUS) {
                        float density = 0.5; // Base density
                        
                        // Fade edges
                        density *= smoothstep(DISK_RADIUS, DISK_RADIUS - 0.5, r);
                        density *= smoothstep(BH_RADIUS * 1.5, BH_RADIUS * 2.0, r);
                        
                        // Texture
                        float tex = diskTexture(p);
                        
                        // Color Gradient: Hot white/blue inner, Orange/Red outer
                        vec3 innerCol = vec3(0.8, 0.9, 1.0); // Hot
                        vec3 outerCol = vec3(1.0, 0.4, 0.1); // Cool
                        vec3 diskCol = mix(outerCol, innerCol, smoothstep(DISK_RADIUS, BH_RADIUS*1.5, r));
                        
                        // Add glow
                        vec3 glow = diskCol * tex * 2.0; 
                        
                        // Integrate
                        float stepDensity = density * 0.2; // Opacity per step
                        diskAccum += glow * stepDensity * (1.0 - alpha);
                        alpha += stepDensity;
                    }
                }
                
                t += STEPSIZE;
                if (alpha > 0.98) break;
                if (dist > 15.0) break; // Too far to matter
            }
            
            // Final Composition
            if (hitHorizon) {
                col = vec3(0.0); // Pure black hole
                
                // Add a thin "photon ring" glow on the edge
                // Hard to do exact without sub-pixel steps, but let's fake it slightly around the black circle if aliased?
                // Actually the accretion disk glow usually covers it.
            } else {
                // If we didn't hit the black hole, we hit the background.
                // The ray direction 'rd' has been bent by gravity!
                // So we sample the starfield with the bent ray.
                col = starField(rd);
            }
            
            // Blend disk on top
            col = col * (1.0 - alpha) + diskAccum;
            
            // Tone mapping/Gamma
            col = pow(col, vec3(0.4545)); 
            
            fragColor = vec4(col, 1.0);
        }
        """
