import numpy as np
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from effects import BaseEffect


class StarfieldEffect(BaseEffect):
    EFFECT_NAME = "starfield"

    def __init__(self):
        super().__init__()
        self.num_stars = 200
        self.speed_factor = 1.0
        self.stars = None  # shape (N, 3): x, y, size
        self._init_stars(1920, 1080)

    def _init_stars(self, w, h):
        self.stars = np.empty((self.num_stars, 3), dtype=np.float32)
        self.stars[:, 0] = np.random.uniform(0, w, self.num_stars)  # x
        self.stars[:, 1] = np.random.uniform(0, h, self.num_stars)  # y
        self.stars[:, 2] = np.random.uniform(1, 4, self.num_stars)  # size

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 50,
                "max": 1000,
                "default": 200,
                "label": "Star Count"
            },
            "speed": {
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 1.0,
                "label": "Speed Multiplier"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.num_stars = int(config['count'])
            self._init_stars(1920, 1080)
        if 'speed' in config:
            self.speed_factor = float(config['speed'])

    def draw(self, p, w, h, phase):

        if self.stars is None or len(self.stars) != self.num_stars:
            self._init_stars(w, h)

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 5, 15))

        # Audio Reactivity
        audio_boost = 0.0
        if self.audio_data:
            audio_boost = self.audio_data.get('bass', 0.0) * 5.0 # Boost speed on bass

        # 🔥 Векторне оновлення X
        self.stars[:, 0] = (self.stars[:, 0] +
                            self.stars[:, 2] * (self.speed_factor + audio_boost)) % w

        # 🔥 Векторний розрахунок alpha
        alpha = 150 + 105 * np.sin(
            phase * 10 + self.stars[:, 0] * 0.01
        )

        alpha = alpha.astype(np.int32)

        p.setPen(Qt.NoPen)

        # Тут лишається цикл тільки для drawEllipse
        # це вже обмеження QPainter
        for i in range(self.num_stars):
            size = self.stars[i, 2]
            p.setBrush(QColor(255, 255, 255, int(alpha[i])))
            p.drawEllipse(
                int(self.stars[i, 0]),
                int(self.stars[i, 1]),
                int(size),
                int(size)
            )
