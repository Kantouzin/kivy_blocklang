#!/usr/bin/python
# coding: utf-8

from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from blocks import DISTANCE_RANGE
from blocks.block_status import BlockStatus
from blocks.concrete_block import ConcreteBlock
from blocks.point import Point


class DeclareBlock(ConcreteBlock):
    def __init__(self):
        super(DeclareBlock, self).__init__()
        self.status = BlockStatus.Declare
        self.block_elem_point = None
        self.elem_block = None

        self.name = ""

    def make_code(self, codes, indent):
        codes += "    " * indent + self.name + " = "

        if self.elem_block is not None:
            codes, indent = self.elem_block.make_code(codes, indent)

        codes += "\n"

        return codes, indent

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

    def draw(self, x, y):
        length = 50
        frame_width = 3

        with self.canvas:
            Color(0.5, 0.3, 0.7)  # 枠線 (紫)
            self.components.append(
                Rectangle(pos=(x, y - length), size=(length*4, length))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + frame_width, y - length + frame_width),
                          size=(length*4 - frame_width*2, length - frame_width*2)
                          )
            )

        self.block_start_point = Point(x, y)
        self.block_end_point = Point(x, y - length)
        self.block_elem_point = Point(x + length*4, y)

        text_input = TextInput(text=self.code, multiline=False)
        text_input.pos = (x + 100, y - length + 10)
        text_input.size = (length*2 - 20, length - 20)
        text_input.bind(text=self.on_text)
        self.add_widget(text_input)
        self.components.append(text_input)

        label = Label(text="Declare")
        label.color = (0, 0, 0, 1)
        label.pos = (x + 10, y - length + 10)
        label.size = (length*2 - 20, length - 20)
        self.add_widget(label)
        self.components.append(label)

    def on_text(self, _, value):
        self.name = value
