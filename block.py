from abc import ABCMeta, abstractmethod

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.config import Config
import enum
import numpy as np

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


DISTANCE_RANGE = 20


class BlockStatus(enum.Enum):
    Function = 0    # 関数
    Argument = 1    # 引数
    Nest = 2        # 入れ子


class Point:
    def __init__(self, x, y):
        self.point = np.array([x, y])
        self.x = self.point[0]
        self.y = self.point[1]

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.point += other.point
        self.x, self.y = self.point
        return self

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.point -= other.point
        self.x, self.y = self.point
        return self

    def norm(self):
        return np.linalg.norm(self.point)


class AbstractBlock:
    __metaclass__ = ABCMeta

    @abstractmethod
    def move(self, dx, dy):
        return NotImplementedError()

    @abstractmethod
    def connect_block(self, block):
        return NotImplementedError()

    @abstractmethod
    def make_code(self, codes, indent):
        return NotImplementedError()

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


class ConcreteBlock(AbstractBlock, Widget):
    __metaclass__ = ABCMeta

    can_touch = True  # Block に mouse click 可能か

    def __init__(self):
        super(ConcreteBlock, self).__init__()
        
        self.status = None

        self.code = ""                  # 実行する Python コード
        self.components = []            # Block の持つ Widget 要素

        self.next_block = None          # 次に実行するブロック
        self.back_block = None          # 前に実行したブロック

        self.block_start_point = None   # ブロックの始点座標
        self.block_end_point = None     # Block の終点座標 = 次の Block が繋がる座標

        self.is_touched = False         # Block が mouse click されているか
        self.mouse_start_point = None   # mouse drag の始点

    def move(self, dx, dy):
        block = self
        while block is not None:
            for component in block.components:
                x, y = component.pos[0] - dx, component.pos[1] - dy

                # floatにcastしないと以下のerror messageが発生する
                # ValueError: Label.x have an invalid format
                component.pos = (float(x), float(y))

            block.block_start_point -= Point(dx, dy)
            block.block_end_point -= Point(dx, dy)

            if block.status in [BlockStatus.Function, BlockStatus.Nest]:
                block.block_elem_point -= Point(dx, dy)

                if block.elem_block is not None:
                    elem_block = block.elem_block

                    for component in elem_block.components:
                        x, y = component.pos[0] - dx, component.pos[1] - dy
                        component.pos = (x, y)

                    elem_block.block_start_point -= Point(dx, dy)
                    elem_block.block_end_point -= Point(dx, dy)

            if block.status == BlockStatus.Nest:
                block.block_nest_point -= Point(dx, dy)
                block.block_bar_point -= Point(dx, dy)

                if block.nest_block is not None:
                    nest_block = block.nest_block

                    for component in nest_block.components:
                        x, y = component.pos[0] - dx, component.pos[1] - dy
                        component.pos = (x, y)

                    nest_block.block_start_point -= Point(dx, dy)
                    nest_block.block_end_point -= Point(dx, dy)

                    # ここわるいコード
                    if nest_block.status in [BlockStatus.Function, BlockStatus.Nest]:
                        nest_block.block_elem_point -= Point(dx, dy)

                        if nest_block.elem_block is not None:
                            nest_elem_block = nest_block.elem_block

                            for component in nest_elem_block.components:
                                x, y = component.pos[0] - dx, component.pos[1] - dy
                                component.pos = (x, y)

                            nest_elem_block.block_start_point -= Point(dx, dy)
                            nest_elem_block.block_end_point -= Point(dx, dy)

            block = block.next_block

    def is_in_block(self, touch):
        for component in self.components:
            if (component.pos[0] <= touch.pos[0] <= component.pos[0] + component.size[0]
                    and component.pos[1] <= touch.pos[1] <= component.pos[1] + component.size[1]):
                return True
        return False

    def on_touch_down(self, touch):
        if "button" in touch.profile:
            if touch.button == "left" and self.is_in_block(touch) and ConcreteBlock.can_touch:
                self.is_touched = True
                ConcreteBlock.can_touch = False
                self.mouse_start_point = touch.pos

        return super(ConcreteBlock, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_touched:
            dx, dy = self.mouse_start_point[0] - touch.pos[0], self.mouse_start_point[1] - touch.pos[1]
            self.move(dx, dy)
            self.mouse_start_point = touch.pos

        return super(ConcreteBlock, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.is_touched:
            self.is_touched = False
            ConcreteBlock.can_touch = True

        return super(ConcreteBlock, self).on_touch_up(touch)

    @abstractmethod
    def make_code(self, codes, indent):
        return NotImplementedError()

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


class FunctionBlock(ConcreteBlock):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(FunctionBlock, self).__init__()
        self.status = BlockStatus.Function
        self.block_elem_point = None
        self.elem_block = None

    def connect_block(self, block):
        if self.can_connect_next(block):
            dx, dy = (block.block_start_point - self.block_end_point).point
            block.move(dx, dy)
            self.next_block = block
            block.back_block = self

        if self.can_connect_argument(block):
            dx, dy = (block.block_start_point - self.block_elem_point).point
            block.move(dx, dy)
            self.elem_block = block
            block.back_block = self

    def can_connect_next(self, block):
        if block.status == BlockStatus.Argument:
            return False

        dx, dy = (block.block_start_point - self.block_end_point).point

        if Point(dx, dy).norm() < DISTANCE_RANGE:
            return True
        else:
            return False

    def can_connect_argument(self, block):
        if block.status != BlockStatus.Argument:
            return False

        dx, dy = (block.block_start_point - self.block_elem_point).point

        if Point(dx, dy).norm() < DISTANCE_RANGE:
            return True
        else:
            return False

    @abstractmethod
    def make_code(self, codes, indent):
        return NotImplementedError()

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


class VariableBlock(ConcreteBlock):
    def __init__(self):
        super(VariableBlock, self).__init__()
        self.code1 = ""
        self.code2 = ""

    def connect_block(self, block):
        if self.can_connect_next(block):
            dx, dy = (block.block_start_point - self.block_end_point).point
            block.move(dx, dy)
            self.next_block = block
            block.back_block = self

    def can_connect_next(self, block):
        if block.status == BlockStatus.Argument:
            return False

        dx, dy = (block.block_start_point - self.block_end_point).point

        if Point(dx, dy).norm() < DISTANCE_RANGE:
            return True
        else:
            return False

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

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - length)

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


class ArgumentBlock(ConcreteBlock):
    def __init__(self):
        super(ArgumentBlock, self).__init__()
        self.status = BlockStatus.Argument

    def connect_block(self, block):
        pass

    def make_code(self, codes, indent):
        codes += self.code

        return codes, indent

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

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - length)

        text_input = TextInput(text=self.code, multiline=False)
        text_input.pos = (x + 10, y - length + 10)
        text_input.size = (length*2 - 20, length - 20)
        text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(text_input)
        self.components.append(text_input)

    def on_enter(self, text_input):
        self.code = text_input.text


class NestBlock(ConcreteBlock):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(NestBlock, self).__init__()
        self.status = BlockStatus.Nest

        self.block_elem_point = None
        self.block_nest_point = None        # 入れ子内に接続する点
        self.block_bar_point = None         # barが接続する点

        self.elem_block = None
        self.nest_block = None

    def connect_block(self, block):
        if self.can_connect_next(block):
            dx, dy = (block.block_start_point - self.block_end_point).point
            block.move(dx, dy)
            self.next_block = block
            block.back_block = self

        if self.can_connect_argument(block):
            dx, dy = (block.block_start_point - self.block_elem_point).point
            block.move(dx, dy)
            self.elem_block = block
            block.back_block = self

        if self.can_connect_nest(block):
            dx, dy = (block.block_start_point - self.block_nest_point).point
            block.move(dx, dy)
            self.nest_block = block
            block.back_block = self

    def can_connect_next(self, block):
        if block.status == BlockStatus.Argument:
            return False

        dx, dy = (block.block_start_point - self.block_end_point).point

        if Point(dx, dy).norm() < DISTANCE_RANGE:
            return True
        else:
            return False

    def can_connect_argument(self, block):
        if block.status != BlockStatus.Argument:
            return False

        dx, dy = (block.block_start_point - self.block_elem_point).point

        if Point(dx, dy).norm() < DISTANCE_RANGE:
            return True
        else:
            return False

    def can_connect_nest(self, block):
        if block.status == BlockStatus.Argument:
            return False

        dx, dy = (block.block_start_point - self.block_nest_point).point

        if Point(dx, dy).norm() < DISTANCE_RANGE:
            return True
        else:
            return False

    @abstractmethod
    def make_code(self, codes, indent):
        return NotImplementedError()

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


class IfBlock(NestBlock):
    def __init__(self):
        super(IfBlock, self).__init__()
        self.code = "if"

        self.bar = None
        self.end = None

    def make_code(self, codes, indent):
        codes += "    " * indent + "if "

        if self.elem_block is not None:
            codes, indent = self.elem_block.make_code(codes, indent)
        else:
            # ここでerrorを起こすべきだが、まずはTrue
            codes += "True"

        codes += ":\n"

        indent += 1
        # ここでif文中のcodeを実行
        next_block = self.nest_block
        while next_block is not None:
            codes, indent = next_block.make_code(codes, indent)
            next_block = next_block.next_block
        indent -= 1

        return codes, indent

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(0, 0, 1)  # 枠線 (青)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            self.bar = Rectangle(pos=(x, y - length*2), size=(length/3, length))
            self.components.append(self.bar)
            self.end = Rectangle(pos=(x, y - (length*2+length/3)), size=(length*4, length/3))
            self.components.append(self.end)

            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*2 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - (length*2+length/3))
        self.block_elem_point = Point(x + length*2, y)
        self.block_nest_point = Point(x + length/3, y - length)
        self.block_bar_point = Point(x, y - length)

        label = Label(text="If")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)


class PrintBlock(FunctionBlock):
    def __init__(self):
        super(PrintBlock, self).__init__()
        self.code = "print"

    def make_code(self, codes, indent):
        codes += "    " * indent + "print("

        if self.elem_block is not None:
            codes, indent = self.elem_block.make_code(codes, indent)

        codes += ")\n"

        return codes, indent

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

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - length)
        self.block_elem_point = Point(x + length*2, y)

        label = Label(text="Print")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)


class ClassBlock(NestBlock):
    def __init__(self):
        super(ClassBlock, self).__init__()
        self.code = "class"

        self.elem_end_point = None
        self.elem_block = None

    def make_code(self, codes, indent):
        codes += "    " * indent + "class "

        if self.elem_block is not None:
            codes, indent = self.elem_block.make_code(codes, indent)
        else:
            # ここでerrorを起こすべきだが、まずはFoo
            codes += "Foo"

        codes += ":\n"

        indent += 1
        # ここでif文中のcodeを実行
        indent -= 1

        return codes, indent

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(0.7, 0.7, 0.7)  # 枠線 (灰)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            self.bar = Rectangle(pos=(x, y - length*2), size=(length/3, length))
            self.components.append(
                self.bar
            )
            self.components.append(
                Rectangle(pos=(x, y - (length*2+length/3)), size=(length*4, length/3))
            )

            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*2 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - (length*2+length/3))
        self.block_elem_point = Point(x + length*2, y)

        label = Label(text="If")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)
