import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import math
import random
import sys
from dataclasses import dataclass
from enum import Enum

class Equipment(Enum):
    LEFT = 1
    RIGHT = 2
    MIDDLE = 3
    RANDOM = 4

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Settings:
    task: int
    start: int
    end: int
    accuracy: int
    equipment: Equipment

class CalculatorUtils:
    @staticmethod
    def get_formula_value_at(x: int, settings: Settings) -> int:
        match settings.task:
            case 2:  return math.e ** x
            case 10: return math.e ** (2 * x)
            case 22: return x ** 3
            case 26: return math.e ** (2 * x)
            case 31: return 3 ** x 
            case _:  raise Exception('Unsupported task')

    @staticmethod
    def calculate_graph_points(settings: Settings) -> list[Point]:
        points = []

        delta_x = CalculatorUtils.calculate_delta_x(settings)
        for i in range(settings.accuracy + 1):
            x = settings.start + i * delta_x
            points.append(Point(x, CalculatorUtils.get_formula_value_at(x, settings)))

        return points
    
    @staticmethod
    def calculate_integral_sum(settings: Settings) -> float:
        integral_sum = 0

        delta_x = CalculatorUtils.calculate_delta_x(settings)
        delta_x_shift = CalculatorUtils.calculate_integral_shape_shift(settings)
        for i in range(settings.accuracy + 1):
            x = settings.start + i * delta_x
            integral_sum += delta_x * CalculatorUtils.get_formula_value_at(x, settings)

        match settings.equipment:
            case Equipment.LEFT:   integral_sum -= CalculatorUtils.get_formula_value_at(settings.start, settings) * delta_x
            case Equipment.RIGHT:  integral_sum -= CalculatorUtils.get_formula_value_at(settings.end, settings) * delta_x
            case Equipment.MIDDLE: integral_sum -= ((CalculatorUtils.get_formula_value_at(settings.start, settings) + CalculatorUtils.get_formula_value_at(settings.end, settings)) / 2) * delta_x
            case Equipment.RANDOM: integral_sum -= CalculatorUtils.get_formula_value_at(settings.start, settings) * delta_x_shift + \
                                                   CalculatorUtils.get_formula_value_at(settings.end, settings) * (delta_x - delta_x_shift)

        return integral_sum

    @staticmethod
    def calculate_delta_x(settings: Settings) -> int:
        return (settings.end - settings.start) / settings.accuracy

    @staticmethod
    def calculate_integral_shape_shift(settings: Settings) -> int:
        delta_x = CalculatorUtils.calculate_delta_x(settings)
        match settings.equipment:
            case Equipment.LEFT:   return 0
            case Equipment.RIGHT:  return delta_x
            case Equipment.MIDDLE: return delta_x / 2
            case Equipment.RANDOM: return random.uniform(0, delta_x)
            case _:                raise Exception('Unsupported equipment')

class Drawer:
    def __init__(self, settings: Settings):
        self.__settings = settings
        self.__points = CalculatorUtils.calculate_graph_points(settings)
        _, self.__axes = plt.subplots()

        # accuracy
        self.accuracy_box = plt.axes([0.7, 0.08, 0.2, 0.05])
        self.accuracy_text_box = TextBox(self.accuracy_box, 'Accuracy', initial=str(settings.accuracy))
        self.accuracy_text_box.on_submit(self.on_accuracy_change)

        # task
        self.task_box = plt.axes([0.7, 0.01, 0.2, 0.05])
        self.task_text_box = TextBox(self.task_box, 'Task', initial=str(settings.task))
        self.task_text_box.on_submit(self.on_task_change)

        # start
        self.start_box = plt.axes([0.15, 0.08, 0.2, 0.05])
        self.start_text_box = TextBox(self.start_box, 'Start', initial=str(settings.start))
        self.start_text_box.on_submit(self.on_start_change)

        # end
        self.end_box = plt.axes([0.15, 0.01, 0.2, 0.05])
        self.end_text_box = TextBox(self.end_box, 'End', initial=str(settings.end))
        self.end_text_box.on_submit(self.on_end_change)
    
    def on_accuracy_change(self, text):
        try:
            new_accuracy = int(text)
            self.__settings.accuracy = new_accuracy
            self.update()
        except ValueError:
            pass

    def on_task_change(self, text):
        try:
            new_task = int(text)
            self.__settings.task = new_task
            self.update()
        except ValueError:
            pass

    def on_start_change(self, text):
        try:
            new_start = int(text)
            self.__settings.start = new_start
            self.update()
        except ValueError:
            pass

    def on_end_change(self, text):
        try:
            new_end = int(text)
            self.__settings.end = new_end
            self.update()
        except ValueError:
            pass

    def on_equipment_change(self, text):
        try:
            new_equipment = int(text)
            self.__settings.equipment = Equipment(new_equipment)
            self.update()
        except ValueError:
            pass

    def update(self):
        self.__points = CalculatorUtils.calculate_graph_points(self.__settings)
        self.draw()

    def create_integral_shape(self) -> list[plt.Rectangle]:
        rectangles = []

        delta_x = CalculatorUtils.calculate_delta_x(self.__settings)
        delta_x_shift = CalculatorUtils.calculate_integral_shape_shift(self.__settings)
        for point in self.__points:
            rectangles.append(self.create_integral_rectangle(point, delta_x, delta_x_shift))

        return rectangles

    def create_integral_rectangle(self, point: Point, delta_x: int, delta_x_shift: int) -> plt.Rectangle:
        return plt.Rectangle((point.x - delta_x_shift, 0), delta_x, point.y, edgecolor='red', facecolor='red')

    def get_formula_text(self) -> str:
        match self.__settings.task:
            case 2:  return r'$y = e^x$'
            case 10: return r'$y = e^{2x}$'
            case 22: return r'$y = x^3$'
            case 26: return r'$y = e^{2x}$'
            case 31: return r'$y = 3^x$'
            case _:  raise Exception('Unsupported task')

    def create_window(self) -> None:
        self.__axes.set_title(self.get_formula_text(), fontsize=20)
        self.__axes.set_xlim(self.__settings.start, self.__settings.end)
        self.__axes.set_ylim(min(point.y for point in self.__points) - 1, max(point.y for point in self.__points) + 1)
        self.__axes.grid(linestyle="--", alpha=0.5, zorder=0)
        self.__axes.set_position([0.1, 0.3, 0.8, 0.6])

    def draw_integral_sum(self) -> None:
        rectangles = self.create_integral_shape()
        for rectangle in rectangles:
            self.__axes.add_patch(rectangle)

    def draw_graph(self) -> None:
        settings_for_graph = Settings(
            task = self.__settings.task,
            start = self.__settings.start,
            end = self.__settings.end,
            accuracy = 1000000,
            equipment = Equipment.RANDOM
        )
        points = CalculatorUtils.calculate_graph_points(settings_for_graph)
        self.__axes.plot([point.x for point in points], [point.y for point in points], color='black', linewidth=0.8)
        
    def draw(self) -> None:
        self.__axes.clear()
        self.draw_graph()
        self.draw_integral_sum()
        self.create_window()

def read_settings(args: list[str]) -> Settings:
    settings = Settings(
        task = 2,
        start = 0,
        end = 1,
        accuracy = 10,
        equipment = Equipment.MIDDLE
    )
    return settings

if __name__ == '__main__':
    Drawer(read_settings(sys.argv)).draw()
    print(CalculatorUtils.calculate_integral_sum(read_settings(sys.argv)))
    plt.show()
