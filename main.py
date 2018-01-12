
import sys
import io
import traceback
from contextlib import contextmanager

import blocks
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config

# ここにこれimportするのヤバくね？
from blocks.block_status import BlockStatus
from blocks.point import Point

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '600')


@contextmanager
def stdoutIO():
    old = sys.stdout
    sys.stdout = io.StringIO()
    yield sys.stdout
    sys.stdout = old


class CodeArea(Widget):
    def __init__(self, **kwargs):
        super(CodeArea, self).__init__(**kwargs)

        self.codes = []

        self.select_block = blocks.PrintBlock

    def set_block(self, n):
        if n == "print":
            self.select_block = blocks.PrintBlock
        elif n == "if":
            self.select_block = blocks.IfBlock
        elif n == "elem":
            self.select_block = blocks.ArgumentBlock
        elif n == "variable":
            self.select_block = blocks.DeclareBlock
        elif n == "object":
            self.select_block = blocks.ClassBlock

    def on_touch_down(self, touch):
        if "button" in touch.profile:
            if touch.button == "right":
                new_block = self.select_block()
                new_block.draw(touch.pos[0], touch.pos[1])
                self.codes.append(new_block)
                self.add_widget(new_block)

        return super(CodeArea, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if "button" in touch.profile:
            if touch.button == "left":
                self.connect_block()

        return super(CodeArea, self).on_touch_up(touch)

    def connect_block(self):
        # 接続の初期化
        for block in self.codes:
            block.next_block = None
            block.back_block = None

            if block.status in [BlockStatus.Function, BlockStatus.Nest]:
                block.elem_block = None

            if block.status == BlockStatus.Nest:
                block.nest_block = None

        # 接続の判定
        for block1 in self.codes:
            for block2 in self.codes:
                if block1 == block2:
                    continue
                block1.connect_block(block2)

        # 入れ子部の拡大
        # 悪質なコードだから修正しようね
        for block in self.codes:
            if block.status == BlockStatus.Nest:
                length = 50
                nest_block = block.nest_block
                while nest_block is not None:
                    length += 50
                    nest_block = nest_block.next_block

                block.bar.size = (block.bar.size[0], length)
                block.bar.pos = (block.block_bar_point.x, block.block_bar_point.y - length)
                block.end.pos = (block.block_bar_point.x, block.block_bar_point.y - length - 50/3)

                distance = block.block_end_point - Point(block.end.pos[0], block.end.pos[1])
                block.block_end_point = Point(block.end.pos[0], block.end.pos[1])

                next_block = block.next_block
                while next_block is not None:
                    # ここに入れ子blockに接続されたblockを移動させるコードを書こう
                    next_block.move(distance.x, distance.y)
                    next_block = next_block.next_block

    def exec_block(self):
        # すべてのブロックが接続されている
        # = headがひとつのとき, 実行可能
        head = None
        count = 0
        for code in self.codes:
            if code.back_block is None:
                head = code
                count += 1
        if count != 1:
            return

        exec_script = ""
        indent = 0
        while head is not None:
            exec_script, indent = head.make_code(exec_script, indent)
            head = head.next_block

        self.parent.parent.ids["ti_code"].text = exec_script

        with stdoutIO() as stdout_string:
            error = ""
            try:
                exec(exec_script)
            except:
                error = traceback.format_exc()
            finally:
                result = stdout_string.getvalue() + error
                self.parent.parent.ids["ti_exec"].text = result


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)


class VPLApp(App):
    def __init__(self):
        super(VPLApp, self).__init__()
        self.title = "Visual Programming Language"

    def build(self):
        return RootWidget()

if __name__ == "__main__":
    VPLApp().run()
