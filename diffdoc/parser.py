from . import rst


class Diff(object):
    def __init__(self, name, render, content):
        self.name = name
        self.render = render
        self.content = content


class Output(object):
    def __init__(self, name, render, content):
        self.name = name
        self.render = render
        self.content = content


class Render(object):
    def __init__(self, name, content):
        self.name = name
        self.content = content


class Replace(object):
    def __init__(self, name, render, content):
        self.name = name
        self.render = render
        self.content = content


class Start(object):
    def __init__(self, name, language, render, content):
        self.name = name
        self.language = language
        self.render = render
        self.content = content


def loads(source_text):
    source = rst.loads(source_text)
    return [
        _read_rst_element(element)
        for element in source
    ]


def _read_rst_element(element):
    if isinstance(element, rst.DiffdocBlock):
        element_type, name = element.arguments
        options = element.options.copy()
        kwargs = {"name": name, "content": element.content}
        if element_type != "render":
            kwargs["render"] = _bool_text[options.pop("render")]
        if element_type == "start":
            kwargs["language"] = options.pop("language")
        assert options == {}, "extra options: {}".format(options)
        return _element_types[element_type](**kwargs)
    else:
        return element


_element_types = {
    "diff": Diff,
    "output": Output,
    "render": Render,
    "replace": Replace,
    "start": Start,
}


_bool_text = {"True": True, "False": False}
