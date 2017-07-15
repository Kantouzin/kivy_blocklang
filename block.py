from abc import ABCMeta, abstractmethod

from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle

# ?
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class Block(Widget):
    __metaclass__ = ABCMeta
    can_touch = True  # Block に mouse click 可能か

    def __init__(self):
        super(Block, self).__init__()

        self.code = None  # 実行する Python コード
        self.components = []  # Block の持つ Widget 要素
        self.indent = 0

        self.next_block = None  # 次に実行するブロック
        self.back_block = None  # 前に実行したブロック

        self.block_start = None  # ブロックの始点座標
        self.block_end = None  # Block の終点座標 = 次の Block が繋がる座標

        self.is_function_block = False
        self.is_variable_block = False
        self.is_elem_block = False
        self.is_nest_block = False

        self.is_touched = False  # Block が mouse click されているか
        self.mouse_start_point = None  # mouse drag の始点

    def move(self, dx, dy):
        block = self
        while block is not None:
            for component in block.components:
                x = component.pos[0] - dx
                y = component.pos[1] - dy
                component.pos = (x, y)

            block.block_start[0] -= dx
            block.block_start[1] -= dy
            block.block_end[0] -= dx
            block.block_end[1] -= dy

            block = block.next_block

    def is_in_block(self, touch):
        for component in self.components:
            if (component.pos[0] <= touch.pos[0] <= component.pos[0] + component.size[0]
                and component.pos[1] <= touch.pos[1] <= component.pos[1] + component.size[1]):
                return True
        return False

    def on_touch_down(self, touch):
        if "button" in touch.profile:
            if touch.button == "left" and self.is_in_block(touch) and Block.can_touch:
                self.is_touched = True
                Block.can_touch = False
                self.mouse_start_point = touch.pos

        return super(Block, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_touched:
            dx, dy = self.mouse_start_point[0] - touch.pos[0], self.mouse_start_point[1] - touch.pos[1]
            self.move(dx, dy)
            self.mouse_start_point = touch.pos

        return super(Block, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.is_touched:
            self.is_touched = False
            Block.can_touch = True

        return super(Block, self).on_touch_up(touch)

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()

    def can_connect_next(self, block2):
        if self.next_block is not None:
            return False

        dx = self.block_end[0] - block2.block_start[0]
        dy = self.block_end[1] - block2.block_start[1]
        d = dx * dx + dy * dy
        if d < 20 * 20:
            return True
        else:
            return False


class VariableBlock(Block):
    def __init__(self):
        super(VariableBlock, self).__init__()


class ElemBlock(Block):
    def __init__(self):
        super(ElemBlock, self).__init__()
        self.text_input = None

    def draw(self, x, y):
        with self.canvas:
            Color(0, 1, 0)  # 枠線 (緑)
            self.components.append(
                Rectangle(pos=(x, y), size=(100, 50))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + 3, y + 3), size=(100 - 6, 50 - 6))
            )

        self.block_start = [x, y + 50]
        self.block_end = [x, y]

        self.text_input = TextInput(text=self.value, multiline=False)
        self.text_input.pos = (x + 10, y + 10)
        self.text_input.size = (100 - 20, 50 - 20)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)

    def on_enter(self, text_input):
        self.value = text_input.text
        self.code = text_input.text


class NestBlock(Block):
    def __init__(self):
        super(NestBlock, self).__init__()
        self.text_input = None
        self.block_nest_end = None

    def draw(self, x, y):
        with self.canvas:
            Color(0, 0, 1)
            self.components.append(
                Rectangle(pos=(x, y - 50), size=(150, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 80), size=(20, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 100), size=(150, 20))
            )
            Color(1, 1, 1)
            self.components.append(
                Rectangle(pos=(x + 3, y - 50 + 3), size=(150 - 3 * 2, 50 - 3 * 2))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 80 - 3), size=(20 - 3 * 2, 50 + 3))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 100 + 3), size=(150 - 3 * 2, 20 - 3 * 2))
            )

        self.block_start = [x, y]
        self.block_end = [x, y - 100]

        self.text_input = TextInput(text="TEST", multiline=False)
        self.text_input.pos = (x + 10, y - 10 - 30)
        self.text_input.size = (150 - 10 * 2, 50 - 10 * 2)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)

    def on_enter(self, text_input):
        self.code = text_input.text
        print(self.value)


class IfBlock(NestBlock):
    def __init__(self):
        super(IfBlock, self).__init__()
        self.code = "if"
        self.text_input = None

    def on_enter(self, text_input):
        self.code = text_input.text
        print(self.value)

    def draw(self, x, y):
        with self.canvas:
            Color(0, 0, 1)
            self.components.append(
                Rectangle(pos=(x, y - 50), size=(150, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 80), size=(20, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 100), size=(150, 20))
            )
            Color(1, 1, 1)
            self.components.append(
                Rectangle(pos=(x + 3, y - 50 + 3), size=(150 - 3 * 2, 50 - 3 * 2))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 80 - 3), size=(20 - 3 * 2, 50 + 3))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 100 + 3), size=(150 - 3 * 2, 20 - 3 * 2))
            )

        self.block_start = [x, y]
        self.block_end = [x, y - 100]
        self.block_nest_end = [x + 20, y - 130]

        self.text_input = TextInput(text="True", multiline=False)
        self.text_input.pos = (x + 10, y - 10 - 30)
        self.text_input.size = (150 - 10 * 2, 50 - 10 * 2)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)


class PrintBlock(Block):
    def __init__(self):
        super(PrintBlock, self).__init__()
        self.code = "print"
        self.text_input = None
        self.value = "\"Hello, world !\""

    def draw(self, x, y):
        with self.canvas:
            Color(1, 0, 0)  # 枠線 (赤)
            self.components.append(
                Rectangle(pos=(x, y), size=(100, 50))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + 3, y + 3), size=(100 - 6, 50 - 6))
            )

        self.block_start = [x, y + 50]
        self.block_end = [x, y]

        self.text_input = TextInput(text=self.value, multiline=False)
        self.text_input.pos = (x + 10, y + 10)
        self.text_input.size = (100 - 20, 50 - 20)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)

    def on_enter(self, text_input):
        self.value = text_input.text
        # print(self.value)
