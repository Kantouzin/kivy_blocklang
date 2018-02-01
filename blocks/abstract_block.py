#!/usr/bin/python
# coding: utf-8

from abc import ABCMeta, abstractmethod


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
