import random
from constants import *


class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    def intersect(self, other):
        return (self.left <= other.right and self.right >= other.left and
                self.top <= other.bottom and self.bottom >= other.top)


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[1 for _ in range(height)] for _ in range(width)]
        self.rooms = []
        self.doors = []
        self.explored = [[False for _ in range(height)] for _ in range(width)]
        self.visible = [[False for _ in range(height)] for _ in range(width)]
        self.stairs_pos = None
        self.shop_room = None
        self.boss_room = None
        self.is_boss_floor = False
        self.stairs_active = True
        self.boss_spawn_pos = None

    def is_wall(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.tiles[x][y] == 1

    def is_door(self, x, y):
        return (x, y) in self.doors

    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.tiles[x][y] in [0, 2, 3, 5]

    def create_room(self, room):
        for x in range(room.left, room.right):
            for y in range(room.top, room.bottom):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[x][y] = 0

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x][y] = 0

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x][y] = 0

    def place_doors(self):
        self.doors = []
        for room in self.rooms:
            cx, cy = room.center
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                checked = set()
                while 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) in checked:
                        break
                    checked.add((nx, ny))
                    if self.tiles[nx][ny] == 0:
                        neighbors_wall = 0
                        for ndx, ndy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nnx, nny = nx + ndx, ny + ndy
                            if 0 <= nnx < self.width and 0 <= nny < self.height:
                                if self.tiles[nnx][nny] == 1:
                                    neighbors_wall += 1
                        if neighbors_wall >= 2:
                            in_room = False
                            for r in self.rooms:
                                if r.left <= nx < r.right and r.top <= ny < r.bottom:
                                    in_room = True
                                    break
                            if not in_room and (nx, ny) not in self.doors:
                                self.tiles[nx][ny] = 2
                                self.doors.append((nx, ny))
                        break
                    nx += dx
                    ny += dy

    def generate(self, floor):
        self.tiles = [[1 for _ in range(self.height)] for _ in range(self.width)]
        self.rooms = []
        self.doors = []
        self.explored = [[False for _ in range(self.height)] for _ in range(self.width)]
        self.visible = [[False for _ in range(self.height)] for _ in range(self.width)]
        self.stairs_pos = None
        self.shop_room = None
        self.boss_room = None
        self.is_boss_floor = (floor % 3 == 0)
        self.stairs_active = not self.is_boss_floor
        self.boss_spawn_pos = None

        num_rooms = 0
        attempts = 0
        while num_rooms < MAX_ROOMS and attempts < 100:
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            new_room = Rect(x, y, w, h)

            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                if len(self.rooms) > 0:
                    prev = self.rooms[-1].center
                    curr = new_room.center
                    if random.randint(0, 1) == 0:
                        self.create_h_tunnel(prev[0], curr[0], prev[1])
                        self.create_v_tunnel(prev[1], curr[1], curr[0])
                    else:
                        self.create_v_tunnel(prev[1], curr[1], prev[0])
                        self.create_h_tunnel(prev[0], curr[0], curr[1])
                self.rooms.append(new_room)
                num_rooms += 1
            attempts += 1

        self.place_doors()

        if len(self.rooms) >= 2:
            max_shop_idx = len(self.rooms) - 2 if self.is_boss_floor else len(self.rooms) - 1
            if max_shop_idx >= 1:
                shop_idx = random.randint(1, max_shop_idx)
                self.shop_room = self.rooms[shop_idx]
                for x in range(self.shop_room.left, self.shop_room.right):
                    for y in range(self.shop_room.top, self.shop_room.bottom):
                        if 0 <= x < self.width and 0 <= y < self.height and self.tiles[x][y] == 0:
                            self.tiles[x][y] = 3

        if len(self.rooms) > 0:
            if self.is_boss_floor and len(self.rooms) >= 2:
                self.boss_room = self.rooms[-1]
                for x in range(self.boss_room.left, self.boss_room.right):
                    for y in range(self.boss_room.top, self.boss_room.bottom):
                        if 0 <= x < self.width and 0 <= y < self.height and self.tiles[x][y] == 0:
                            self.tiles[x][y] = 5
                bx, by = self.boss_room.center
                self.boss_spawn_pos = (bx, by)
                stairs_room = self.boss_room
            else:
                stairs_room = self.rooms[-1]

            sx, sy = stairs_room.center
            if 0 <= sx < self.width and 0 <= sy < self.height:
                self.tiles[sx][sy] = 4
                self.stairs_pos = (sx, sy)

    def get_random_floor_tile(self, room=None):
        if room is None:
            room = random.choice(self.rooms)
        attempts = 0
        while attempts < 50:
            x = random.randint(room.left + 1, room.right - 2)
            y = random.randint(room.top + 1, room.bottom - 2)
            if 0 <= x < self.width and 0 <= y < self.height and self.tiles[x][y] in [0, 3, 5]:
                return (x, y)
            attempts += 1
        return room.center

    def compute_fov(self, px, py, radius=8):
        for x in range(self.width):
            for y in range(self.height):
                self.visible[x][y] = False
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    x, y = px + dx, py + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        if self._has_line_of_sight(px, py, x, y):
                            self.visible[x][y] = True
                            self.explored[x][y] = True

    def _has_line_of_sight(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if x0 == x1 and y0 == y1:
                return True
            if self.is_wall(x0, y0):
                return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
