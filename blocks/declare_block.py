#!/usr/bin/python
# coding: utf-8

from blocks.concrete_block import ConcreteBlock


class DeclareBlock(ConcreteBlock):
    def __init__(self):
        super(DeclareBlock, self).__init__()

    def make_code(self, codes, indent):
        pass

    def connect_block(self, block):
        pass

    def draw(self, x, y):
        pass
