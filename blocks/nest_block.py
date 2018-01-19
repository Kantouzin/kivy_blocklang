#!/usr/bin/python
# coding: utf-8

from abc import ABCMeta, abstractmethod

from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from blocks import DISTANCE_RANGE
from blocks.block_status import BlockStatus
from blocks.concrete_block import ConcreteBlock
from blocks.point import Point


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

    def initialize_connect(self):
        super(NestBlock, self).initialize_connect()
        self.nest_block = None

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


class ClassBlock(NestBlock):
    def __init__(self):
        super(ClassBlock, self).__init__()
        self.code = "class"

        self.bar = None
        self.end = None

    def make_code(self, codes, indent):
        codes += "    " * indent + "class "

        if self.elem_block is not None:
            codes, indent = self.elem_block.make_code(codes, indent)
        else:
            # ここでerrorを起こすべきだが、まずはFoo
            codes += "Foo"

        codes += ":\n"

        indent += 1
        # ここで入れ子のcodeを実行
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
            Color(0.7, 0.7, 0.7)  # 枠線 (灰)

            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*2, length))
            )
            self.bar = Rectangle(pos=(x, y - length*2), size=(length/3, length))
            self.components.append(self.bar)

            self.end = Rectangle(pos=(x, y - (length * 2 + length / 3)), size=(length * 4, length / 3))
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

        label = Label(text="Class")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)


class DefineBlock(NestBlock):
    def __init__(self):
        super(DefineBlock, self).__init__()
        self.code = "class"

        self.name = ""  # 関数名

        self.bar = None
        self.end = None

    def make_code(self, codes, indent):
        codes += "    " * indent + "def " + self.name

        codes += "("
        if self.elem_block is not None:
            codes, indent = self.elem_block.make_code(codes, indent)
        codes += "):\n"

        indent += 1
        # ここで入れ子のcodeを実行
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
            Color(0.5, 0.3, 0.7)  # 枠線 (紫)

            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*4, length))
            )
            self.bar = Rectangle(pos=(x, y - length*2), size=(length/3, length))
            self.components.append(self.bar)

            self.end = Rectangle(pos=(x, y - (length * 2 + length / 3)), size=(length * 4, length / 3))
            self.components.append(self.end)

            Color(1, 1, 1)  # 本体 (白)

            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*4 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - (length*2+length/3))
        self.block_elem_point = Point(x + length*4, y)
        self.block_nest_point = Point(x + length/3, y - length)
        self.block_bar_point = Point(x, y - length)

        text_input = TextInput(text=self.name, multiline=False)
        text_input.pos = (x + 100, y - length + 10)
        text_input.size = (length*2 - 20, length - 20)
        text_input.bind(text=self.on_text)

        self.add_widget(text_input)
        self.components.append(text_input)

        label = Label(text="define")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)

    def on_text(self, _, value):
        self.name = value
