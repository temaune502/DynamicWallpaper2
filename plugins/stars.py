from shader_effect import ShaderEffect

class StarNestGLSLEffect(ShaderEffect):
    EFFECT_NAME = "stars_GLSL"
    
    def get_fragment_shader(self):
        return """
#version 330 core
out vec4 fragColor;

uniform float iTime;
uniform vec2 iResolution;

#define ITER 12
#define VOLSTEPS 15
#define STEPSIZE 0.1
#define ZOOM 0.8
#define TILE 0.85
#define SPEED 0.01
#define BRIGHT 0.0015
#define DM 0.3
#define FADE 0.73
#define SAT 0.85

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy - 0.5;
    uv.y *= iResolution.y / iResolution.x;

    vec3 dir = vec3(uv * ZOOM, 1.0);
    float time = iTime * SPEED + 0.25;

    mat2 rot1 = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    mat2 rot2 = mat2(cos(0.8), sin(0.8), -sin(0.8), cos(0.8));

    dir.xz *= rot1;
    dir.xy *= rot2;

    vec3 from = vec3(1.0, 0.5, 0.5) + vec3(time * 2.0, time, -2.0);
    from.xz *= rot1;
    from.xy *= rot2;

    vec3 col = vec3(0.0);
    float fade = 1.0;
    float s = 0.1;

    for(int r=0; r<VOLSTEPS; r++){
        vec3 p = from + dir * s * 0.5;
        // Залишаємо abs+mod, щоб fractal залишався стабільним
        p = abs(vec3(TILE) - mod(p, vec3(TILE*2.0)));

        float a = 0.0;
        float pa = 0.0;

        for(int i=0; i<ITER; i++){
            p = abs(p)/dot(p,p) - 0.53;
            float len = length(p);
            a += abs(len - pa);
            pa = len;
        }

        float dm = max(0.0, DM - a*a*0.001);
        if(r>6) fade *= 1.0 - dm;

        col += vec3(s, s*s, s*s*s*s) * a * BRIGHT * fade;
        fade *= FADE;
        s += STEPSIZE;
    }

    col = mix(vec3(length(col)), col, SAT);
    fragColor = vec4(clamp(col*5.0,0.0,1.0),1.0);

}

        """


