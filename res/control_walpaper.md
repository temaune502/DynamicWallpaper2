# Команди керування Dynamic Wallpaper

Цей документ описує всі доступні команди, які можна надсилати на клієнт шпалер через UDP-сервер.

## Формат повідомлення
Всі команди надсилаються як JSON-об'єкт у полі `payload` повідомлення типу `data`.

---

## 1. Керування ефектами

### Перемикання ефекту (`switch_effect`)
Плавно перемикає поточний ефект на інший.
```json
{
  "cmd": "switch_effect",
  "name": "digital_rain"
}
```
**Параметри:**
- `name`: Назва ефекту (наприклад: `glitch`, `matrix`, `digital_rain`, `space`, `plasma`, `stars`, `metaballs`).

### Керування фоном ефекту (`set_show_background`)
Вмикає або вимикає малювання власного фону ефекту (корисно, якщо використовується статична картинка як фон).
```json
{
  "cmd": "set_show_background",
  "show": false
}
```
**Параметри:**
- `show`: `true` (увімкнено) або `false` (вимкнено).

---

## 2. Керування пресетами

### Завантаження пресету (`load_preset`)
Повністю оновлює конфігурацію (ефект, віджети, фон) із файлу в папці `presets/`.
```json
{
  "cmd": "load_preset",
  "name": "matrix_style"
}
```
**Параметри:**
- `name`: Назва файлу в папці `presets` (без або з `.json`).

---

## 3. Керування віджетами

### Оновлення віджета (`update_widget`)
Змінює налаштування конкретного віджета.
```json
{
  "cmd": "update_widget",
  "id": "widget_0",
  "config": {
    "time_format": "HH:mm:ss",
    "x": 50,
    "y": 50,
    "anchor": "top-right"
  }
}
```
**Параметри:**
- `id`: Унікальний ідентифікатор віджета (за замовчуванням `widget_0`, `widget_1` тощо).
- `index`: (Опціонально) Можна використовувати індекс у списку замість ID.
- `config`: Об'єкт з полями, які треба змінити (координати, формат, колір).

---

## 4. Системні команди

### Оновлення загальної конфігурації (`update_config`)
Змінює глобальні параметри програми.
```json
{
  "cmd": "update_config",
  "params": {
    "playlist_interval": 60000
  }
}
```

### Встановлення фону (`set_background`)
Змінює статичний фон (колір або зображення).
```json
{
  "cmd": "set_background",
  "config": {
    "type": "image",
    "path": "C:/path/to/image.jpg"
  }
}
```

### Перезапуск рендеру (`restart_render`)
Скидає фазу анімації до нуля.
```json
{
  "cmd": "restart_render"
}
```

---

## Приклад використання (Python)
```python
from client import UDPClient

tester = UDPClient(name="ADMIN.Controller")
# Надсилаємо команду всім шпалерам
tester.send("WALLPAPER.*", {"cmd": "load_preset", "name": "matrix_style"})
```
