from shader_effect import ShaderEffect

class PaperGridEffect(ShaderEffect):
    EFFECT_NAME = "paper_grid"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        uniform vec3 iAudio; // bass, mid, treble

        void main() {
            // Нормалізовані координати (центричні)
            vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
            
            // Базова "біла" тема
            vec3 bgColor = vec3(0.95); // Світло-сірий фон (майже білий)
            vec3 gridColor = vec3(0.1); // Темно-сірі лінії (майже чорні)
            
            // Динаміка сітки
            float zoom = 5.0 + iAudio.x * 2.0; // Bass збільшує масштаб
            vec2 grid = fract(uv * zoom + iTime * 0.2);
            
            // Малювання ліній сітки
            float thickness = 0.02 + iAudio.y * 0.03; // Mid потовщує лінії
            float lines = smoothstep(0.0, thickness, grid.x) * smoothstep(1.0, 1.0 - thickness, grid.x);
            lines += smoothstep(0.0, thickness, grid.y) * smoothstep(1.0, 1.0 - thickness, grid.y);
            
            // Додаємо шум/акцент від Treble
            float noise = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
            float spark = step(0.995, noise) * iAudio.z;
            
            // Змішуємо кольори
            vec3 col = mix(bgColor, gridColor, clamp(lines, 0.0, 1.0));
            col += spark; // Білі "іскри" на сітці
            
            // Інверсія для високого контрасту (щоб лінії були темними на світлому)
            fragColor = vec4(col, 1.0);
        }
        """