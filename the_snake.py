from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр экрана
SREEN_CENTER = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблок:
APPLE_COLOR = (255, 0, 0)

# Цвет змейки:
SNAKE_COLOR = (0, 255, 0)

# Цвет мух:
FLY_COLOR = (66, 170, 255)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Родительский класс для игровых объектов -
    таких, как "еда" и "змейка".
    """

    def __init__(self) -> None:
        self.position = None
        self.body_color = None  # Для каждого наследника - свой цвет.

    @staticmethod
    def draw_base_rect(position, color):
        """
        Метод для отрисовки базового квадрата:
        яблока, мухи, головы змейки.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """
        Метод для отрисовки объектов, который
        переопределится в классах-наследниках.
        """


class Food(GameObject):
    """
    Родительский класс для игровых объектов типа "еда" -
    таких, как "яблоко" и "муха".
    """

    def __init__(
            self,
            snake_positions=[(SREEN_CENTER)],
            food_positions=[]) -> None:
        super().__init__()
        self.randomize_position(snake_positions, food_positions)

    def randomize_position(self, snake_positions, food_positions):
        """Метод, определяющий случайные координаты "еды"."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

            if self.position not in snake_positions + food_positions:
                return self.position

    def draw(self):
        """Метод для отрисовки "еды"."""
        self.draw_base_rect(self.position, self.body_color)


class Apple(Food):
    """
    Класс, описывающий игровой объект "яблоко".
    Если змейка съела яблоко, её длина увеличивается.
    """

    def __init__(self, snake_positions=[(SREEN_CENTER)], food_positions=[]):
        super().__init__(snake_positions, food_positions)
        self.body_color = APPLE_COLOR


class Fly(Food):
    """
    Класс, описывающий игровой объект "муха".
    Если змейка съела муху, длина уменьшается.
    """

    def __init__(self, snake_positions=[(SREEN_CENTER)], food_positions=[]):
        super().__init__(snake_positions, food_positions)
        self.body_color = FLY_COLOR


class Snake(GameObject):
    """
    Класс, описывающий игровой объект "змейка".
    Змейка перемещается по полю, стараясь съесть как можно больше яблок,
    как можно меньше мух
    и избежать столкновения с собственным хвостом.
    """

    def __init__(self):
        super().__init__()
        self.positions = None
        self.length = None
        self.diretion = RIGHT
        self.reset()
        self.next_direction = None
        self.body_color = SNAKE_COLOR

    def reset(self):
        """Метод, который сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [SREEN_CENTER]
        self.last = None
        self.direction = self.randomize_direction()

    def randomize_direction(self):
        """
        Метод для выбора случайного направления
        движения змейки в начале игры.
        """
        return choice([RIGHT, LEFT, UP, DOWN])

    def update_direction(self, next_direction=None):
        """Метод, который обновляет направление движения змейки."""
        if next_direction:
            self.direction = next_direction
            self.next_direction = None

    def move(self):
        """
        Метод, который обновляет позицию змейки,
        добавляет новую голову в начало списка positions
        и удаляет последний элемент этого списка,
        если длина змейки не увеличилась.
        """
        head_x, head_y = self.get_head_position
        dir_x, dir_y = self.direction
        new_head_position = (
            (head_x + (dir_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (dir_y * GRID_SIZE)) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, (new_head_position))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    @property
    def get_head_position(self):
        """Метод, который возвращает позицию головы змейки."""
        return self.positions[0]

    def draw(self):
        """Метод для отрисовки объекта "змейка"."""
        for position in self.positions[:-1]:
            self.draw_base_rect(position, self.body_color)

        # Отрисовка головы змейки.
        self.draw_base_rect(self.get_head_position, self.body_color)

        # Затирание хвоста.
        if self.last:
            self.erase_tail_segment(self.last)

    def erase_tail_segment(self, segment):
        """Метод для затирания хвоста."""
        last_rect = pg.Rect(segment, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """Метод обрабатывает нажатие клавиш пользователем."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.update_direction(DOWN)
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.update_direction(RIGHT)


def main():
    """Здесь инициализируется игра."""
    pg.init()

    snake = Snake()
    apple = Apple(snake_positions=snake.positions, food_positions=[])
    fly = Fly(snake_positions=snake.positions, food_positions=[])

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        apple.draw()
        snake.draw()
        fly.draw()
        snake.move()
        pg.display.update()

        # Заголовок окна игрового поля:
        pg.display.set_caption(f'Текущий счёт: {snake.length}')

        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions, [fly.position])
        elif snake.get_head_position == fly.position and snake.length > 1:
            snake.length -= 1
            snake.erase_tail_segment(snake.positions.pop())
            fly.randomize_position(snake.positions, [apple.position])
        elif snake.get_head_position in snake.positions[4:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()


if __name__ == '__main__':
    main()
