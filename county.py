class County:
    def __init__(self, name, state, datacase, links, notes):
        self.name = name
        self.state = state
        self.links = links
        self.datacase = datacase
        self.notes = notes
    def __repr__(self):
        return str(dict({
            "name": self.name,
            "state": self.state,
            "links": self.links,
            "datacase": self.datacase,
            "notes": self.notes
                     }))
