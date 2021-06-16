#Provides UI objects to be drawn
#Kinda not needed but whatever
class Interface(object):
    interface = []
    def __init__(self, name, app):
        self.interface.append(self)
        self.name = name
    def __repr__(self):
        return self.name, (self.x, self.y)
    def __hash__(self):
        return hash((self.name, self.x, self.y))
    def __eq__(self, other):
        return self.name == other.name
    
    def update(self, app):
        pass
    def draw(self, app, canvas):
        pass

class Cursor(Interface):
    
    def __init__(self, app):
        super().__init__("Cursor", app)
        self.r = 500
        self.x = app.width//2
        self.y = app.width//2
    
    def update(self, app):
        pass
    
    def draw(self, app, canvas):
        pass