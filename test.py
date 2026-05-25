# Клас-шаблон (Креслення)
class Shape:
    def __init__(self, name):
        self.name = name
    
    def draw(self):
        pass
       
# Наслідування та Поліморфізм
class Circle(Shape):
    def draw(self):
        return f"Малюємо коло {self.name}"
        

# Створення об'єкта (Екземпляр)
my_circle = Circle(name = "Центральне")
print(my_circle.draw())