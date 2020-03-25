import math

class Object:
    def __init__(self, x, y, color, symbol):
        self.x = x
        self.y = y
        self.color = color
        self.symbol = symbol
    def get_pos(self):
        return (self.x, self.y)
    def move(self, dir):
        if dir == "right":
            self.x += 1
        elif dir == "left":
            self.x -= 1
        elif dir == "down":
            self.y += 1
        elif dir == "up":
            self.y -= 1
    def update(self, timediff, gamehandler):
        pass

class BlockObject(Object):
    pass

class Collectable(Object):
    def __init__(self, x, y, color, symbol, name):
        super().__init__(x, y, color, symbol)
        self.name = name

class MovingObject(Object):
    def __init__(self, x, y, color, symbol, dir, speed):
        super().__init__(x, y, color, symbol)
        self.direction = dir
        self.speed = speed
        self._micro_steps = 0.0
    def change_direction(self, dir):
        self.direction = dir
        self._micro_steps = 0
    def update(self, timediff, gamehandler):
        if self.direction != None:
            self._micro_steps += self.speed * timediff
            while self._micro_steps > 1:
                self._micro_steps -= 1.0
                cx, cy = self.x, self.y
                self.move(self.direction)
                nx, ny = self.x, self.y
                # undo
                self.x, self.y = cx, cy
                if gamehandler.on_before_move(self, nx, ny):
                    # can move, apply new x and y
                    self.x, self.y = nx, ny

class ArrowShot(MovingObject):
    def __init__(self, x, y, color, symbol, dir, speed, character):
        super().__init__(x, y, color, symbol, dir, speed)
        self.character = character

class Character(MovingObject):
    def __init__(self, x, y, color, symbol, dir, speed, arrows):
        super().__init__(x, y, color, symbol, dir, speed)
        self.arrows = arrows
