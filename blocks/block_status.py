#!/usr/bin/python
# coding: utf-8

import enum


class BlockStatus(enum.Enum):
    Function = 0    # 関数
    Argument = 1    # 引数
    Nest = 2        # 入れ子
    Declare = 3     # 変数宣言
    Call = 4        # 関数呼び出し
