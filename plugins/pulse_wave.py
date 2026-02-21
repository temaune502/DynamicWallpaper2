from shader_effect import ShaderEffect

class PulseWaveEffect(ShaderEffect):
    EFFECT_NAME = "pulse_wave"

    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;

        void main() {
            vec2 uv = gl_FragCoord.xy / iResolution.xy;
            uv = uv * 2.0 - 1.0;  // від -1 до 1
            uv.x *= iResolution.x / iResolution.y;

            // Відстань до центру
            float r = length(uv);

            // Пульсація хвиль
            float waves = sin(10.0 * r - iTime * 4.0);
            waves = abs(waves);

            // Колір залежно від відстані та хвиль
            vec3 col = vec3(0.2, 0.0, 0.5) + vec3(0.5, 0.8, 1.0) * waves;

            // Фейд до країв
            col *= smoothstep(1.2, 0.0, r);

            fragColor = vec4(col, 1.0);
        }
        """
