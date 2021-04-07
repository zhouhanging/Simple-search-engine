class Doc:
    def __init__(self):
        self.field = {}

    def add(self, field, content):
        self.field[field] = content

    def get(self, field):
        return self.field[field]
