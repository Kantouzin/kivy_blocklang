#!/usr/bin/python
# coding: utf-8

import numpy as np


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
