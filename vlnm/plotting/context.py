
class Context:

    def __init__(self):
        self.stack = []

    def push(self, context):
        self.stack.append(context)

    def pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            return {}

    def current(self):
        value = {}
        for item in self.stack:
            value.update(**item)
        return value


class ContextCollection:

    def __init__(self):
        self.collection = {}

    def push(self, context_id, context):
        if context_id not in self.collection:
            self.collection[context_id] = Context()
        self.collection[context_id].push(context)

    def pop(self, context_id=None):
        if context_id:
            return self.collection[context_id].pop()
        value = {}
        for ctx_id in self.collection:
            value.update(**self.collection[ctx_id].pop())
        return value

    def current(self, context_id=None):
        if context_id:
            return self.collection[context_id].current()
        value = {}
        for ctx_id in self.collection:
            value.update(**self.collection[ctx_id].current())
        return value
