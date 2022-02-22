from typing import List, Callable


class HTMLElement:
    def render_text(self) -> str:
        raise NotImplementedError

    def render_markdown(self) -> str:
        raise NotImplementedError


AfterRenderHook = Callable[[str], str]
BeforeRenderHook = Callable[[HTMLElement], List[HTMLElement]]


class Header(HTMLElement):
    def __init__(self, level: int, text: str):
        self.level = level
        self.text = text

    def render_text(self) -> str:
        return self.text + '\n\n'

    def render_markdown(self) -> str:
        return '#' * self.level + ' ' + self.text + '\n\n'


class Text(HTMLElement, str):
    def __init__(self, content: str):
        self.content = content

    def render_text(self) -> str:
        return self.content

    def render_markdown(self) -> str:
        return self.content


class MathElement(HTMLElement):
    def __init__(self, raw_text: str, image_source: str):
        self.raw_text = raw_text
        self.image_source = image_source

    def render_text(self) -> str:
        return self.raw_text

    def render_markdown(self) -> str:
        return ' ![]({}) '.format(self.image_source)


class Paragraph(HTMLElement):
    def __init__(self, elements=None):
        self.elements = elements if elements is not None else []

    def render_text(self) -> str:
        return ''.join(e.render_text() for e in self.elements) + '\n\n'

    def render_markdown(self) -> str:
        return ''.join(e.render_markdown() for e in self.elements) + '\n\n'

    def append(self, element: HTMLElement):
        self.elements.append(element)


class Article:
    def __init__(self, content: List[HTMLElement]):
        self.content: List[HTMLElement] = content
        self.after_render_hook: AfterRenderHook = lambda x: x
        self.before_render_hook: BeforeRenderHook = lambda x: x

    def render_text(self) -> str:
        content = self.before_render_hook(self.content)
        output = ''.join(e.render_text() for e in content)
        return self.after_render_hook(output)

    def render_markdown(self) -> str:
        content = self.before_render_hook(self.content)
        output = ''.join(e.render_markdown() for e in content)
        return self.after_render_hook(output)
