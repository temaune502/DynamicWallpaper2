from shader_effect import ShaderEffect

class TunnelEffect(ShaderEffect):
    EFFECT_NAME = "tunnel"
    
    def get_fragment_shader(self):
        return """
   #version 330 core

out vec4 fragColor;

uniform float iTime;
uniform vec2 iResolution;
uniform vec3 iAudio; // bass, mid, treble

// 2D rotation
mat2 rot(float a){
    float s = sin(a);
    float c = cos(a);
    return mat2(c,-s,s,c);
}

void main()
{
    vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
    
    float bass   = iAudio.x;
    float mid    = iAudio.y;
    float treble = iAudio.z;

    // Convert to polar
    float r = length(uv);
    float a = atan(uv.y, uv.x);

    // Spiral rotation
    a += iTime * 0.8;
    a += r * 3.0;

    // Tunnel depth illusion
    float depth = 1.0 / (r + 0.15);
    depth += bass * 2.0;

    // Stripe pattern
    float stripes = sin(a * 10.0 + iTime * 4.0);
    stripes = smoothstep(0.2, 0.8, stripes);

    // Radial glow
    float glow = 0.03 / abs(r - 0.3 + sin(iTime + r * 5.0)*0.1);
    glow *= (1.0 + bass * 4.0);

    // Color shifting
    vec3 col = vec3(
        0.5 + 0.5*sin(iTime + depth),
        0.5 + 0.5*sin(iTime + depth + 2.0),
        0.5 + 0.5*sin(iTime + depth + 4.0)
    );

    // Add stripe energy
    col += stripes * vec3(0.0, 0.8, 1.5) * (1.0 + mid * 2.0);

    // Treble sparkles
    col += treble * vec3(1.5, 1.2, 0.8) * glow;

    // Depth fade
    col *= depth * 0.5;

    fragColor = vec4(col, 1.0);
}
        """
