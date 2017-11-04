from abc import ABCMeta, abstractmethod

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class Block(Widget):
    __metaclass__ = ABCMeta
    can_touch = True  # Block に mouse click 可能か

    def __init__(self):
        super(Block, self).__init__()

        self.code = ""                  # 実行する Python コード
        self.components = []            # Block の持つ Widget 要素

        self.next_block = None          # 次に実行するブロック
        self.back_block = None          # 前に実行したブロック

        self.block_start_point = None   # ブロックの始点座標
        self.block_end_point = None     # Block の終点座標 = 次の Block が繋がる座標

        self.is_function_block = False
        self.is_variable_block = False
        self.is_elem_block = False
        self.is_nest_block = False
        self.is_end_block = False

        self.is_touched = False         # Block が mouse click されているか
        self.mouse_start_point = None   # mouse drag の始点

    def move(self, dx, dy):
        block = self
        while block is not None:
            for component in block.components:
                x = component.pos[0] - dx
                y = component.pos[1] - dy
                component.pos = (x, y)

            block.block_start_point[0] -= dx
            block.block_start_point[1] -= dy
            block.block_end_point[0] -= dx
            block.block_end_point[1] -= dy

            if block.is_function_block or block.is_nest_block:
                block.elem_end_point[0] -= dx
                block.elem_end_point[1] -= dy

                if block.elem_block is not None:
                    elem_block = block.elem_block

                    for component in elem_block.components:
                        x = component.pos[0] - dx
                        y = component.pos[1] - dy
                        component.pos = (x, y)

                    elem_block.block_start_point[0] -= dx
                    elem_block.block_start_point[1] -= dy
                    elem_block.block_end_point[0] -= dx
                    elem_block.block_end_point[1] -= dy

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

        if self.is_elem_block or block2.is_elem_block:
            return False

        dx = self.block_end_point[0] - block2.block_start_point[0]
        dy = self.block_end_point[1] - block2.block_start_point[1]

        d_range = 20
        if dx**2 + dy**2 < d_range**2:
            return True
        else:
            return False

    def can_connect_elem(self, block2):

        if self.elem_block is not None:
            return False

        dx = self.elem_end_point[0] - block2.block_start_point[0]
        dy = self.elem_end_point[1] - block2.block_start_point[1]

        d_range = 20
        if dx**2 + dy**2 < d_range**2:
            return True
        else:
            return False


class FunctionBlock(Block):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(FunctionBlock, self).__init__()
        self.is_function_block = True
        self.elem_end_point = None
        self.elem_block = None

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


class VariableBlock(Block):
    def __init__(self):
        super(VariableBlock, self).__init__()
        self.is_variable_block = True
        self.code1 = ""
        self.code2 = ""

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(1, 0, 1)  # 枠線 (黄)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length * 2, length))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length * 2 - frame_width * 2, length - frame_width * 2)
                          )
            )

        self.block_start_point = [x, y]
        self.block_end_point = [x, y - length]

        label = Label(text="=")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)

        text_input1 = TextInput(text=self.code1, multiline=False)
        text_input1.pos = (x + 10, y - length + 10)
        text_input1.size = (length * 2 / 3, length - 20)
        text_input1.bind(on_text_validate=self.on_enter1)
        self.add_widget(text_input1)
        self.components.append(text_input1)

        text_input2 = TextInput(text=self.code2, multiline=False)
        text_input2.pos = (x + 10 + length * 2 / 3 * 1.5, y - length + 10)
        text_input2.size = (length * 2 / 3, length - 20)
        text_input2.bind(on_text_validate=self.on_enter2)
        self.add_widget(text_input2)
        self.components.append(text_input2)

    def on_enter1(self, text_input):
        self.code1 = text_input.text

    def on_enter2(self, text_input):
        self.code2 = text_input.text


class ElemBlock(Block):
    def __init__(self):
        super(ElemBlock, self).__init__()
        self.is_elem_block = True

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(0, 1, 0)  # 枠線 (緑)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*2 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = [x, y]
        self.block_end_point = [x, y - length]

        text_input = TextInput(text=self.code, multiline=False)
        text_input.pos = (x + 10, y - length + 10)
        text_input.size = (length*2 - 20, length - 20)
        text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(text_input)
        self.components.append(text_input)

    def on_enter(self, text_input):
        self.code = text_input.text


class NestBlock(Block):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(NestBlock, self).__init__()
        self.is_nest_block = True
        self.elem_end_point = None
        self.elem_block = None

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


class IfBlock(NestBlock):
    def __init__(self):
        super(IfBlock, self).__init__()
        self.code = "if"

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(0, 0, 1)  # 枠線 (青)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*2 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = [x, y]
        self.block_end_point = [x, y - length]
        self.elem_end_point = [x + length*2, y]

        label = Label(text="If")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)


class EndBlock(Block):
    def __init__(self):
        super(EndBlock, self).__init__()
        self.is_end_block = True

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(0, 0, 1)  # 枠線 (赤)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*2 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = [x, y]
        self.block_end_point = [x, y - length]

        label = Label(text="End")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)


class PrintBlock(FunctionBlock):
    def __init__(self):
        super(PrintBlock, self).__init__()
        self.code = "print"

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(1, 0, 0)  # 枠線 (赤)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*2 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = [x, y]
        self.block_end_point = [x, y - length]
        self.elem_end_point = [x + length*2, y]

        label = Label(text="Print")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)

class ObjectBlock(Block):
    def __init__(self):
        super(ObjectBlock, self).__init__()
        self.code = "obj"

    def draw(self, x, y):
