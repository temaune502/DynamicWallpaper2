from shader_effect import ShaderEffect

class QxxxxxxxxxxxxxxxxxxxEffect(ShaderEffect):
    EFFECT_NAME = "xxxxxxxxxxxxxxxxxxx"
    
    def get_fragment_shader(self):
        return """
#version 120
#define M_PI 3.1415926535897932384626433832795

uniform sampler2D texture;
uniform float time;
uniform float yaw;
uniform float pitch;
uniform float alpha;

varying vec3 position;

float hash(float n){
    return fract(sin(n) * 43758.5453);
}

void main()
{
    vec4 col = vec4(0.047, 0.035, 0.063, 1.0);

    vec3 dir = normalize(-position);

    float sb = sin(pitch);
    float cb = cos(pitch);
    dir = vec3(dir.x, dir.y * cb - dir.z * sb, dir.y * sb + dir.z * cb);

    float sa = sin(-yaw);
    float ca = cos(-yaw);
    dir = vec3(dir.z * sa + dir.x * ca, dir.y, dir.z * ca - dir.x * sa);

    float u = 0.5 + atan(dir.z / dir.x) / (2.0 * M_PI);
    float v = 0.5 + asin(dir.y) / M_PI;

    for(int i = 0; i < 8; i++)
    {
        float fi = float(i);
        float scale = 3.0 + fi * 0.7;

        float r1 = hash(fi*3.1);
        float r2 = hash(fi*7.3);

        vec2 uv = vec2(
            u*scale + r1,
            (v + time*0.0001)*scale*0.6 + r2
        );

        vec4 tcol = texture2D(texture, uv);

        float fade = 1.0 - smoothstep(0.2,0.5,abs(v-0.5));

        float a = tcol.r * (0.08 + 0.4/(fi+1.0)) * fade;

        vec3 layerColor = vec3(
            r1*0.6 + 0.2,
            r2*0.5 + 0.4,
            hash(fi*11.0)*0.5 + 0.5
        );

        col.rgb = col.rgb * (1.0 - a) + layerColor * a;
    }

    float br = clamp(2.5*gl_FragCoord.w + alpha,0.0,1.0);

    col.rgb = col.rgb * br + vec3(0.047,0.035,0.063) * (1.0-br);
    col.rgb = clamp(col.rgb * (1.0 + alpha*3.0), 0.0, 1.0);

    gl_FragColor = vec4(col.rgb,1.0);
}
        """
