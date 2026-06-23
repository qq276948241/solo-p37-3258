# 像素地下城探险 — 项目架构文档

## 1. 项目概览

基于 `pygame` 的 Roguelike 像素风 2D 地下城探险游戏，窗口 800×600，60 FPS。
核心玩法：逐层往下探索随机生成的地下城，打史莱姆/骷髅/BOSS，捡金币血瓶，买装备升级。

**入口文件**：[main.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/main.py#L322-L334)
```python
game = Game()
game.run()
```

---

## 2. 主循环三阶段（Game.run）

一切从 `Game.run()` 开始，每一帧严格按顺序执行三步：

```
每帧 (60 FPS)
├── 1. handle_events()   # 处理键盘/鼠标事件（按键按下、关闭窗口等）
├── 2. update()          # 更新游戏世界状态（移动、AI、碰撞、掉落…）
└── 3. draw()            # 渲染所有图层到屏幕
    └── clock.tick(FPS)  # 锁帧 60
```

三种游戏状态由 `Game.state` 控制：`'playing'` / `'shop'` / `'game_over'`，
决定了 `handle_events()` 和 `update()` 中实际执行的分支。

---

## 3. 模块职责与调用关系

### 3.1 模块一览

| 模块 | 主要类/函数 | 职责 | 被谁调用 |
|---|---|---|---|
| [constants.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/constants.py) | `MONSTER_CONFIGS`、颜色、尺寸等常量 | 所有可调数值的**唯一数据源** | 所有模块 |
| [game_map.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/game_map.py) | `GameMap`、`Rect` | 地图生成、瓦片查询、FOV 视野、已探索标记 | `Game` |
| [player.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/player.py) | `Player`、`Arrow` | 玩家移动、近战、射箭、受伤、回血、绘制 | `Game` |
| [monster.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/monster.py) | `BaseMonster`、`Slime`、`Skeleton`、`Boss` | 怪物 AI、攻击、碰撞、绘制 | `Game` |
| [items.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/items.py) | `Item`、`create_drops()`、`check_item_pickup()` | 金币/血瓶/箭矢/弓的绘制、掉落生成、拾取 | `Game` |
| [shop.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/shop.py) | `Shop` | 商店老板绘制、商店面板输入/购买逻辑 | `Game` |
| [ui.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/ui.py) | `draw_ui()`、`draw_minimap()`、`draw_floor_notice()` | HUD（血条/金币/层数）、小地图、楼层提示 | `Game.draw()` |
| [game_over.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/game_over.py) | `GameOverScreen` | 死亡结算面板绘制与点击重开 | `Game` |
| [main.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/main.py) | `Game` | **顶层编排器**：串起所有模块、主循环、相机、伤害数字 | 入口 |

### 3.2 调用方向（单向依赖）

```
                    constants.py (被所有人 import)
                         ↑
main.py ──→  game_map.py  player.py  monster.py  items.py  shop.py  ui.py  game_over.py
  │            │           │           │           │         │        │       │
  └──编排──────┴───────────┴───────────┴───────────┴─────────┴────────┴───────┘

注意：子模块之间**互不直接调用**，全部通过 main.py 的 Game 类中转。
     例如怪物死亡 → 掉落物品：不是 monster 调 items，而是 Game.update()
     检测到 monster.alive=False，然后调用 create_drops(monster)。
```

---

## 4. 关键流程详解

### 4.1 地图随机生成流程

**触发时机**：`Game.new_game()` 和 `Game.next_floor()` 中调用 `game_map.generate(floor)`

**入口**：[GameMap.generate()](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/game_map.py#L75-L145)

```
generate(floor)
├── 1. 清空 tiles[][] 为全墙 (1)
├── 2. 随机生成房间（最多 MAX_ROOMS=8 个，尝试 100 次）
│   ├── 随机宽高 (ROOM_MIN_SIZE~ROOM_MAX_SIZE)
│   ├── 随机位置
│   ├── 与已有房间做 intersect 碰撞检测 → 不重叠才保留
│   └── 与上一个房间连通：随机先横后竖 或 先竖后横 挖走廊
│
├── 3. place_doors()  — 走廊两端有墙堵住的位置放门 tile type=2
│
├── 4. 标记商店房间（第 2~倒数第 2 间随机选 1 间），地板改 type=3
│
├── 5. 若 floor % 3 == 0（BOSS 层）
│   ├── 最后一个房间改为 BOSS 房，地板改 type=5
│   ├── 记录 boss_spawn_pos（房间中心）
│   ├── stairs_active = False（BOSS 死后才激活）
│   └── 楼梯仍放在 BOSS 房中心（type=4）
│
└── 6. 非 BOSS 层，楼梯直接放在最后一个房间中心，stairs_active = True
```

**瓦片数字含义**：
| 值 | 含义 | 颜色 |
|---|---|---|
| 0 | 普通地板 | 深棕 |
| 1 | 墙 | 棕色 |
| 2 | 门（可通过） | 木色+黄门把手 |
| 3 | 商店地板 | 紫色 |
| 4 | 楼梯 | 灰蓝色横线 |
| 5 | BOSS 房地板 | 暗红色 |

---

### 4.2 FOV 视野系统

**触发时机**：`Game.update()` 每帧调用 `game_map.compute_fov(px, py, radius=8)`

两层位图标记：
- `visible[][]`：当前帧玩家能否直接看见（实时）
- `explored[][]`：历史上是否曾被看见（永久）

**渲染时的色彩策略**（见 `Game.draw_map()`）：
```
if explored[col][row]:
    color = 正常颜色 if visible[col][row] else 颜色 // 2（半暗）
else:
    完全不画（全黑）
```

怪物/物品也只在 `visible` 的瓦片上才绘制，避免穿墙看见。

---

### 4.3 怪物刷新与 AI

**刷新时机**：`Game.spawn_monsters()`，在 `new_game()` / `next_floor()` 时被调用一次

```
spawn_monsters()
├── 遍历所有房间（跳过起点房、商店房、BOSS 房）
│   ├── 每间房随机 1~3+floor//2 只怪
│   ├── floor<3:  Slime:Slime:Skeleton = 2:1
│   └── floor>=3: Slime:Skeleton:Skeleton = 1:2
│
└── 若 BOSS 层 → 在 boss_spawn_pos 生成一只 Boss(floor)
```

**AI 更新链路**（每帧在 `Game.update()`）：
```
对每只 monster：
  if visible[monster.tile_xy] 或 距离玩家 < 4 格:
      monster.update(player, game_map, monsters)
          ↓
      BaseMonster.update()
      ├── hit_flash 倒计时（受击闪烁）
      ├── update_special() ← Boss override 它实现冲锋
      │
      ├── if dist < aggro_range:  追击玩家
      │   ├── 归一化方向向量
      │   └── _try_move() 做 AABB 瓦片碰撞（检测四角 tile 是否为墙）
      │
      └── else: 随机巡逻
          ├── 每 30~90 帧换一次随机方向
          └── 同样 _try_move()
      ↓
  monster.try_attack(player)
      └── 圆-圆碰撞：dist < 怪物半径 + 玩家半径
          → player.take_damage(atk)
```

---

### 4.4 攻击系统与伤害传播

玩家有两种攻击，入口在 `Game.handle_events()` 的 KEYDOWN：

```
按 J / 空格 → player.attack_melee(monsters)
    ├── 冷却判定 (ATTACK_COOLDOWN=300ms)
    ├── 攻击中心 = 玩家中心 + 朝向 × ATTACK_RANGE × 0.6
    ├── 对每只怪：
    │   if 圆心距 < ATTACK_RANGE + monster.size//2 （两圆相交）
    │       damage = max(1, atk - monster.df)
    │       monster.take_damage(damage)
    │       Game 记录伤害数字（飘字）
    │       if not monster.alive:  player.total_kills++
    └── 攻击动画标记（player.attack_timer = 200ms）

按 K → player.shoot_arrow()
    ├── 冷却判定
    ├── 检查 has_bow && arrows > 0
    └── 返回一个 Arrow 对象，加入 Game.arrows[] 列表
```

**箭矢每帧更新**（Game.update()）：
```
arrow.update()       → 沿方向飞，撞墙则 active=False
→ 对每只怪做命中检测（dist < monster.size//2 + 4）
  → monster.take_damage()
  → 若怪死：create_drops(monster) 生成掉落物
```

---

### 4.5 物品掉落与拾取

**掉落触发**：两个位置
1. `Game.update()` 中箭矢击杀怪时
2. `Game.update()` 中统一遍历：`monster.alive==False && !_dropped` → `create_drops(monster)`

**掉落规则**统一在 [items.py:create_drops()](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/items.py#L54-L82)：
```
普通怪：
  └── 必掉 1 份金币（gold_min ~ gold_max）
  └── 30% 掉血瓶、20% 掉箭矢、5% 掉弓

BOSS：
  └── 必掉 1 份大量金币
  └── 必掉 2+floor//2 个血瓶（散开 2 格范围）
  └── 50% 掉 5~10 支箭矢
```

**拾取**：每帧 `check_item_pickup(player, items)`
→ 距离 < TILE_SIZE → 按 type 加金币/加血/加箭/给弓

---

### 4.6 玩家输入处理链路

两种输入方式分不同位置处理：

| 输入方式 | 处理位置 | 原因 |
|---|---|---|
| **按下类事件**（J/K/E/./ESC/R/鼠标点击） | `Game.handle_events()` 的 KEYDOWN / MOUSEBUTTONDOWN | 需要"单次触发"语义，不能 60 次/秒重复 |
| **持续按住类**（WASD / 方向键移动） | `Game.update()` 的 `pygame.key.get_pressed()` | 需要"按住就一直走"的连续语义 |

```
事件流向：
pygame.event.get()
    └──→ Game.handle_events()
         ├── state == 'game_over' → GameOverScreen.handle_click / R键重开
         ├── state == 'shop'      → Shop.handle_input() （上下选/空格买/ESC退）
         └── state == 'playing'
              ├── J/空格 → player.attack_melee()
              ├── K      → player.shoot_arrow()
              ├── E      → 在商店房内 → state = 'shop'
              └── .      → 在楼梯上且激活 → next_floor()
```

---

### 4.7 渲染分层（从下到上）

`Game.draw()` 中的绘制顺序决定覆盖关系，**下面的图层覆盖上面的**：

| 层号 | 内容 | 绘制位置 | 可见性判定 |
|---|---|---|---|
| 1 | 地图瓦片（墙/地板/门/楼梯/商店/BOSS房） | `Game.draw_map()` | `explored[][]` + `visible[][]` 调暗 |
| 2 | 地面物品（金币/血瓶/箭矢/弓） | `Item.draw()` | `visible[][]` |
| 3 | 怪物 | `monster.draw()` | `visible[][]` |
| 4 | 飞行中的箭矢 | `Arrow.draw()` | 总是可见 |
| 5 | 玩家 | `Player.draw()` | 总是可见（无敌帧闪烁） |
| 6 | 商店老板 | `Shop.draw_keeper()` | 总是可见（站在商店中心） |
| 7 | 伤害数字飘字 | 动态 `blit` | life>0 |
| 8 | HUD（顶部血条/金币/层数/属性） | `draw_ui()` | 屏幕坐标（不随相机） |
| 9 | 小地图（右下） | `draw_minimap()` | 屏幕坐标 |
| 10 | 楼层进入提示（中央） | `draw_floor_notice()` | 屏幕坐标，120 帧淡出 |
| 11 | 楼梯/商店交互提示（玩家头顶） | `Game.draw()` 末尾 | 玩家距离 <1 格才显示 |
| 12 | 商店面板 / 死亡结算（全屏遮罩+对话框） | `Shop.draw_panel()` / `GameOverScreen.draw()` | state 判定 |

**相机系统**：
- 相机 = 玩家在世界中的位置 − 屏幕中心
- clamp 到地图边界，避免看到地图外的黑边
- 世界 → 屏幕：`screen_xy = world_xy − camera_xy + (0, UI_HEIGHT)`

---

### 4.8 状态机

三个状态的转换关系：

```
           死亡(hp<=0)
playing ─────────────────→ game_over
   │  ↑                        │
   │  │  点击按钮/按R          │  new_game()
   │  └────────────────────────┘
   │
   │  E键(在商店房内)      ESC/E键
   └───────────────→ shop ────────────┘
```

| 状态 | handle_events 行为 | update 行为 |
|---|---|---|
| `playing` | 移动/攻击/开商店/下楼梯 | 全部游戏逻辑执行 |
| `shop` | 交给 Shop.handle_input | **return 跳过**（游戏世界暂停） |
| `game_over` | 交给 GameOverScreen | **return 跳过**（游戏世界暂停） |

---

### 4.9 BOSS 机制

| 机制 | 实现位置 |
|---|---|
| 每 3 层触发 | `GameMap.generate()` 中 `is_boss_floor = (floor % 3 == 0)` |
| 楼梯初始未激活 | `GameMap.stairs_active = False`，下楼梯按键要检查它 |
| BOSS 死后激活楼梯 | `Game.update()`：`if is_boss_floor && !stairs_active && !any(m.is_boss)` → `stairs_active=True` |
| BOSS 冲锋 | `Boss.update_special()`：随机触发 60 帧的冲锋状态，速度 ×2.5，伤害 ×1.5 |
| 丰厚掉落 | `create_drops()` 的 BOSS 分支：多金币 + 多血瓶 + 可能多箭矢 |

---

## 5. 怪物系统设计（配置驱动 + 模板方法）

[monster.py](file:///d:/code/ai-prompt/solo-chrome-dev-F12/repos/repo37/project37/monster.py) 的架构是整个项目最值得复用的模式：

```
BaseMonster（所有通用代码）
│
├── _apply_config(config_key, floor)     ← 从 MONSTER_CONFIGS 读属性
│
├── update()                             ← 模板方法，不要 override
│   ├── hit_flash 倒计时
│   ├── update_special()       【钩子1】Boss 用它做冲锋
│   ├── 追击 / 巡逻 分支
│   └── _try_move()            （AABB 碰撞检测）
│
├── try_attack()                       ← 模板方法
│   ├── get_attack_cooldown()  【钩子2】冲锋时冷却更短
│   └── get_attack_damage()    【钩子3】冲锋时伤害×1.5
│
├── draw()                             ← 模板方法，不要 override
│   ├── draw_body()            【钩子4】子类各自画形状
│   └── draw_health_bar()      （Boss override 它，加名字和等级）
│
├── Slime      → 只写 draw_body()
├── Skeleton   → 只写 draw_body()
└── Boss       → override 所有 4 个钩子 + draw_health_bar()
```

**好处**：加第 4 种新怪物（比如蝙蝠）只需：
1. 在 `constants.py` 的 `MONSTER_CONFIGS` 加一条配置
2. 在 `monster.py` 加个 `class Bat(BaseMonster)`，实现 `draw_body()`
3. 在 `Game.spawn_monsters()` 里把它加进随机选择列表

---

## 6. 数据结构速查

### Game 实例持有的集合：
```python
self.monsters      # List[BaseMonster]  — 当前层所有活怪
self.items         # List[Item]         — 地面上的物品
self.arrows        # List[Arrow]        — 飞行中箭矢
self.damage_texts  # List[Dict]         — {x,y,text,color,life} 飘字
```

### GameMap 实例持有的关键属性：
```python
self.tiles         # List[List[int]]    # 50×40 瓦片数组 (0~5)
self.rooms         # List[Rect]         # 房间列表，rooms[0] 是起点
self.shop_room     # Rect / None
self.boss_room     # Rect / None
self.stairs_pos    # (col,row) / None
self.boss_spawn_pos# (col,row) / None
self.is_boss_floor # bool
self.stairs_active # bool               # BOSS 层需击杀后变 True
self.visible       # List[List[bool]]   # 实时 FOV
self.explored      # List[List[bool]]   # 永久记忆
```

### Player 属性：
```python
hp / max_hp       # 血量
atk / df          # 攻击 / 防御
gold              # 当前金币
arrows            # 箭矢数
has_bow           # 是否已捡弓
total_kills / total_gold / floor  # 结算用统计
```

---

## 7. 扩展指引

### 加一种新怪物
1. `constants.py` → `MONSTER_CONFIGS['bat'] = {...}`
2. `monster.py` → `class Bat(BaseMonster):` 实现 `draw_body()`
3. `main.py` → `Game.spawn_monsters()` 的 random.choice 里加入 Bat

### 加一种新物品
1. `constants.py` → 加颜色/数值常量
2. `items.py` → `Item.draw()` 里加新 type 的绘制
3. `items.py` → `check_item_pickup()` 加拾取效果
4. `create_drops()` 中加入掉落概率

### 加一种新装备（除商店外的掉落）
1. `player.py` → 加属性，比如 `has_helmet` 或 `crit_chance`
2. `items.py` → 加新物品 type + 拾取设置属性
3. `attack_melee()` / `shoot_arrow()` 里用新属性计算伤害

### 改地图尺寸 / 房间数量
→ 全部在 `constants.py`：`MAP_COLS`、`MAP_ROWS`、`MAX_ROOMS`、`ROOM_MIN_SIZE`、`ROOM_MAX_SIZE`

---

*文档生成时间：2026-06-23。代码结构稳定，新增功能优先考虑扩展子类和配置字典，避免修改基类。*
