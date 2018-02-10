# coding: utf-8

DISTANCE_RANGE = 20

from blocks.function_block import PrintBlock
from blocks.nest_block import IfBlock, ClassBlock, DefineBlock
from blocks.argument_block import ArgumentBlock
from blocks.declare_block import DeclareBlock
from blocks.call_block import CallBlock

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
