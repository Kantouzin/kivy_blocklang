
from block import ElemBlock, IfBlock, EndBlock, PrintBlock, VariableBlock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class CodeArea(Widget):
    def __init__(self, parent_widget):
        super(CodeArea, self).__init__()

        self.codes = []
        self.parent_widget = parent_widget

        self.select_block = PrintBlock

    def set_block(self, n):
        if n == 0:
            self.select_block = PrintBlock
        elif n == 1:
            self.select_block = IfBlock
        elif n == 2:
            self.select_block = ElemBlock
        elif n == 3:
            self.select_block = EndBlock
        elif n == 4:
            self.select_block = VariableBlock

    def on_touch_down(self, touch):
        if "button" in touch.profile:
            if touch.button == "right":
                new_block = self.select_block()
                new_block.draw(touch.pos[0], touch.pos[1])
                self.codes.append(new_block)
                self.parent_widget.add_widget(new_block)

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

            if block.is_function_block or block.is_nest_block:
                block.elem_block = None

        # 接続の判定
        for block1 in self.codes:
            for block2 in self.codes:
                if block1 == block2:
                    continue

                if block1.can_connect_next(block2):
                    dx = block2.block_start_point[0] - block1.block_end_point[0]
                    dy = block2.block_start_point[1] - block1.block_end_point[1]

                    block2.move(dx, dy)
                    block1.next_block = block2
                    block2.back_block = block1

                if (block1.is_function_block or block1.is_nest_block) and block2.is_elem_block:
                    if block1.can_connect_elem(block2):
                        dx = block2.block_start_point[0] - block1.elem_end_point[0]
                        dy = block2.block_start_point[1] - block1.elem_end_point[1]

                        block2.move(dx, dy)
                        block1.elem_block = block2
                        block2.back_block = block1

    def exec_block(self):
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
            if head.is_function_block:              # 関数ブロック
                exec_script += "    " * indent
                exec_script += head.code
                exec_script += "("
                if head.elem_block is not None:
                    exec_script += head.elem_block.code
                exec_script += ")\n"
            elif head.is_variable_block:            # 変数宣言ブロック
                exec_script += "    " * indent
                exec_script += head.code1 + " = " + head.code2 + "\n"
            elif head.is_nest_block:                # 入れ子ブロック
                exec_script += "    " * indent
                exec_script += head.code
                exec_script += "("
                if head.elem_block is not None:
                    exec_script += head.elem_block.code
                exec_script += "):\n"
                indent += 1
            elif head.is_end_block:
                indent -= 1

            head = head.next_block

        self.parent_widget.ids["ti_code"].text = exec_script

        try:
            exec(exec_script)
        except Exception as error:
            print(error)


class RootWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

        self.code_area = CodeArea(self)
        self.add_widget(self.code_area)


class VPLApp(App):
    def __init__(self):
        super(VPLApp, self).__init__()
        self.title = "Visual Programming Language"

if __name__ == "__main__":
    VPLApp().run()
