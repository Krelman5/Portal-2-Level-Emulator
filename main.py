from ursina import *
import json

class PuzzleItem(Entity):
    def __init__(self, item_data, player=None):
        super().__init__()

        self.id = item_data.get('ID', 'Unknown')  # Unique ID to link signals
        self.type = item_data.get('Type', 'Unknown')
        self.state = 'off'

        pos = item_data.get('Pos', '0 0 0')
        pos = [float(x) for x in pos.split()]
        # Assume 1 Blender unit = 1 tile, so scale by your tile size
        tile_size = 1  # 1 means no scaling, adjust if needed
        self.position = Vec3(pos[0] * tile_size, pos[2] * tile_size, pos[1] * tile_size)

        # Swap Y/Z for Source ➜ Ursina axes
        angles = item_data.get('Angles', '0 0 0')
        angles = [float(x) for x in angles.split()]
        self.rotation = Vec3(angles[0], angles[1], angles[2])

        self.model_name = f'{self.type.lower()}'
        self.model = f'{self.model_name}_off.obj'
        self.texture = f'{self.model_name}.png'
        self.collider = 'box'

        self.connections = []  # List of connected PuzzleItem objects
        self.player = player

    def toggle(self):
        if self.state == 'off':
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        self.state = 'on'
        self.model = f'{self.model_name}_on.obj'
        print(f'{self.id} turned ON')
        self.send_signal()

    def turn_off(self):
        self.state = 'off'
        self.model = f'{self.model_name}_off.obj'
        print(f'{self.id} turned OFF')

    def send_signal(self):
        for target in self.connections:
            target.receive_signal()

    def receive_signal(self):
        self.toggle()

# ---------------------------
# Specific Elements
# ---------------------------

class Button(PuzzleItem):
    def input(self, key):
        if self.hovered and key == 'left mouse down':
            self.toggle()

class Door(PuzzleItem):
    pass

class CubeDropper(PuzzleItem):
    def receive_signal(self):
        print(f'{self.id} dropping a cube!')
        Cube({'ID':'cubeX','Type':'ItemCube','Pos':f'{self.x} {self.z} {self.y+2}','Angles':'0 0 0'})
        # No on/off model swap needed

class Cube(PuzzleItem):
    pass

# ... add others like Faith Plate etc. the same way ...

# ---------------------------
# Player
# ---------------------------
class Player(Entity):
    def __init__(self):
        super().__init__()
        self.controller = FirstPersonController()
        self.controller.gravity = 0.5

# ---------------------------
# Load Level + Connections
# ---------------------------
app = Ursina()

with open('level.json') as f:
    items_data = json.load(f)

player = Player()
all_items = {}

# Spawn all puzzle items
for item_data in items_data:
    t = item_data.get('Type')
    if t == 'ItemButton':
        item = Button(item_data)
    elif t == 'ItemDoor':
        item = Door(item_data)
    elif t == 'ItemCubeDropper':
        item = CubeDropper(item_data)
    elif t == 'ItemCube':
        item = Cube(item_data)
    else:
        item = PuzzleItem(item_data)

    all_items[item_data.get('ID')] = item

# Example: manual connections
# You'd parse this from level.json ideally
# Here we hardcode: Button1 opens Door1 and activates Dropper1
all_items['Button1'].connections.append(all_items['Door1'])
all_items['Button1'].connections.append(all_items['Dropper1'])

Sky()
app.run()

