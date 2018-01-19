#!/usr/bin/python
# coding: utf-8

from abc import ABCMeta, abstractmethod

from kivy.uix.widget import Widget

from blocks.abstract_block import AbstractBlock
from blocks.block_status import BlockStatus
from blocks.point import Point


class ConcreteBlock(AbstractBlock, Widget):
    __metaclass__ = ABCMeta

    can_touch = True  # Block に mouse click 可能か

    def __init__(self):
        super(ConcreteBlock, self).__init__()

        self.status = None

        self.code = ""  # 実行する Python コード
        self.components = []  # Block の持つ Widget 要素

        self.next_block = None  # 次に実行するブロック
        self.back_block = None  # 前に実行したブロック

        self.block_start_point = None  # ブロックの始点座標
        self.block_end_point = None  # Block の終点座標 = 次の Block が繋がる座標

        self.is_touched = False  # Block が mouse click されているか
        self.mouse_start_point = None  # mouse drag の始点

    def move(self, dx, dy):
        block = self
        while block is not None:
            # blockのcomponentを(dx, dy)分移動する
            for component in block.components:
                # float型にcastしないと以下のerror messageが発生する
                # ValueError: Label.x have an invalid format
                x, y = float(component.pos[0] - dx), float(component.pos[1] - dy)

                component.pos = (x, y)

            # blockの始点と終点の更新
            block.block_start_point -= Point(dx, dy)
            block.block_end_point -= Point(dx, dy)

            # 関数, 入れ子型Blockの, 引数Blockについての処理
            if block.status in [BlockStatus.Function, BlockStatus.Nest]:
                block.block_elem_point -= Point(dx, dy)

                if block.elem_block is not None:
                    elem_block = block.elem_block

                    for component in elem_block.components:
                        x, y = float(component.pos[0] - dx), float(component.pos[1] - dy)
                        component.pos = (x, y)

                    elem_block.block_start_point -= Point(dx, dy)
                    elem_block.block_end_point -= Point(dx, dy)

            if block.status == BlockStatus.Nest:
                block.block_nest_point -= Point(dx, dy)
                block.block_bar_point -= Point(dx, dy)

                if block.nest_block is not None:
                    nest_block = block.nest_block

                    for component in nest_block.components:
                        x, y = float(component.pos[0] - dx), float(component.pos[1] - dy)
                        component.pos = (x, y)

                    nest_block.block_start_point -= Point(dx, dy)
                    nest_block.block_end_point -= Point(dx, dy)

                    # ここわるいコード
                    if nest_block.status in [BlockStatus.Function, BlockStatus.Nest]:
                        nest_block.block_elem_point -= Point(dx, dy)

                        if nest_block.elem_block is not None:
                            nest_elem_block = nest_block.elem_block

                            for component in nest_elem_block.components:
                                x, y = float(component.pos[0] - dx), float(component.pos[1] - dy)
                                component.pos = (x, y)

                            nest_elem_block.block_start_point -= Point(dx, dy)
                            nest_elem_block.block_end_point -= Point(dx, dy)

            block = block.next_block

    def initialize_connect(self):
        self.next_block = None
        self.back_block = None

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

    def update(self):
        pass
