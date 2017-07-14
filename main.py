from abc import ABCMeta, abstractmethod

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle

# ?
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class Block(Widget):
    __metaclass__ = ABCMeta
    can_touch = True  # Block に mouse click 可能か

    def __init__(self):
        super(Block, self).__init__()

        self.code = None  # 実行する Python コード
        self.components = []  # Block の持つ Widget 要素
        self.indent = 0

        self.next_block = None  # 次に実行するブロック
        self.back_block = None  # 前に実行したブロック
        self.block_start = None  # ブロックの始点座標
        self.block_end = None  # Block の終点座標 = 次の Block が繋がる座標

        self.next_elem = None  # 次の要素のブロック
        self.elem_end = None  # 要素の接続する始点
        self.next_nest = None  # 次の入れ子のブロック
        self.nest_end = None  # 入れ子の接続する始点

        self.has_nest = False
        self.has_elem = False
        self.is_elem = False

        self.is_touched = False  # Block が mouse click されているか
        self.mouse_start = None  # mouse drag の始点

    def move(self, dx, dy):
        block = self
        while block is not None:
            for component in block.components:
                x = component.pos[0] - dx
                y = component.pos[1] - dy
                component.pos = (x, y)

            block.block_start[0] -= dx
            block.block_start[1] -= dy
            block.block_end[0] -= dx
            block.block_end[1] -= dy

            block = block.next_block

    def is_in_block(self, touch):
        for component in self.components:
            if (component.pos[0] <= touch.pos[0] <= component.pos[0] + component.size[0]
                and component.pos[1] <= touch.pos[1] <= component.pos[1] + component.size[1]):
                return True
        return False

    def on_touch_down(self, touch):
        if "button" in touch.profile:
            if touch.button == "left" and self.is_in_block(touch) and Block.can_touch:
                self.is_touched = True
                Block.can_touch = False
                self.mouse_start = touch.pos

        return super(Block, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_touched:
            dx, dy = self.mouse_start[0] - touch.pos[0], self.mouse_start[1] - touch.pos[1]
            self.move(dx, dy)
            self.mouse_start = touch.pos

        return super(Block, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.is_touched:
            self.is_touched = False
            Block.can_touch = True

        return super(Block, self).on_touch_up(touch)

    @abstractmethod
    def draw(self, x, y):
        return NotImplementedError()

    def can_connect_next(self, block2):
        if self.next_block is not None:
            return False

        dx = self.block_end[0] - block2.block_start[0]
        dy = self.block_end[1] - block2.block_start[1]
        d = dx * dx + dy * dy
        if d < 20 * 20:
            return True
        else:
            return False

    def can_connect_elem(self, block2):
        if not self.has_elem:
            return False

        dx = self.elem_end[0] - block2.block_start[0]
        dy = self.elem_end[1] - block2.block_start[1]
        d = dx * dx + dy * dy
        if d < 20 * 20:
            return True
        else:
            return False

    def can_connect_nest(self, block2):
        if not self.has_nest:
            return False

        dx = self.nest_end[0] - block2.block_start[0]
        dy = self.nest_end[1] - block2.block_start[1]
        d = dx * dx + dy * dy
        if d < 20 * 20:
            return True
        else:
            return False


class ElemBlock(Block):
    def __init__(self):
        super(ElemBlock, self).__init__()
        self.value = ""
        self.text_input = None

        self.code = ""

    def draw(self, x, y):
        with self.canvas:
            Color(0, 1, 0)  # 枠線 (緑)
            self.components.append(
                Rectangle(pos=(x, y), size=(100, 50))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + 3, y + 3), size=(100 - 6, 50 - 6))
            )

        self.block_start = [x, y + 50]
        self.block_end = [x, y]

        self.text_input = TextInput(text=self.value, multiline=False)
        self.text_input.pos = (x + 10, y + 10)
        self.text_input.size = (100 - 20, 50 - 20)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)

    def on_enter(self, text_input):
        self.value = text_input.text
        # print(self.value)
        self.code = text_input.text


class NestBlock(Block):
    def __init__(self):
        super(NestBlock, self).__init__()
        self.code = None
        self.value = None
        self.text_input = None

        self.block_nest_end = None
        self.has_nest = True

    def draw(self, x, y):
        with self.canvas:
            Color(0, 0, 1)
            self.components.append(
                Rectangle(pos=(x, y - 50), size=(150, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 80), size=(20, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 100), size=(150, 20))
            )
            Color(1, 1, 1)
            self.components.append(
                Rectangle(pos=(x + 3, y - 50 + 3), size=(150 - 3 * 2, 50 - 3 * 2))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 80 - 3), size=(20 - 3 * 2, 50 + 3))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 100 + 3), size=(150 - 3 * 2, 20 - 3 * 2))
            )

        self.block_start = [x, y]
        self.block_end = [x, y - 100]

        self.text_input = TextInput(text="TEST", multiline=False)
        self.text_input.pos = (x + 10, y - 10 - 30)
        self.text_input.size = (150 - 10 * 2, 50 - 10 * 2)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)

    def on_enter(self, text_input):
        self.value = text_input.text
        print(self.value)


class IfBlock(NestBlock):
    def __init__(self):
        super(IfBlock, self).__init__()
        self.code = "if"
        self.text_input = None

    def on_enter(self, text_input):
        self.value = text_input.text
        print(self.value)

    def draw(self, x, y):
        with self.canvas:
            Color(0, 0, 1)
            self.components.append(
                Rectangle(pos=(x, y - 50), size=(150, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 80), size=(20, 50))
            )
            self.components.append(
                Rectangle(pos=(x, y - 100), size=(150, 20))
            )
            Color(1, 1, 1)
            self.components.append(
                Rectangle(pos=(x + 3, y - 50 + 3), size=(150 - 3 * 2, 50 - 3 * 2))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 80 - 3), size=(20 - 3 * 2, 50 + 3))
            )
            self.components.append(
                Rectangle(pos=(x + 3, y - 100 + 3), size=(150 - 3 * 2, 20 - 3 * 2))
            )

        self.block_start = [x, y]
        self.block_end = [x, y - 100]
        self.block_nest_end = [x + 20, y - 130]

        self.text_input = TextInput(text="True", multiline=False)
        self.text_input.pos = (x + 10, y - 10 - 30)
        self.text_input.size = (150 - 10 * 2, 50 - 10 * 2)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)


class PrintBlock(Block):
    def __init__(self):
        super(PrintBlock, self).__init__()
        self.code = "print"
        self.text_input = None
        self.value = "\"Hello, world !\""

    def draw(self, x, y):
        with self.canvas:
            Color(1, 0, 0)  # 枠線 (赤)
            self.components.append(
                Rectangle(pos=(x, y), size=(100, 50))
            )
            Color(1, 1, 1)  # 本体 (白)
            self.components.append(
                Rectangle(pos=(x + 3, y + 3), size=(100 - 6, 50 - 6))
            )

        self.block_start = [x, y + 50]
        self.block_end = [x, y]

        self.text_input = TextInput(text=self.value, multiline=False)
        self.text_input.pos = (x + 10, y + 10)
        self.text_input.size = (100 - 20, 50 - 20)

        self.text_input.bind(on_text_validate=self.on_enter)

        self.add_widget(self.text_input)
        self.components.append(self.text_input)

    def on_enter(self, text_input):
        self.value = text_input.text
        # print(self.value)


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

    def on_touch_down(self, touch):
        if "button" in touch.profile:
            if touch.button == "right":
                # new_block = TestBlock(touch.pos[0], touch.pos[1])
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
            block.nest_block = None

        # 接続の判定
        for block1 in self.codes:
            for block2 in self.codes:
                if block1 != block2:
                    if block1.can_connect_next(block2):
                        dx = block2.block_start[0] - block1.block_end[0]
                        dy = block2.block_start[1] - block1.block_end[1]

                        block2.move(dx, dy)
                        block1.next_block = block2
                        block2.back_block = block1

                    # if block1.can_connect_elem(block2):
                    #     dx = block2.block_start[0] - block1.elem_end[0]
                    #     dy = block2.block_start[0] - block1.elem_end[1]
                    #
                    #     block2.move(dx, dy)
                    #     block1.next_elem = block2
                    #     block2.back_block = block1
                    #
                    # if block1.can_connect_nest(block2):
                    #     dx = block2.block_start[0] - block1.nest_end[0]
                    #     dy = block2.block_start[1] - block1.nest_end[1]
                    #
                    #     block2.move(dx, dy)
                    #     block1.next_nest = block2
                    #     block2.back_block = block1

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
        while head is not None:
            exec_script += "    " * head.indent
            exec_script += head.code

            exec_script += "("
            if head.value is not None:
                exec_script += head.value
            exec_script += ")"
            if head.has_nest:
                exec_script += ":"
            exec_script += "\n"

            head = head.next_block
        # print(exec_script)
        self.parent_widget.ids["ti_code"].text = exec_script
        try:
            exec(exec_script)
        except:
            print("error")


class SelectBlockBar:
    def __init__(self):
        pass


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
