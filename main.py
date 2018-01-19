
import sys
import io
import traceback
from contextlib import contextmanager

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config

import blocks

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
        elif n == "define":
            self.select_block = blocks.DefineBlock

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
            block.initialize_connect()

        # 接続の判定
        for block_1 in self.codes:
            for block_2 in self.codes:
                if block_1 is block_2:
                    continue
                block_1.connect_block(block_2)

        # 接続状況に従い更新
        for block in self.codes:
            block.update()

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
