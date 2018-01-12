#!/usr/bin/python
# coding: utf-8

from abc import ABCMeta, abstractmethod

from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label

from blocks import DISTANCE_RANGE
from blocks.block_status import BlockStatus
from blocks.concrete_block import ConcreteBlock
from blocks.point import Point


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

    def initialize_connect(self):
        super(FunctionBlock, self).initialize_connect()
        self.elem_block = None

    @abstractmethod
    def make_code(self, codes, indent):
        return NotImplementedError()

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()


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
