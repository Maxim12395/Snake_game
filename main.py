from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition, TransitionBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Rectangle, Color, InstructionGroup, Point
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from random import randint, random
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.vector import Vector

from settings import load_settings, save_settings

from levels import LEVELS

from kivy.utils import platform  # Для кнопок на телефоне

from database import init_db, update_score, get_or_create_profile, get_top_players, validate_user, create_user, \
    get_player_score, get_player_rank

print("TEST:", get_top_players(limit=10))

from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle
from kivy.animation import Animation
from kivy.properties import NumericProperty

from kivy.logger import Logger

from kivy.properties import BooleanProperty

from kivy.resources import resource_find

GRID_SIZE = 20
SPEED = 0.15
PLAYER_NAME = ""

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound_click = SoundLoader.load(resource_find('sounds/click.wav'))
        self.setup_ui()

    def on_enter(self):
        # Применяем текущую тему при входе на экран
        self.apply_theme()

    def setup_ui(self):
        self.settings = load_settings()
        self.clear_widgets()

        # Основной контейнер с прокруткой
        scroll = ScrollView(size_hint=(1, 1))
        main_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=Window.height * 1.5,  # Достаточно места для прокрутки
            spacing=15,
            padding=30
        )

        # Заголовок (фиксированная высота)
        title = EmojiLabel(
            text="⚙️ Настройки",
            font_size=32,
            size_hint=(1, None),
            height=60
        )
        main_layout.add_widget(title)

        # Раздел "Переключатели"
        section_label = Label(
            text="Переключатели:",
            font_size=24,
            size_hint=(1, None),
            height=40
        )
        main_layout.add_widget(section_label)

        # Стиль переключателей
        switch_style_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50
        )
        switch_style_layout.add_widget(Label(
            text="Ретро-стиль переключателей:",
            font_size=20,
            size_hint=(0.7, 1)
        ))

        self.retro_style_switch = Switch(
            active=self.settings.get("retro_style", False),
            size_hint=(0.2, None),
            height=50,
            pos_hint={'center_y': 0.5}
        )
        switch_style_layout.add_widget(self.retro_style_switch)
        switch_style_layout.add_widget(Label(
            text="Вкл" if self.settings.get("retro_style", False) else "Выкл",
            font_size=20,
            size_hint=(0.1, 1)
        ))
        main_layout.add_widget(switch_style_layout)

        # Звуковые эффекты
        sound_effects_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50
        )
        sound_effects_layout.add_widget(Label(
            text="Звук:",
            font_size=20,
            size_hint=(0.7, 1)
        ))

        self.sound_effects_switch = Switch(
            active=self.settings.get("sound_effects", True),
            size_hint=(0.2, None),
            height=50,
            pos_hint={'center_y': 0.5}
        )
        sound_effects_layout.add_widget(self.sound_effects_switch)
        sound_effects_layout.add_widget(Label(
            text="Вкл" if self.settings.get("sound_effects", True) else "Выкл",
            font_size=20,
            size_hint=(0.1, 1)
        ))
        main_layout.add_widget(sound_effects_layout)

        # Раздел "Цветовые схемы"
        color_scheme_label = Label(
            text="Цветовые схемы:",
            font_size=24,
            size_hint=(1, None),
            height=40
        )
        main_layout.add_widget(color_scheme_label)

        # Выбор темы
        theme_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50
        )
        theme_layout.add_widget(Label(
            text="Тема:",
            font_size=20,
            size_hint=(0.4, 1)
        ))

        self.theme_spinner = Spinner(
            text=self.settings["theme"],
            values=["Классическая", "Тёмная", "Ретро"],
            size_hint=(0.6, None),
            height=50,
            font_size=20
        )
        theme_layout.add_widget(self.theme_spinner)
        main_layout.add_widget(theme_layout)

        # Превью темы
        self.theme_preview = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=150,
            padding=10,
            spacing=10
        )
        self.update_theme_preview()
        main_layout.add_widget(self.theme_preview)

        # Кнопки управления
        btn_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint=(1, None),
            height=150
        )

        logout_btn = Button(
            text="Выйти из профиля",
            size_hint=(1, None),
            height=70,
            font_size=20
        )
        logout_btn.bind(on_release=self.logout)

        back_btn = Button(
            text="Назад",
            size_hint=(1, None),
            height=70,
            font_size=20
        )
        back_btn.bind(on_release=self.save_and_return)

        btn_layout.add_widget(logout_btn)
        btn_layout.add_widget(back_btn)
        main_layout.add_widget(btn_layout)

        scroll.add_widget(main_layout)
        self.add_widget(scroll)

        # Привязка событий
        self.retro_style_switch.bind(active=self.on_retro_style_toggle)
        self.sound_effects_switch.bind(active=self.on_sound_effects_toggle)
        self.theme_spinner.bind(text=self.on_theme_select)

        # Добавьте этот блок в setup_ui()
        music_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50
        )
        music_layout.add_widget(Label(
            text="Фоновая музыка:",
            font_size=20,
            size_hint=(0.7, 1)
        ))

        self.music_switch = Switch(
            active=self.settings.get("background_music", True),
            size_hint=(0.2, None),
            height=50,
            pos_hint={'center_y': 0.5}
        )
        music_layout.add_widget(self.music_switch)
        music_layout.add_widget(Label(
            text="Вкл" if self.settings.get("background_music", True) else "Выкл",
            font_size=20,
            size_hint=(0.1, 1)
        ))
        main_layout.add_widget(music_layout)

        # Привязка события
        self.music_switch.bind(active=self.on_music_toggle)

    def on_music_toggle(self, instance, value):
        if self.sound_effects_switch.active and value:
            self.sound_click.play()
        self.settings["background_music"] = value
        # Обновляем текст
        for child in instance.parent.children:
            if isinstance(child, Label):
                child.text = "Вкл" if value else "Выкл"

        # Контролируем музыку
        app = App.get_running_app()
        if value:
            app.start_menu_music()
        else:
            app.stop_menu_music()

    def update_theme_preview(self):
        self.theme_preview.clear_widgets()
        theme = self.settings["theme"]

        # Цвета для превью в зависимости от темы
        if theme == "Классическая":
            bg_color = (1, 1, 1, 1)  # Белый фон
            text_color = (0, 0, 0, 1)  # Черный текст
            btn_color = (0.9, 0.9, 0.9, 1)  # Светло-серые кнопки
        elif theme == "Тёмная":
            bg_color = (0.1, 0.1, 0.1, 1)  # Темный фон
            text_color = (1, 1, 1, 1)  # Белый текст
            btn_color = (0.3, 0.3, 0.3, 1)  # Темно-серые кнопки
        else:  # Ретро
            bg_color = (0.1, 0.1, 0.2, 1)  # Темно-синий фон
            text_color = (0.8, 0.8, 0.1, 1)  # Желтый текст
            btn_color = (0.3, 0.1, 0.3, 1)  # Фиолетовые кнопки

        # Фон превью
        with self.theme_preview.canvas.before:
            Color(*bg_color)
            Rectangle(pos=self.theme_preview.pos, size=self.theme_preview.size)

        # Пример элементов интерфейса
        example_label = Label(
            text="Пример текста",
            color=text_color,
            font_size=20,
            size_hint=(1, 0.3)
        )

        example_btn = Button(
            text="Пример кнопки",
            background_color=btn_color,
            color=text_color,
            size_hint=(1, 0.4)
        )

        example_switch = Switch(
            active=True,
            size_hint=(0.5, 0.3),
            pos_hint={'center_x': 0.5}
        )

        self.theme_preview.add_widget(example_label)
        self.theme_preview.add_widget(example_btn)
        self.theme_preview.add_widget(example_switch)

    def on_retro_style_toggle(self, instance, value):
        if self.sound_effects_switch.active and value:
            self.sound_click.play()
        self.settings["retro_style"] = value
        # Обновляем текст рядом с переключателем
        for child in instance.parent.children:
            if isinstance(child, Label):
                child.text = "Вкл" if value else "Выкл"

    def on_sound_effects_toggle(self, instance, value):
        if value:  # Если звуки включаются, проигрываем щелчок
            self.sound_click.play()
        self.settings["sound_effects"] = value
        # Обновляем текст рядом с переключателем
        for child in instance.parent.children:
            if isinstance(child, Label):
                child.text = "Вкл" if value else "Выкл"

    def on_theme_select(self, instance, value):
        if self.sound_effects_switch.active:
            self.sound_click.play()
        self.settings["theme"] = value
        self.update_theme_preview()
        self.apply_theme()

    def apply_theme(self):
        theme = self.settings["theme"]
        Window.clearcolor = (0.1, 0.1, 0.1, 1) if theme == "Тёмная" else (1, 1, 1, 1) if theme == "Классическая" else (
        0.1, 0.1, 0.2, 1)

        text_color = (1, 1, 1, 1) if theme == "Тёмная" else (0, 0, 0, 1) if theme == "Классическая" else (
        0.8, 0.8, 0.1, 1)
        btn_color = (0.3, 0.3, 0.3, 1) if theme == "Тёмная" else (0.9, 0.9, 0.9, 1) if theme == "Классическая" else (
        0.3, 0.1, 0.3, 1)

        for widget in self.walk():
            if isinstance(widget, Label):
                widget.color = text_color
            elif isinstance(widget, Button):
                widget.background_color = btn_color
                widget.color = text_color

    def save_and_return(self, instance):
        self.settings["retro_style"] = self.retro_style_switch.active
        self.settings["sound_effects"] = self.sound_effects_switch.active
        self.settings["theme"] = self.theme_spinner.text
        save_settings(self.settings)

        # Применяем настройки ко всему приложению
        App.get_running_app().apply_theme(self.settings["theme"])
        self.manager.current = 'menu'

    def logout(self, instance):
        global PLAYER_NAME
        PLAYER_NAME = None
        self.manager.current = 'login'


class EndlessSnakeGame(Widget):
    def __init__(self, score_label, **kwargs):
        super().__init__(**kwargs)
        self.score_label = score_label
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = (10, 10)
        self.direction = (1, 0)
        self.paused = False
        self.obstacles = []
        self.speed = SPEED
        self.particles = []  # Для эффектов частиц
        self.food_animation = None
        self.food_type = 0  # Тип еды (0-яблоко, 1-груша и т.д.)

        Clock.schedule_interval(self.update, self.speed)
        Window.bind(on_key_down=self.on_key_down)
        self.spawn_food()
        self.init_effects()  # Инициализация эффектов
        self.draw()

        self.eat_sound = SoundLoader.load(resource_find('sounds/eat.wav'))  # Добавляем загрузку звука


    def init_effects(self):
        # Эффект сетки
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.1)
            for x in range(0, int(self.width), GRID_SIZE):
                Line(points=[x, 0, x, self.height], width=0.5)
            for y in range(0, int(self.height), GRID_SIZE):
                Line(points=[0, y, self.width, y], width=0.5)

    def on_touch_up(self, touch):
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y
        if abs(dx) > abs(dy):
            self.direction = (1, 0) if dx > 0 else (-1, 0)
        else:
            self.direction = (0, 1) if dy > 0 else (0, -1)

    def on_key_down(self, _, key, *args):
        if key == 273:
            self.direction = (0, 1)
        elif key == 274:
            self.direction = (0, -1)
        elif key == 275:
            self.direction = (1, 0)
        elif key == 276:
            self.direction = (-1, 0)

    def update(self, dt):
        if self.paused:
            return

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Добавляем частицы следа
        self.add_trail_particles(head)

        if (new_head in self.snake or
                not (0 <= new_head[0] < self.width // GRID_SIZE) or
                not (0 <= new_head[1] < self.height // GRID_SIZE)):
            score = len(self.snake)
            update_score(PLAYER_NAME, score)
            self.reset()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            if self.eat_sound:  # Проигрываем звук, если он загрузился
                self.eat_sound.play()
            self.add_eat_particles() #Эффект поедания
            self.spawn_food()
        else:
            self.snake.pop()

        self.update_particles()  # Обновляем частицы
        self.draw()
        self.score_label.text = f"Счёт: {len(self.snake)}"

    def add_trail_particles(self, pos):
        # Добавляем частицы следа
        for _ in range(2):
            self.particles.append({
                'pos': (pos[0] * GRID_SIZE + GRID_SIZE / 2, pos[1] * GRID_SIZE + GRID_SIZE / 2),
                'size': randint(3, 6),
                'color': (0.2, 0.8, 0.2, 0.7),
                'life': randint(10, 20)
            })

    def add_eat_particles(self):
        # Эффект вспышки при поедании еды
        for _ in range(15):
            self.particles.append({
                'pos': (self.food[0] * GRID_SIZE + GRID_SIZE / 2, self.food[1] * GRID_SIZE + GRID_SIZE / 2),
                'size': randint(5, 10),
                'color': (1, 0.2, 0.2, 1) if self.food_type == 0 else (1, 0.8, 0.2, 1),
                'life': randint(15, 30),
                'velocity': Vector(randint(-3, 3), randint(-3, 3))
            })

    def update_particles(self):
        # Обновляем и удаляем старые частицы
        new_particles = []
        for p in self.particles:
            p['life'] -= 1
            if 'velocity' in p:
                p['pos'] = (p['pos'][0] + p['velocity'][0], p['pos'][1] + p['velocity'][1])
            if p['life'] > 0:
                new_particles.append(p)
        self.particles = new_particles

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def reset(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.score_label.text = "Счёт: 3"
        self.particles = []

    def spawn_food(self):
        while True:
            new_food = (randint(0, self.width // GRID_SIZE - 1),
                        randint(0, self.height // GRID_SIZE - 1))
            if new_food not in self.snake:
                self.food = new_food
                self.food_type = randint(0, 1)  # Случайный тип еды
                break

    def draw(self):
        self.canvas.clear()
        self.init_effects()  # Перерисовываем сетку

        with self.canvas:
            # Рисуем змейку с градиентом
            for i, (x, y) in enumerate(self.snake):
                ratio = i / len(self.snake)
                Color(0.2, 1 - ratio * 0.5, 0.2, 1)
                Rectangle(
                    pos=(x * GRID_SIZE, y * GRID_SIZE),
                    size=(GRID_SIZE, GRID_SIZE)
                )
                # Голова с глазами
                if i == 0:
                    eye_size = GRID_SIZE // 5
                    Color(1, 1, 1, 1)
                    # Глаза в зависимости от направления
                    if self.direction[0] == 1:  # Вправо
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE - 2 * eye_size, y * GRID_SIZE + GRID_SIZE // 2),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE - 2 * eye_size, y * GRID_SIZE + GRID_SIZE // 3),
                            size=(eye_size, eye_size)
                        )
                    elif self.direction[0] == -1:  # Влево
                        Rectangle(
                            pos=(x * GRID_SIZE + eye_size, y * GRID_SIZE + GRID_SIZE // 2),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + eye_size, y * GRID_SIZE + GRID_SIZE // 3),
                            size=(eye_size, eye_size)
                        )
                    elif self.direction[1] == 1:  # Вверх
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE // 3, y * GRID_SIZE + GRID_SIZE - 2 * eye_size),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + 2 * GRID_SIZE // 3, y * GRID_SIZE + GRID_SIZE - 2 * eye_size),
                            size=(eye_size, eye_size)
                        )
                    else:  # Вниз
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE // 3, y * GRID_SIZE + eye_size),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + 2 * GRID_SIZE // 3, y * GRID_SIZE + eye_size),
                            size=(eye_size, eye_size)
                        )

            # Рисуем еду
            self.draw_food()

            # Рисуем частицы
            for p in self.particles:
                alpha = p['life'] / 20 * p['color'][3] if 'life' in p else p['color'][3]
                Color(p['color'][0], p['color'][1], p['color'][2], alpha)
                Rectangle(
                    pos=(p['pos'][0] - p['size'] / 2, p['pos'][1] - p['size'] / 2),
                    size=(p['size'], p['size'])
                )

    def draw_food(self):
        fx, fy = self.food
        if not self.food_animation:
            self.food_animation = Animation(size=(GRID_SIZE * 1.3, GRID_SIZE * 1.3), duration=0.5) \
                                  + Animation(size=(GRID_SIZE, GRID_SIZE), duration=0.5)
            self.food_animation.repeat = True

        with self.canvas:
            # Разные виды еды
            if self.food_type == 0:  # Яблоко
                Color(1, 0.2, 0.2, 1)
                Rectangle(pos=(fx * GRID_SIZE, fy * GRID_SIZE), size=(GRID_SIZE, GRID_SIZE))
                # Листик
                Color(0.2, 0.8, 0.2, 1)
                Rectangle(
                    pos=(fx * GRID_SIZE + GRID_SIZE // 3, fy * GRID_SIZE + GRID_SIZE - GRID_SIZE // 4),
                    size=(GRID_SIZE // 3, GRID_SIZE // 4)
                )
            else:  # Груша
                Color(1, 0.8, 0.2, 1)
                Rectangle(pos=(fx * GRID_SIZE, fy * GRID_SIZE), size=(GRID_SIZE, GRID_SIZE))
                # Черенок
                Color(0.4, 0.2, 0.1, 1)
                Rectangle(
                    pos=(fx * GRID_SIZE + GRID_SIZE // 2 - 1, fy * GRID_SIZE + GRID_SIZE - GRID_SIZE // 5),
                    size=(2, GRID_SIZE // 5)
                )

            # Блики на еде
            Color(1, 1, 1, 0.8)
            Rectangle(
                pos=(fx * GRID_SIZE + GRID_SIZE // 3, fy * GRID_SIZE + GRID_SIZE // 1.5),
                size=(GRID_SIZE // 4, GRID_SIZE // 4)
            )

    def set_direction(self, dx, dy):
        self.direction = (dx, dy)


class SnakeGame(Widget):
    def __init__(self, score_label, **kwargs):
        super().__init__(**kwargs)
        self.score_label = score_label
        self.level = 0
        self.goal = LEVELS[self.level]['goal']
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = (10, 10)
        self.direction = (1, 0)
        self.paused = False
        self.obstacles = LEVELS[self.level]['obstacles']
        self.speed = LEVELS[self.level]['speed']
        self.particles = []  # Для эффектов частиц
        self.food_animation = None
        self.food_type = 0  # Тип еды (0-яблоко, 1-груша)

        Clock.schedule_interval(self.update, self.speed)
        Window.bind(on_key_down=self.on_key_down)
        self.spawn_food()
        self.init_effects()
        self.draw()

        self.eat_sound = SoundLoader.load(resource_find('sounds/eat.wav'))  # Добавляем загрузку звука

    def init_effects(self):
        # Эффект сетки
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.1)
            for x in range(0, int(self.width), GRID_SIZE):
                Line(points=[x, 0, x, self.height], width=0.5)
            for y in range(0, int(self.height), GRID_SIZE):
                Line(points=[0, y, self.width, y], width=0.5)

    def on_touch_up(self, touch):
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y
        if abs(dx) > abs(dy):
            self.direction = (1, 0) if dx > 0 else (-1, 0)
        else:
            self.direction = (0, 1) if dy > 0 else (0, -1)

    def on_key_down(self, _, key, *args):
        if key == 273:
            self.direction = (0, 1)
        elif key == 274:
            self.direction = (0, -1)
        elif key == 275:
            self.direction = (1, 0)
        elif key == 276:
            self.direction = (-1, 0)

    def update(self, dt):
        if self.paused:
            return

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Добавляем частицы следа
        self.add_trail_particles(head)

        if (new_head in self.snake or
                new_head in self.obstacles or
                not (0 <= new_head[0] < self.width // GRID_SIZE) or
                not (0 <= new_head[1] < self.height // GRID_SIZE)):
            score = len(self.snake)
            update_score(PLAYER_NAME, score)
            self.reset()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            if self.eat_sound:  # Проигрываем звук, если он загрузился
                self.eat_sound.play()
            self.add_eat_particles() #Эффект поедания
            self.spawn_food()
            if len(self.snake) >= self.goal:
                self.advance_level()
        else:
            self.snake.pop()

        self.update_particles()  # Обновляем частицы
        self.draw()
        self.score_label.text = f"Счёт: {len(self.snake)}"

    def add_trail_particles(self, pos):
        # Добавляем частицы следа
        for _ in range(2):
            self.particles.append({
                'pos': (pos[0] * GRID_SIZE + GRID_SIZE/2, pos[1] * GRID_SIZE + GRID_SIZE/2),
                'size': randint(3, 6),
                'color': (0.2, 0.8, 0.2, 0.7),
                'life': randint(10, 20)
            })

    def add_eat_particles(self):
        # Эффект вспышки при поедании еды
        for _ in range(15):
            self.particles.append({
                'pos': (self.food[0] * GRID_SIZE + GRID_SIZE/2, self.food[1] * GRID_SIZE + GRID_SIZE/2),
                'size': randint(5, 10),
                'color': (1, 0.2, 0.2, 1) if self.food_type == 0 else (1, 0.8, 0.2, 1),
                'life': randint(15, 30),
                'velocity': Vector(randint(-3, 3), randint(-3, 3))
            })

    def update_particles(self):
        # Обновляем и удаляем старые частицы
        new_particles = []
        for p in self.particles:
            p['life'] -= 1
            if 'velocity' in p:
                p['pos'] = (p['pos'][0] + p['velocity'][0], p['pos'][1] + p['velocity'][1])
            if p['life'] > 0:
                new_particles.append(p)
        self.particles = new_particles

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def reset(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.score_label.text = "Счёт: 3"
        self.particles = []

    def spawn_food(self):
        while True:
            new_food = (randint(0, self.width // GRID_SIZE - 1),
                        randint(0, self.height // GRID_SIZE - 1))
            if (new_food not in self.snake and
                new_food not in self.obstacles):  # Проверяем, чтобы еда не спавнилась в препятствиях
                self.food = new_food
                self.food_type = randint(0, 1)  # Случайный тип еды
                break

    def advance_level(self):
        self.level += 1
        if self.level >= len(LEVELS):
            self.level = len(LEVELS) - 1
        self.reset_level()
        # Обновляем label уровня через родительский экран
        game_screen = self.parent.parent if hasattr(self.parent, 'parent') else None
        if game_screen and hasattr(game_screen, 'level_label'):
            game_screen.level_label.text = f"Уровень: {self.level + 1}"

    def reset_level(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.food = (10, 10)
        self.obstacles = LEVELS[self.level]['obstacles']
        self.speed = LEVELS[self.level]['speed']
        self.goal = LEVELS[self.level]['goal']
        self.score_label.text = "Счёт: 3"
        self.particles = []

        # Перезапускаем таймер с новой скоростью
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, self.speed)

        self.draw()

    def draw(self):
        self.canvas.clear()
        self.init_effects()  # Перерисовываем сетку

        with self.canvas:
            # Рисуем змейку с градиентом
            for i, (x, y) in enumerate(self.snake):
                ratio = i / len(self.snake)
                Color(0.2, 1 - ratio * 0.5, 0.2, 1)
                Rectangle(
                    pos=(x * GRID_SIZE, y * GRID_SIZE),
                    size=(GRID_SIZE, GRID_SIZE)
                )
                # Голова с глазами
                if i == 0:
                    eye_size = GRID_SIZE // 5
                    Color(1, 1, 1, 1)
                    # Глаза в зависимости от направления
                    if self.direction[0] == 1:  # Вправо
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE - 2*eye_size, y * GRID_SIZE + GRID_SIZE//2),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE - 2*eye_size, y * GRID_SIZE + GRID_SIZE//3),
                            size=(eye_size, eye_size)
                        )
                    elif self.direction[0] == -1:  # Влево
                        Rectangle(
                            pos=(x * GRID_SIZE + eye_size, y * GRID_SIZE + GRID_SIZE//2),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + eye_size, y * GRID_SIZE + GRID_SIZE//3),
                            size=(eye_size, eye_size)
                        )
                    elif self.direction[1] == 1:  # Вверх
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE//3, y * GRID_SIZE + GRID_SIZE - 2*eye_size),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + 2*GRID_SIZE//3, y * GRID_SIZE + GRID_SIZE - 2*eye_size),
                            size=(eye_size, eye_size)
                        )
                    else:  # Вниз
                        Rectangle(
                            pos=(x * GRID_SIZE + GRID_SIZE//3, y * GRID_SIZE + eye_size),
                            size=(eye_size, eye_size)
                        )
                        Rectangle(
                            pos=(x * GRID_SIZE + 2*GRID_SIZE//3, y * GRID_SIZE + eye_size),
                            size=(eye_size, eye_size)
                        )

            # Рисуем еду
            self.draw_food()

            # Рисуем препятствия
            Color(0.5, 0.2, 0.2, 0.7)
            for ox, oy in self.obstacles:
                Rectangle(
                    pos=(ox * GRID_SIZE, oy * GRID_SIZE),
                    size=(GRID_SIZE, GRID_SIZE)
                )

            # Рисуем частицы
            for p in self.particles:
                alpha = p['life'] / 20 * p['color'][3] if 'life' in p else p['color'][3]
                Color(p['color'][0], p['color'][1], p['color'][2], alpha)
                Rectangle(
                    pos=(p['pos'][0] - p['size']/2, p['pos'][1] - p['size']/2),
                    size=(p['size'], p['size'])
                )

    def draw_food(self):
        fx, fy = self.food
        if not self.food_animation:
            self.food_animation = Animation(size=(GRID_SIZE * 1.3, GRID_SIZE * 1.3), duration=0.5) \
                                  + Animation(size=(GRID_SIZE, GRID_SIZE), duration=0.5)
            self.food_animation.repeat = True

        with self.canvas:
            # Разные виды еды
            if self.food_type == 0:  # Яблоко
                Color(1, 0.2, 0.2, 1)
                Rectangle(pos=(fx * GRID_SIZE, fy * GRID_SIZE), size=(GRID_SIZE, GRID_SIZE))
                # Листик
                Color(0.2, 0.8, 0.2, 1)
                Rectangle(
                    pos=(fx * GRID_SIZE + GRID_SIZE//3, fy * GRID_SIZE + GRID_SIZE - GRID_SIZE//4),
                    size=(GRID_SIZE//3, GRID_SIZE//4)
                )
            else:  # Груша
                Color(1, 0.8, 0.2, 1)
                Rectangle(pos=(fx * GRID_SIZE, fy * GRID_SIZE), size=(GRID_SIZE, GRID_SIZE))
                # Черенок
                Color(0.4, 0.2, 0.1, 1)
                Rectangle(
                    pos=(fx * GRID_SIZE + GRID_SIZE//2 - 1, fy * GRID_SIZE + GRID_SIZE - GRID_SIZE//5),
                    size=(2, GRID_SIZE//5)
                )

            # Блики на еде
            Color(1, 1, 1, 0.8)
            Rectangle(
                pos=(fx * GRID_SIZE + GRID_SIZE // 3, fy * GRID_SIZE + GRID_SIZE // 1.5),
                size=(GRID_SIZE // 4, GRID_SIZE // 4)
            )

    def set_direction(self, dx, dy):
        # Запрещаем разворот на 180 градусов
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)
    def set_level(self, level_index):
        self.level = level_index
        self.speed = LEVELS[self.level]['speed']
        self.goal = LEVELS[self.level]['goal']
        self.obstacles = LEVELS[self.level]['obstacles']
        self.reset()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = FloatLayout()

        self.score_label = Label(
            text="Счёт: 3",
            size_hint=(.3, .1),
            pos_hint={"top": 1, "x": 0},
            font_size=20
        )

        self.pause_button = Button(
            text="⚙️",  # Шестерёнка с явным указанием шрифта
            size_hint=(.1, .1),
            pos_hint={"top": 1, "right": 1},
            font_size=20,
            font_name='EmojiFont'  # Ключевое изменение
        )
        self.pause_button.bind(on_release=self.show_pause_menu)

        self.snake_game = EndlessSnakeGame(score_label=self.score_label)  # Используем EndlessSnakeGame
        self.root_layout.add_widget(self.snake_game)
        self.root_layout.add_widget(self.score_label)
        self.root_layout.add_widget(self.pause_button)

        self.add_widget(self.root_layout)
        # Добавляем кнопки управления (только для мобильных устройств)
        if platform == 'android' or platform == 'ios':
            self.add_control_buttons()
    def setup_game(self):
        self.root_layout.clear_widgets()

        self.score_label = Label(text="Счёт: 0", size_hint=(.3, .1), pos_hint={"top": 1, "x": 0}, font_size=20)
        self.pause_button = Button(text="⏸", size_hint=(.1, .1), pos_hint={"top": 1, "right": 1}, font_size=20)
        self.pause_button.bind(on_release=self.show_pause_menu)

        self.snake_game = EndlessSnakeGame(score_label=self.score_label)  # Используем EndlessSnakeGame

        self.root_layout.add_widget(self.snake_game)
        self.root_layout.add_widget(self.score_label)
        self.root_layout.add_widget(self.pause_button)

    def on_enter(self):
        self.setup_game()

    def show_pause_menu(self, instance):
        self.snake_game.pause()
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        resume_btn = Button(text="Продолжить", size_hint_y=None, height=50)
        restart_btn = Button(text="Перезапустить", size_hint_y=None, height=50)
        settings_btn = Button(text="Настройки", size_hint_y=None, height=50)
        exit_btn = Button(text="Выход в меню", size_hint_y=None, height=50)

        popup = Popup(title='Пауза', content=layout, size_hint=(0.7, 0.7), auto_dismiss=False)
        resume_btn.bind(on_release=lambda _: (self.snake_game.resume(), popup.dismiss()))
        restart_btn.bind(on_release=lambda _: (self.snake_game.reset(), self.snake_game.resume(), popup.dismiss()))
        settings_btn.bind(on_release=lambda _: (popup.dismiss(), setattr(self.manager, 'current', "settings")))
        exit_btn.bind(on_release=lambda _: (popup.dismiss(), setattr(self.manager, 'current', 'menu')))

        for btn in [resume_btn, restart_btn, settings_btn, exit_btn]:
            layout.add_widget(btn)

        popup.open()

    def add_control_buttons(self):
        # Функция анимации (можно сделать вложенной)
        def on_press(btn):
            anim = Animation(background_color=(1, 1, 1, 0.8), duration=0.1) + \
                   Animation(background_color=(1, 1, 1, 0.5), duration=0.3)
            anim.start(btn)

        # Создаем контейнер для кнопок
        control_layout = FloatLayout(size_hint=(1, 1))

        # Размер и прозрачность кнопок
        btn_size = (Window.width * 0.15, Window.width * 0.15)
        opacity = 0.5

        # Кнопка ВВЕРХ
        up_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'center_x': 0.5, 'top': 0.3},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='↑',
            font_size='24sp'
        )
        up_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(0, 1),
            on_release=on_press  # Анимация при нажатии
        )

        # Кнопка ВНИЗ
        down_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'center_x': 0.5, 'y': 0.05},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='↓',
            font_size='24sp'
        )
        down_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(0, -1),
            on_release=on_press
        )

        # Кнопка ВЛЕВО
        left_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'x': 0.05, 'center_y': 0.175},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='←',
            font_size='24sp'
        )
        left_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(-1, 0),
            on_release=on_press
        )

        # Кнопка ВПРАВО
        right_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'right': 0.95, 'center_y': 0.175},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='→',
            font_size='24sp'
        )
        right_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(1, 0),
            on_release=on_press
        )

        # Добавляем все кнопки в layout
        for btn in [up_btn, down_btn, left_btn, right_btn]:
            control_layout.add_widget(btn)

        self.root_layout.add_widget(control_layout)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clear_widgets()

        # Фон
        with self.canvas.before:
            Color(0.08, 0.1, 0.08, 1)
            self.bg_rect = Rectangle(size=Window.size)

        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Заголовок по центру
        title = EmojiLabel(
            text='[b]🐍 SNAKE GAME 🐍[/b]',
            markup=True,
            font_size='48sp',
            color=(0.3, 1, 0.3, 1),
            size_hint=(1, 0.2),
            halign='center'
        )
        main_layout.add_widget(title)

        # Контейнер для кнопок с фиксированной высотой
        button_container = GridLayout(
            cols=1,
            size_hint=(1, 0.8),
            spacing=15,
            padding=[50, 0]  # Боковые отступы
        )

        # Кнопки с фиксированной высотой
        buttons = [
            ("🐍 Бесконечный режим", 'endless'),
            ("🏰 Уровни", 'level_select'),
            ("🏆 Таблица рекордов", 'leaderboard'),
            ("⚙️ Настройки", 'settings'),
            ("🚪 Выход", 'exit')
        ]

        for text, screen in buttons:
            btn = NeonButton(
                text=text,
                size_hint=(1, None),
                height=60,
                font_name='EmojiFont'  # Используем наш шрифт с эмодзи
            )
            if screen == 'exit':
                btn.bind(on_release=App.get_running_app().stop)
            else:
                btn.bind(on_release=lambda x, s=screen: setattr(self.manager, 'current', s))
            button_container.add_widget(btn)

        main_layout.add_widget(button_container)
        self.add_widget(main_layout)

        self.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.size = self.size

    def on_enter(self):
        # Запускаем музыку при входе в меню
        App.get_running_app().start_menu_music()

    def on_leave(self):
        # Останавливаем музыку при выходе из меню
        App.get_running_app().stop_menu_music()

class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Заголовок
        title = EmojiLabel(
            text="Выберите уровень",
            font_size='28sp',
            size_hint=(1, None),
            height=50
        )
        main_layout.add_widget(title)

        # Контейнер с прокруткой для кнопок уровней
        scroll = ScrollView(size_hint=(1, 1))
        levels_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=15,  # Расстояние между кнопками
            padding=[20, 10]  # Отступы слева/справа и сверху/снизу
        )

        # Устанавливаем высоту в зависимости от количества кнопок
        levels_layout.bind(minimum_height=levels_layout.setter('height'))
        levels_layout.height = 60 * 20  # (высота кнопки + spacing) * количество уровней

        # Создаем кнопки для каждого уровня
        for i in range(1, 21):
            btn = Button(
                text=f"Уровень {i}",
                size_hint_y=None,
                height=50,  # Фиксированная высота кнопки
                font_size='20sp'
            )
            btn.bind(on_release=self.start_level)
            levels_layout.add_widget(btn)

        scroll.add_widget(levels_layout)
        main_layout.add_widget(scroll)

        # Кнопка "Назад"
        back_btn = Button(
            text="Назад",
            size_hint_y=None,
            height=60,
            font_size='24sp'
        )
        back_btn.bind(on_release=lambda _: setattr(self.manager, 'current', 'menu'))
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)

    def start_level(self, instance):
        level_index = int(instance.text.split()[-1]) - 1
        self.manager.get_screen('level_game').start_level(level_index)
        self.manager.current = 'level_game'

class LevelGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = FloatLayout()
        self.score_label = Label(text="Счёт: 3", size_hint=(.3, .1), pos_hint={"top": 1, "x": 0}, font_size=20)
        self.level_label = Label(text="Уровень: 1", size_hint=(.3, .1), pos_hint={"top": 0.9, "x": 0}, font_size=18)
        self.pause_button = Button(
            text="⚙️",  # Используем шестерёнку с вариационным селектором (эмоджи-версия)
            size_hint=(.1, .1),
            pos_hint={"top": 1, "right": 1},
            font_size=20,
            font_name='EmojiFont'  # Явно указываем шрифт
        )
        self.pause_button.bind(on_release=self.show_pause_menu)
        self.root_layout.add_widget(self.score_label)
        self.root_layout.add_widget(self.level_label)
        self.root_layout.add_widget(self.pause_button)
        self.add_widget(self.root_layout)

        if platform == 'android' or platform == 'ios':
            self.add_control_buttons()

    def add_control_buttons(self):
        # Функция анимации (можно сделать вложенной)
        def on_press(btn):
            anim = Animation(background_color=(1, 1, 1, 0.8), duration=0.1) + \
                   Animation(background_color=(1, 1, 1, 0.5), duration=0.3)
            anim.start(btn)

        # Создаем контейнер для кнопок
        control_layout = FloatLayout(size_hint=(1, 1))

        # Размер и прозрачность кнопок
        btn_size = (Window.width * 0.15, Window.width * 0.15)
        opacity = 0.5

        # Кнопка ВВЕРХ
        up_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'center_x': 0.5, 'top': 0.3},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='↑',
            font_size='24sp'
        )
        up_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(0, 1),
            on_release=on_press  # Анимация при нажатии
        )

        # Кнопка ВНИЗ
        down_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'center_x': 0.5, 'y': 0.05},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='↓',
            font_size='24sp'
        )
        down_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(0, -1),
            on_release=on_press
        )

        # Кнопка ВЛЕВО
        left_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'x': 0.05, 'center_y': 0.175},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='←',
            font_size='24sp'
        )
        left_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(-1, 0),
            on_release=on_press
        )

        # Кнопка ВПРАВО
        right_btn = Button(
            size_hint=(None, None),
            size=btn_size,
            pos_hint={'right': 0.95, 'center_y': 0.175},
            background_normal='',
            background_color=(1, 1, 1, opacity),
            text='→',
            font_size='24sp'
        )
        right_btn.bind(
            on_press=lambda x: self.snake_game.set_direction(1, 0),
            on_release=on_press
        )
        # Добавляем все кнопки в layout
        for btn in [up_btn, down_btn, left_btn, right_btn]:
            control_layout.add_widget(btn)
        self.root_layout.add_widget(control_layout)

    def start_level(self, level_index):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.score_label)
        self.root_layout.add_widget(self.level_label)
        self.root_layout.add_widget(self.pause_button)
        self.snake_game = SnakeGame(score_label=self.score_label)
        self.snake_game.set_level(level_index)
        self.root_layout.add_widget(self.snake_game)
        self.level_label.text = f"Уровень: {level_index + 1}"

    def show_pause_menu(self, instance):
        self.snake_game.pause()
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        resume_btn = Button(text="Продолжить", size_hint_y=None, height=50)
        restart_btn = Button(text="Перезапустить", size_hint_y=None, height=50)
        exit_btn = Button(text="Назад к уровням", size_hint_y=None, height=50)
        popup = Popup(title='Пауза', content=layout, size_hint=(0.7, 0.7), auto_dismiss=False)
        resume_btn.bind(on_release=lambda _: (self.snake_game.resume(), popup.dismiss()))
        restart_btn.bind(on_release=lambda _: (self.snake_game.reset(), self.snake_game.resume(), popup.dismiss()))
        exit_btn.bind(on_release=lambda _: (popup.dismiss(), setattr(self.manager, 'current', 'level_select')))
        for btn in [resume_btn, restart_btn, exit_btn]:
            layout.add_widget(btn)
        popup.open()

class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Основной layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Заголовок по центру
        self.title = EmojiLabel(
            text='🏆 ТОП ИГРОКОВ 🏆',
            font_size='32sp',
            size_hint=(1, 0.2),
            halign='center',
            valign='middle'
        )
        layout.add_widget(self.title)

        # Контейнер для таблицы с прокруткой
        scroll = ScrollView(size_hint=(1, 0.8))
        self.table = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=10,
            padding=[20, 10]
        )
        self.table.bind(minimum_height=self.table.setter('height'))
        scroll.add_widget(self.table)
        layout.add_widget(scroll)

        # Контейнер для кнопки "Назад" (центрируем)
        btn_container = BoxLayout(
            size_hint=(1, 1),
            padding=[150, 0]  # Добавляем отступы слева и справа для центрирования
        )

        # Кнопка "Назад" с эмодзи
        back_btn = NeonButton(
            text="⬅️ Назад",
            size_hint=(0.5, 1),  # Уменьшаем ширину кнопки
            pos_hint={'center_x': 0.5},  # Центрируем по горизонтали
            font_name='EmojiFont'
        )
        back_btn.bind(on_release=lambda _: setattr(self.manager, 'current', 'menu'))

        btn_container.add_widget(Widget())  # Пустой виджет слева
        btn_container.add_widget(back_btn)
        btn_container.add_widget(Widget())  # Пустой виджет справа

        layout.add_widget(btn_container)
        self.add_widget(layout)
        self.update_table()

    def update_table(self):
        print("DEBUG: Updating leaderboard table")
        top_players = get_top_players()
        print(f"DEBUG: Received top players: {top_players}")
        if not top_players:
            # Сообщение с эмодзи, если нет данных
            self.table.add_widget(EmojiLabel(
                text="😕 Пока нет рекордов",
                font_size='24sp',
                size_hint_y=None,
                height=100
            ))
            return
        for i, (name, score) in enumerate(top_players, 1):
            # Создаем элемент с эмодзи для топ-3 игроков
            emoji = ""
            if i == 1:
                emoji = "🥇 "
            elif i == 2:
                emoji = "🥈 "
            elif i == 3:
                emoji = "🥉 "
            item = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=60,
                spacing=10,
                padding=[20, 0]
            )
            # Место с эмодзи
            rank_label = EmojiLabel(
                text=f"{emoji}{i}.",
                font_size='24sp',
                size_hint_x=0.2,
                color=(0.3, 1, 0.3, 1) if i <= 3 else (0.8, 0.8, 0.8, 1)
            )
            item.add_widget(rank_label)

            # Имя игрока
            name_label = EmojiLabel(
                text=name,
                font_size='24sp',
                size_hint_x=0.6,
                halign='left'
            )
            item.add_widget(name_label)
            # Счет
            score_label = Label(
                text=str(score),
                font_size='24sp',
                size_hint_x=0.2,
                halign='right'
            )
            item.add_widget(score_label)
            self.table.add_widget(item)
        # Если текущий игрок не в топе, добавляем его отдельно
        if PLAYER_NAME and not any(name == PLAYER_NAME for name, _ in top_players):
            player_score = get_player_score(PLAYER_NAME)
            if player_score is not None:
                separator = Label(
                    text="...",
                    font_size='24sp',
                    size_hint_y=None,
                    height=40
                )
                self.table.add_widget(separator)
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=60,
                    spacing=10,
                    padding=[20, 0]
                )
                # Место в рейтинге
                rank = get_player_rank(PLAYER_NAME)
                rank_label = Label(
                    text=f"{rank}.",
                    font_size='24sp',
                    size_hint_x=0.1,
                    color=(0.8, 0.8, 0.8, 1)
                )
                item.add_widget(rank_label)
                # Имя игрока
                name_label = Label(
                    text=PLAYER_NAME,
                    font_size='24sp',
                    size_hint_x=0.6,
                    halign='left'
                )
                item.add_widget(name_label)
                # Счет
                score_label = Label(
                    text=str(player_score),
                    font_size='24sp',
                    size_hint_x=0.3,
                    halign='right'
                )
                item.add_widget(score_label)
                self.table.add_widget(item)

    def on_enter(self, *args):
        print("DEBUG: LeaderboardScreen entered")
        self.update_table()  # Обновляем таблицу при каждом входе

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clear_widgets()

        # Фон
        with self.canvas.before:
            Color(0.1, 0.12, 0.1, 1)
            self.bg_rect = Rectangle(size=Window.size)

        # Основной контейнер
        main_layout = FloatLayout()

        # Центральная форма
        form = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=20,
            padding=30
        )

        # Заголовок
        title = EmojiLabel(
            text='ВХОД',
            font_size='36sp',
            color=(0.3, 1, 0.3, 1),
            size_hint=(1, 0.3)
        )

        # Поля ввода
        self.username = AuthInput(
            hint_text='Имя пользователя',
            size_hint=(1, 0.15)
        )

        self.password = AuthInput(
            hint_text='Пароль',
            password=True,
            size_hint=(1, 0.15)
        )

        # Кнопки
        btn_layout = BoxLayout(
            size_hint=(1, 1),
            spacing=10
        )

        login_btn = NeonButton(text='Войти', size_hint=(1, 1))
        reg_btn = NeonButton(text='Регистрация', size_hint=(1, 1))

        login_btn.bind(on_release=self.login)
        reg_btn.bind(on_release=self.register)

        # Сборка интерфейса
        btn_layout.add_widget(login_btn)
        btn_layout.add_widget(reg_btn)

        form.add_widget(title)
        form.add_widget(self.username)
        form.add_widget(self.password)
        form.add_widget(btn_layout)

        main_layout.add_widget(form)
        self.add_widget(main_layout)

        self.bind(size=self.update_bg)

    def login(self, instance):
        try:
            username = self.username.text.strip()
            password = self.password.text.strip()

            if validate_user(username, password):
                global PLAYER_NAME
                PLAYER_NAME = username
                self.manager.current = 'menu'
            else:
                self.show_error_popup("Неверный логин или пароль")
        except Exception as e:
            self.show_error_popup("Ошибка соединения. Проверьте интернет")

    def register(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()

        if not username or not password:
            self.show_error_popup("Логин и пароль не могут быть пустыми")
            return

        if create_user(username, password):
            self.show_error_popup("Регистрация успешна! Теперь войдите", is_error=False)
        else:
            self.show_error_popup("Пользователь уже существует")

    def show_error_popup(self, message, is_error=True):
        # Сначала очистим предыдущие элементы
        #self.canvas.before.clear()

        # Создаем popup с сообщением об ошибке
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))

        ok_button = Button(text='OK', size_hint=(1, 0.4))
        popup = Popup(title='Ошибка' if is_error else 'Успех',
                      content=content,
                      size_hint=(0.7, 0.4))

        ok_button.bind(on_release=popup.dismiss)
        content.add_widget(ok_button)

        popup.open()

        # Очищаем поля ввода
        self.username.text = ''
        self.password.text = ''

    def animate_dots(self):
        for dot in self.dots:
            start_pos = dot.children[1].pos
            end_pos = (
                start_pos[0] + randint(-50, 50),
                start_pos[1] + randint(-50, 50)
            )
            anim = Animation(
                pos=end_pos,
                duration=randint(3, 7))
            anim.start(dot.children[1])
            anim.on_complete = self.animate_dots

    def update_bg(self, *args):
        self.bg_rect.size = self.size


class SnakeApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_music = None
        self.is_music_playing = False

    def build(self):
        try:
            init_db()  # Инициализация БД
        except Exception as e:
            Logger.error(f'Database init error: {str(e)}')
            # Создаем popup с ошибкой
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label

            popup = Popup(title='Error',
                          content=Label(text=f'Database error: {str(e)}'),
                          size_hint=(0.8, 0.4))
            popup.open()
            return Label(text=f'Error: {str(e)}')  # Возвращаем простой виджет с ошибкой
#----------------------
        # Регистрация шрифта с эмодзи
        from kivy.core.text import LabelBase
        LabelBase.register(
            name='EmojiFont',
            fn_regular='fonts/seguiemj.ttf'  # путь относительно main.py
        )

        # Установка шрифта по умолчанию
        from kivy.config import Config
        Config.set('kivy', 'default_font', ['EmojiFont', 'Arial'])

        init_db()
        settings = load_settings()
        self.apply_theme(settings["theme"])

        # Создаем корневой layout
        root = FloatLayout()

        # Добавляем эффект частиц первым (будет внизу z-порядка)
        self.particle_effect = ParticleEffect()
        root.add_widget(self.particle_effect)

        # Создаем менеджер экранов с кастомными переходами
        self.sm = EnhancedScreenManager()

        # Добавляем экраны
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(GameScreen(name='endless'))
        self.sm.add_widget(LeaderboardScreen(name='leaderboard'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(LevelSelectScreen(name='level_select'))
        self.sm.add_widget(LevelGameScreen(name='level_game'))

        root.add_widget(self.sm)

        # Обновляем частицы
        Clock.schedule_interval(self.particle_effect.update, 1 / 60)

        # Привязка мыши для интерактивного фона
        Window.bind(mouse_pos=self.on_mouse_pos)

        self.sm.current = 'login'
        self.load_music()
        return root

    def load_music(self):
        self.menu_music = SoundLoader.load(resource_find('sounds/menu_music.mp3'))
        if self.menu_music:
            self.menu_music.loop = True

    def start_menu_music(self):
        if self.menu_music and not self.is_music_playing:
            settings = load_settings()
            if settings.get("background_music", True):
                self.menu_music.play()
                self.is_music_playing = True

    def stop_menu_music(self):
        if self.menu_music and self.is_music_playing:
            self.menu_music.stop()
            self.is_music_playing = False
    def apply_theme(self, theme_name):
        """Применяет выбранную тему ко всему приложению"""
        if theme_name == "Тёмная":
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
        elif theme_name == "Светлая":
            Window.clearcolor = (1, 1, 1, 1)
        elif theme_name == "Ретро":
            Window.clearcolor = (0.1, 0.1, 0.2, 1)
        else:  # По умолчанию - тёмная тема
            Window.clearcolor = (0.1, 0.1, 0.1, 1)

    def on_start(self):
        self.start_menu_music()
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_stop(self):
        self.stop_menu_music()

    def on_mouse_pos(self, window, pos):
        # Интерактивный фон в меню
        if self.sm.current == 'menu':
            self.particle_effect.emit(
                pos,
                count=1,
                color=(0.3, 1, 0.3, 0.5),
                velocity=Vector(0, 0),
                size=randint(5, 10),
                life=30
            )

    def show_confetti(self):
        # Эффект конфетти
        for _ in range(100):
            x = randint(0, Window.width)
            y = randint(Window.height, Window.height + 100)
            color = (random(), random(), random(), 1)
            self.particle_effect.emit(
                (x, y),
                count=1,
                color=color,
                velocity=Vector(randint(-2, 2), randint(-10, -5)),
                size=randint(8, 15),
                life=randint(40, 60)
            )

#--ВНЕШНИЙ-ВИД---------------------------------------

    def switch_screen(self, screen_name, transition='fade'):
        self.sm.switch_to(screen_name, transition=transition)

class EmojiLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', 'EmojiFont')  # Используем наш шрифт
        super().__init__(**kwargs)

class NeonButton(Button):
    glow_intensity = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Прозрачный фон
        self.color = (0.3, 1, 0.3, 1)  # Неоново-зеленый текст
        self.font_size = '24sp'
        self.bold = True
        self.size_hint = (0.7, 0.12)

        with self.canvas.before:
            Color(0.1, 0.5, 0.1, 0.3)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )
            Color(0.2, 1, 0.2, 0.5)
            self.border_line = Line(
                rounded_rectangle=(*self.pos, *self.size, 15),
                width=1.2
            )
            Color(0.3, 1, 0.3, 0.1)
            self.glow = Ellipse(
                pos=(self.center_x - 50, self.center_y - 50),
                size=(100, 100))

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics,
            glow_intensity=self.update_glow
        )

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (*self.pos, *self.size, 15)
        self.update_glow()

    def update_glow(self, *args):
        glow_size = 100 + self.glow_intensity * 20
        self.glow.pos = (
            self.center_x - glow_size / 2,
            self.center_y - glow_size / 2
        )
        self.glow.size = (glow_size, glow_size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(glow_intensity=1, duration=0.3)
            anim.start(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        anim = Animation(glow_intensity=0, duration=0.5)
        anim.start(self)
        return super().on_touch_up(touch)


class AuthInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.9, 0.9, 0.9, 0.1)
        self.foreground_color = (1, 1, 1, 1)
        self.font_size = '20sp'
        self.padding = [15, 10]
        self.halign = 'center'
        self.cursor_color = (0.3, 1, 0.3, 1)

        with self.canvas.before:
            Color(0.3, 0.8, 0.3, 0.3)
            self.underline = Line(
                points=[self.x, self.y, self.right, self.y],
                width=1.5
            )

        self.bind(pos=self.update_underline, size=self.update_underline)

    def update_underline(self, *args):
        self.underline.points = [self.x, self.y, self.right, self.y]


class LeaderboardItem(BoxLayout):
    def __init__(self, rank, username, score, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50
        self.spacing = 10
        self.padding = [20, 0]

        # Ранг с иконкой
        rank_color = (1, 1, 0, 1) if rank <= 3 else (0.8, 0.8, 0.8, 1)
        rank_icon = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else f'{rank}.'

        self.add_widget(Label(
            text=rank_icon,
            font_size='24sp',
            color=rank_color,
            size_hint_x=0.15
        ))

        # Аватар (генерируем по имени)
        with self.canvas.before:
            Color(0.2, 0.4, 0.2, 0.3)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_bg, size=self.update_bg)

        # Информация об игроке
        main_info = BoxLayout(orientation='vertical')
        main_info.add_widget(Label(
            text=username,
            font_size='18sp',
            color=(0.9, 0.9, 0.9, 1),
            halign='left'
        ))

        # Прогресс бар
        progress = FloatLayout()
        with progress.canvas:
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=(0, 0), size=(200, 5))
            Color(0.3, 1, 0.3, 1)
            self.progress_bar = Rectangle(
                pos=(0, 0),
                size=(min(200, score * 2), 5)
            )

        main_info.add_widget(progress)
        self.add_widget(main_info)

        # Очки
        self.add_widget(Label(
            text=str(score),
            font_size='24sp',
            color=(1, 1, 1, 1),
            size_hint_x=0.3
        ))

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


#------------------------------------------------

# Новые классы для визуальных элементов
class RetroToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = (0.9, 0.9, 0.9, 1)
        self.font_size = 18
        self.size_hint = (1, 0.8)

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            Color(0.3, 0.3, 0.3, 1)
            self.border_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect, state=self.update_state)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.x - 2, self.y - 2)
        self.border_rect.size = (self.width + 4, self.height + 4)

    def update_state(self, *args):
        if self.state == 'down':
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.3, 1, 0.3, 1)
                self.bg_rect = Rectangle(size=self.size, pos=self.pos)
                Color(0.5, 1, 0.5, 1)
                self.border_rect = Rectangle(size=(self.width + 4, self.height + 4),
                                             pos=(self.x - 2, self.y - 2))


class RetroSwitch(ToggleButton):
    active = BooleanProperty(False)  # Добавляем Kivy Property

    def __init__(self, **kwargs):
        # Убедимся, что 'active' передается до вызова super()
        if 'active' in kwargs:
            self._active = kwargs.pop('active')
        else:
            self._active = False

        super().__init__(**kwargs)

        self.background_normal = ''
        self.background_down = ''
        self.color = (0.9, 0.9, 0.9, 1)
        self.state = 'down' if self._active else 'normal'

        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            self.track = RoundedRectangle(radius=[10])
            Color(0.5, 0.5, 0.5, 1)
            self.thumb = RoundedRectangle(size=(40, 40), radius=[20])

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics,
            state=self.update_state
        )
        self.update_graphics()

    def update_graphics(self, *args):
        self.track.pos = self.pos
        self.track.size = self.size
        thumb_x = self.right - 45 if self.state == 'down' else self.x + 5
        self.thumb.pos = (thumb_x, self.y + 5)
        self.thumb.size = (40, 40)

    def update_state(self, instance, value):
        if value == 'down':
            self.thumb.rgba = (0.3, 1, 0.3, 1)
            self.active = True
        else:
            self.thumb.rgba = (0.5, 0.5, 0.5, 1)
            self.active = False
        self.update_graphics()

    def on_active(self, instance, value):
        self.state = 'down' if value else 'normal'

class ThemePreview(Button):
    def __init__(self, theme_name, colors, selected=False, **kwargs):
        super().__init__(**kwargs)
        self.theme_name = theme_name
        self.colors = colors
        self.background_normal = ''
        self.background_down = ''

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=theme_name, size_hint_y=0.3))

        preview = FloatLayout(size_hint_y=0.7)
        with preview.canvas:
            Color(*colors[0])
            Rectangle(size=(self.width, self.height * 0.6))
            Color(*colors[1])
            Rectangle(pos=(0, 0), size=(self.width, self.height * 0.2))

        if selected:
            with preview.canvas.after:
                Color(0.3, 1, 0.3, 0.5)
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10), width=2)

        layout.add_widget(preview)
        self.add_widget(layout)
        self.bind(on_release=self.on_select)

    def on_select(self):
        self.dispatch('on_select')


#-------------------------------------
# Добавим эффекты перехода между экранами
class TransitionManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition_duration = 0.5
        self.effect = 'fade'  # 'fade', 'slide', 'snake'

    def set_current(self, name, effect=None):
        if effect:
            self.effect = effect

        if self.effect == 'fade':
            self.transition = FadeTransition()
        elif self.effect == 'slide':
            self.transition = SlideTransition(direction='left')
        elif self.effect == 'snake':
            self.transition = SnakeTransition()

        self.current = name


class SnakeTransition(TransitionBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duration = 0.5

    def start(self, manager):
        self.manager = manager
        self.screen_in = manager.current_screen
        self.screen_out = manager.screens[manager.current]

        with self.screen_in.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=Window.size)

        self._anim = Animation(x=Window.width, duration=self.duration)
        self._anim.bind(on_complete=self._finish)
        self._anim.start(self.rect)

    def _finish(self, *args):
        self.manager.remove_widget(self.screen_out)
        self.screen_in.canvas.before.remove(self.rect)
        self.is_active = False

# Добавим эффекты частиц
class ParticleEffect(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.max_particles = 200

    def emit(self, pos, count=1, color=(1, 1, 1, 1), velocity=None, size=None, life=None):
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                continue

            particle = {
                'pos': pos,
                'size': size if size else randint(5, 15),
                'color': color,
                'velocity': velocity if velocity else Vector(randint(-5, 5), randint(-5, 5)),
                'life': life if life else randint(20, 40)
            }
            self.particles.append(particle)

    def update(self, dt):
        new_particles = []
        self.canvas.clear()

        with self.canvas:
            for p in self.particles:
                p['pos'] = (p['pos'][0] + p['velocity'][0],
                            p['pos'][1] + p['velocity'][1])
                p['life'] -= 1

                if p['life'] > 0:
                    alpha = p['life'] / 40 * p['color'][3]
                    Color(p['color'][0], p['color'][1], p['color'][2], alpha)
                    Point(points=p['pos'], pointsize=p['size'])
                    new_particles.append(p)

        self.particles = new_particles


# Обновим кнопки для добавления эффектов частиц
class EnhancedNeonButton(Button):
    glow_intensity = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (0.3, 1, 0.3, 1)
        self.font_size = '24sp'
        self.bold = True
        self.size_hint = (0.7, 0.12)

        with self.canvas.before:
            Color(0.1, 0.5, 0.1, 0.3)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            Color(0.2, 1, 0.2, 0.5)
            self.border_line = Line(rounded_rectangle=(*self.pos, *self.size, 15), width=1.2)
            Color(0.3, 1, 0.3, 0.1)
            self.glow = Ellipse(pos=(self.center_x - 50, self.center_y - 50), size=(100, 100))

        self.bind(pos=self.update_graphics, size=self.update_graphics, glow_intensity=self.update_glow)

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (*self.pos, *self.size, 15)
        self.update_glow()

    def update_glow(self, *args):
        glow_size = 100 + self.glow_intensity * 20
        self.glow.pos = (self.center_x - glow_size / 2, self.center_y - glow_size / 2)
        self.glow.size = (glow_size, glow_size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(glow_intensity=1, duration=0.3)
            anim.start(self)

            # Эффект частиц при нажатии
            app = App.get_running_app()
            if hasattr(app, 'particle_effect'):
                app.particle_effect.emit(
                    touch.pos,
                    count=10,
                    color=(0.3, 1, 0.3, 0.7),
                    velocity=Vector(randint(-5, 5), randint(1, 5)),
                    size=randint(8, 15),
                    life=randint(30, 50)
                )
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        anim = Animation(glow_intensity=0, duration=0.5)
        anim.start(self)
        return super().on_touch_up(touch)

class EnhancedScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = FadeTransition()

    def switch_to(self, screen, transition='fade', direction='left'):
        if transition == 'fade':
            self.transition = FadeTransition()
        elif transition == 'slide':
            self.transition = SlideTransition(direction=direction)
        elif transition == 'snake':
            self.transition = SnakeTransition()

        self.current = screen


class RetroButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.font_size = '20sp'
        self.bold = True
        self.size_hint = (None, None)
        self.size = (150, 50)
        self.color = (0.9, 0.9, 0.9, 1)

        with self.canvas.before:
            # Фон кнопки
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10]
            )
            # Граница
            Color(0.4, 0.4, 0.4, 1)
            self.border_rect = RoundedRectangle(
                pos=(self.x - 2, self.y - 2),
                size=(self.width + 4, self.height + 4),
                radius=[12]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.x - 2, self.y - 2)
        self.border_rect.size = (self.width + 4, self.height + 4)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Эффект нажатия
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.3, 0.3, 0.3, 1)
                self.bg_rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[10]
                )
                Color(0.5, 1, 0.5, 1)
                self.border_rect = RoundedRectangle(
                    pos=(self.x - 2, self.y - 2),
                    size=(self.width + 4, self.height + 4),
                    radius=[12]
                )
            return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # Возвращаем обычный вид
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10]
            )
            Color(0.4, 0.4, 0.4, 1)
            self.border_rect = RoundedRectangle(
                pos=(self.x - 2, self.y - 2),
                size=(self.width + 4, self.height + 4),
                radius=[12]
            )
        return super().on_touch_up(touch)

if __name__ == '__main__':
    SnakeApp().run()
