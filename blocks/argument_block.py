#!/usr/bin/python
# coding: utf-8

from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput

from blocks.block_status import BlockStatus
from blocks.concrete_block import ConcreteBlock
from blocks.point import Point


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
