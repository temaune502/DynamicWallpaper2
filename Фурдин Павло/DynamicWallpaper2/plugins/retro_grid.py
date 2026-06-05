from shader_effect import ShaderEffect

class RetroGridEffect(ShaderEffect):
    EFFECT_NAME = "retro_grid"
    
    def get_fragment_shader(self):
        return """
        #version 330 core

out vec4 fragColor;

uniform float iTime;
uniform vec2 iResolution;
uniform vec3 iAudio; // bass, mid, treble

// Simple star noise
float hash(vec2 p){
    return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453);
}

void main()
{
    vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;

    float bass = iAudio.x;
    float mid  = iAudio.y;

    float horizon = -0.15;

    // ---------------- SKY ----------------
    float skyMask = step(horizon, uv.y);

    vec3 skyCol = vec3(0.0);

    if(skyMask > 0.0)
    {
        vec2 sunPos = vec2(0.0, 0.25);
        float sunDist = length(uv - sunPos);

        float sun = smoothstep(0.32, 0.28, sunDist);

        // Stripes
        float stripe = sin((uv.y - sunPos.y) * 60.0);
        float stripeMask = step(0.4, stripe);
        sun *= mix(1.0, stripeMask, step(uv.y, sunPos.y + 0.12));

        vec3 sunCol = vec3(1.0, 0.2, 0.6) * sun;

        vec3 grad = mix(
            vec3(0.3, 0.0, 0.5),
            vec3(0.0, 0.0, 0.1),
            smoothstep(horizon, 0.8, uv.y)
        );

        float stars = step(0.997, hash(floor(uv * 200.0)));
        stars *= (1.0 - sun);

        skyCol = grad + sunCol + vec3(stars);
    }

    // ---------------- GRID ----------------
    vec3 gridCol = vec3(0.0);

    if(skyMask < 1.0)
    {
        float y = uv.y - horizon;
        float depth = 1.0 / (y * 4.0 + 0.2);   // stabilized perspective

        vec2 gridUV = uv * depth;
        gridUV.x *= 2.0;

        // forward motion
        gridUV.y += iTime * (2.0 + bass * 6.0);

        vec2 g = abs(fract(gridUV) - 0.5);

        float line = min(g.x, g.y);

        float thickness = 0.015;
        float mask = smoothstep(thickness, 0.0, line);

        float glow = 0.02 / (line + 0.02);
        glow *= (1.0 + mid * 3.0);

        gridCol = vec3(0.0, 0.9, 1.0) * (mask + glow * 0.3);

        // distance fade (more correct)
        float fade = smoothstep(8.0, 0.5, depth);
        gridCol *= fade;
    }

    fragColor = vec4(skyCol + gridCol, 1.0);
}
        """
