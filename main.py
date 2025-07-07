from ursina import *
import json
from ursina import *
import json

class PuzzleItem(Entity):
    def __init__(self, item_data, player=None):
        super().__init__()

        self.type = item_data.get('Type', 'Unknown')
        pos = item_data.get('Pos', '0 0 0')
        pos = [float(x) for x in pos.split()]
        self.position = Vec3(pos[0]/64, pos[2]/64, pos[1]/64)

        # Simple angle parsing
        angles = item_data.get('Angles', '0 0 0')
        angles = [float(x) for x in angles.split()]
        self.rotation = Vec3(angles[0], angles[1], angles[2])

        # Use lowercase type name for model/texture names
        self.model_name = f'{self.type.lower()}.obj'
        self.texture_name = f'{self.type.lower()}.png'

        self.model = self.model_name
        self.texture = self.texture_name

        self.collider = 'box'

        self.player = player  # For things that affect the player
class Button(PuzzleItem):
    def input(self, key):
        if self.hovered and key == 'left mouse down':
            print('Button pressed!')
            # Add logic here to open doors, etc.

class Cube(PuzzleItem):
    pass  # For now, just static. Later add carry logic.

class CubeDropper(PuzzleItem):
    def input(self, key):
        if self.hovered and key == 'left mouse down':
            print('Dropping a cube!')
            new_cube = Cube({
                'Type': 'Cube',
                'Pos': f'{self.x*64} {self.z*64} {self.y*64 + 64}',
                'Angles': '0 0 0'
            })

class ObservationWindow(PuzzleItem):
    pass  # Just static geometry

class EntryDoor(PuzzleItem):
    def open(self):
        print('Entry Door opened!')
        # Swap to open version if you have one

class ExitDoor(PuzzleItem):
    def open(self):
        print('Exit Door opened!')

class Door(PuzzleItem):
    def toggle(self):
        print('Door toggled!')

class AerialFaithPlate(PuzzleItem):
    def update(self):
        if self.intersects().hit and self.intersects().entity == self.player:
            print('Launch!')
            self.player.controller.velocity += Vec3(0, 20, 0)  # Yeet upward

class NonPortableSurface(PuzzleItem):
    pass

class PortableSurface(PuzzleItem):
    pass
class Player(Entity):
    def __init__(self):
        super().__init__()
        self.controller = FirstPersonController()
        self.controller.gravity = 0.5  # Adjust as needed

    def update(self):
        hit_info = self.controller.intersects()
        if hit_info.hit:
            pass  # Add portal checks later
app = Ursina()

# Load level.json
with open('level.json') as f:
    items = json.load(f)

player = Player()

for item in items:
    t = item.get('Type')
    if t == 'ItemButton':
        Button(item)
    elif t == 'ItemCube':
        Cube(item)
    elif t == 'ItemCubeDropper':
        CubeDropper(item)
    elif t == 'ItemObservationRoom':
        ObservationWindow(item)
    elif t == 'ItemEntryDoor':
        EntryDoor(item)
    elif t == 'ItemExitDoor':
        ExitDoor(item)
    elif t == 'ItemPanel':
        Door(item)
    elif t == 'ItemFaithPlate':
        AerialFaithPlate(item, player=player.controller)
    elif t == 'ItemNonPortableSurface':
        NonPortableSurface(item)
    elif t == 'ItemPortableSurface':
        PortableSurface(item)
    else:
        print(f'Unknown item type: {t}')

Sky()
app.run()

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

