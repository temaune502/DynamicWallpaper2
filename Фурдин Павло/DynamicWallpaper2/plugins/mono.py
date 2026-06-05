from shader_effect import ShaderEffect

class CloudGasEffect(ShaderEffect):
    EFFECT_NAME = "cloud_gas"
    
    def get_fragment_shader(self):
        return """
        #version 330 core
out vec4 fragColor;
uniform float iTime;
uniform vec2 iResolution;
uniform vec3 iAudio; // bass, mid, treble

// Покращений градієнтний шум
vec2 hash(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    vec2 u = f*f*(3.0-2.0*f);
    return mix(mix(dot(hash(i+vec2(0.0,0.0)), f-vec2(0.0,0.0)),
                   dot(hash(i+vec2(1.0,0.0)), f-vec2(1.0,0.0)), u.x),
               mix(dot(hash(i+vec2(0.0,1.0)), f-vec2(0.0,1.0)),
                   dot(hash(i+vec2(1.0,1.0)), f-vec2(1.0,1.0)), u.x), u.y);
}

// Фрактальна сума шуму (FBM - Fractal Brownian Motion)
// Чим більше ітерацій, тим складніша структура
float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    mat2 m = mat2(1.6, 1.2, -1.2, 1.6); // Матриця повороту для кожного шару
    for (int i = 0; i < 8; i++) {
        v += a * noise(p);
        p = m * p;
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
    
    // Створюємо чітке "ядро" хмари в центрі (форму кулі)
    // Використовуємо smoothstep для м'якого переходу до чистого білого по краях
    float dist = length(uv);
    float cloudMask = smoothstep(0.9, 0.0, dist); 
    
    // Плавний, але динамічний рух газу (поєднання iTime та аудіо)
    float speed = iTime * 0.05;
    vec2 p = uv * (3.0 + iAudio.z * 1.5); // Treble додає дрібне масштабування контурів
    p += vec2(speed, speed * 0.5);
    
    // Отримуємо значення шуму, деформоване іншим шумом (Warping)
    float n = fbm(p + fbm(p + speed * 0.2));
    n = n * 0.5 + 0.5; // Нормалізація в [0, 1]
    
    // Накопичувальний ефект від звуку (інтеграція частот):
    // iAudio.x (Bass) додає "маси" і деформації.
    // iAudio.y (Mid) змушує ядро ставати чорним (інтенсивність згущення).
    float audioIntensity = (iAudio.x + iAudio.y * 1.5) * 0.5;
    
    // Створення контрасту: робимо хмару темною в центрі, білою по краях
    float density = n * cloudMask; // Хмара існує тільки в межах маски
    
    // КРИТИЧНО: Високий контраст (затемнення) в центрі.
    // Якщо density висока, brightness падає. audioIntensity затемнює його до 0.1 (jet-black).
    float coreBlackness = 0.1;
    float brightness = 1.0 - (density * (0.8 + audioIntensity * 1.0));
    
    // Обмежуємо колір у сіро-чорний спектр
    brightness = clamp(brightness, coreBlackness, 1.0);
    
    fragColor = vec4(vec3(brightness), 1.0);
}
        """