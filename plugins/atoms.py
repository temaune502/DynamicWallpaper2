from shader_effect import ShaderEffect

class AtomsEffect(ShaderEffect):
    EFFECT_NAME = "atoms"
    
    def get_fragment_shader(self):
        return """
#version 330 core
out vec4 fragColor;

uniform float iTime;
uniform vec2 iResolution;
uniform vec3 iAudio;

float hash(vec2 p)
{
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float circle(vec2 uv, vec2 pos, float r)
{
    return smoothstep(r, r - 0.01, length(uv - pos));
}

void main()
{
    vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;

    vec3 col = vec3(0.0);

    float bass = iAudio.x;
    float mid  = iAudio.y;

    const int ATOMS = 6;

    for(int i = 0; i < ATOMS; i++)
    {
        float fi = float(i);

        // позиція ядра
        vec2 center = vec2(
            sin(fi * 1.7 + iTime * 0.5),
            cos(fi * 1.3 + iTime * 0.4)
        ) * 0.6;

        float nucleus = circle(uv, center, 0.05 + bass * 0.03);

        col += vec3(1.0, 0.6, 0.2) * nucleus * 3.0;

        // орбіти
        for(int e = 0; e < 3; e++)
        {
            float fe = float(e);

            float angle = iTime * (1.0 + fe * 0.4) + fi * 2.0;

            float radius = 0.12 + fe * 0.05;

            vec2 electronPos = center + vec2(
                cos(angle),
                sin(angle)
            ) * radius;

            float electron = circle(uv, electronPos, 0.015);

            col += vec3(0.2, 0.8, 1.0) * electron * 2.0;
        }

        // хвильова хмара
        float wave = sin(length(uv - center) * 20.0 - iTime * 4.0);
        wave = abs(wave);
        wave *= exp(-length(uv - center) * 3.0);

        col += vec3(0.4, 0.2, 1.0) * wave * 0.3 * mid;
    }

    // глобальний glow
    col = 1.0 - exp(-col * 1.2);

    fragColor = vec4(col, 1.0);
}

        """
