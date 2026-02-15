import pygame
import random

# 测试git而使用的注释22

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]


class Tetromino:
    def __init__(self):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        # 顺时针旋转90度
        self.shape = [[self.shape[j][i] for j in range(len(self.shape) - 1, -1, -1)]
                      for i in range(len(self.shape[0]))]


class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('俄罗斯方块')
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 500  # 毫秒

    def check_collision(self, piece, offset_x=0, offset_y=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + offset_x
                    new_y = piece.y + y + offset_y
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + y
                    grid_x = self.current_piece.x + x
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece.color

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                y -= 1

        if lines_cleared > 0:
            self.score += lines_cleared * 100

    def move(self, dx, dy):
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        old_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            self.current_piece.shape = old_shape

    def get_ghost_y(self):
        """计算方块最终会落到的Y坐标"""
        ghost_y = self.current_piece.y
        while not self.check_collision(self.current_piece, 0, ghost_y - self.current_piece.y + 1):
            ghost_y += 1
        return ghost_y

    def draw_grid(self):
        # 绘制交替背景色的列
        for x in range(GRID_WIDTH):
            if x % 2 == 1:  # 奇数列用深色背景
                pygame.draw.rect(self.screen, (20, 20, 20),
                               (x * BLOCK_SIZE, 0, BLOCK_SIZE, SCREEN_HEIGHT))

        # 绘制已放置的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x],
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                   ((piece.x + x) * BLOCK_SIZE,
                                    (piece.y + y) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_ghost_piece(self):
        """绘制半透明的方块最终落点"""
        ghost_y = self.get_ghost_y()

        # 创建半透明表面
        ghost_surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        ghost_surface.set_alpha(80)  # 设置透明度 (0-255)
        ghost_color = self.current_piece.color
        ghost_surface.fill(ghost_color)

        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.screen.blit(ghost_surface,
                                   ((self.current_piece.x + x) * BLOCK_SIZE,
                                    (ghost_y + y) * BLOCK_SIZE))

    def draw_text(self, text, size, x, y):
        font = pygame.font.SysFont('microsoftyahei,simsun,simhei', size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def run(self):
        running = True
        down_pressed = False
        down_press_time = 0
        left_move_time = 0
        right_move_time = 0
        left_initial_delay_done = False
        right_initial_delay_done = False
        initial_delay = 300  # 首次长按延迟（毫秒）
        move_delay = 100  # 持续移动间隔（毫秒）
        while running:
            self.fall_time += self.clock.get_rawtime()
            raw_time = self.clock.get_rawtime()
            self.clock.tick()

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move(-1, 0)
                        left_move_time = 0
                        left_initial_delay_done = False
                    elif event.key == pygame.K_RIGHT:
                        self.move(1, 0)
                        right_move_time = 0
                        right_initial_delay_done = False
                    elif event.key == pygame.K_DOWN:
                        self.move(0, 1)
                        down_pressed = True
                        down_press_time = 0
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        while self.move(0, 1):
                            pass

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        down_pressed = False
                        down_press_time = 0
                    elif event.key == pygame.K_LEFT:
                        left_move_time = 0
                        left_initial_delay_done = False
                    elif event.key == pygame.K_RIGHT:
                        right_move_time = 0
                        right_initial_delay_done = False

            # 检测按键长按
            if not self.game_over:
                keys = pygame.key.get_pressed()

                # ↓键长按
                if keys[pygame.K_DOWN] and down_pressed:
                    down_press_time += raw_time
                    if down_press_time >= 200:  # 长按超过200毫秒
                        while self.move(0, 1):
                            pass
                        down_pressed = False
                        down_press_time = 0

                # ←键长按
                if keys[pygame.K_LEFT]:
                    left_move_time += raw_time
                    if not left_initial_delay_done:
                        if left_move_time >= initial_delay:
                            left_initial_delay_done = True
                            left_move_time = 0
                    else:
                        if left_move_time >= move_delay:
                            self.move(-1, 0)
                            left_move_time = 0

                # →键长按
                if keys[pygame.K_RIGHT]:
                    right_move_time += raw_time
                    if not right_initial_delay_done:
                        if right_move_time >= initial_delay:
                            right_initial_delay_done = True
                            right_move_time = 0
                    else:
                        if right_move_time >= move_delay:
                            self.move(1, 0)
                            right_move_time = 0

            # 自动下落
            if self.fall_time >= self.fall_speed and not self.game_over:
                self.fall_time = 0
                if not self.move(0, 1):
                    self.merge_piece()
                    self.clear_lines()
                    self.current_piece = Tetromino()
                    if self.check_collision(self.current_piece):
                        self.game_over = True

            # 绘制
            self.screen.fill(BLACK)
            self.draw_grid()
            if not self.game_over:
                self.draw_ghost_piece()  # 先绘制半透明的最终位置
                self.draw_piece(self.current_piece)  # 再绘制当前方块

            # 显示分数
            self.draw_text(f'分数: {self.score}', 30, SCREEN_WIDTH // 2, 10)

            if self.game_over:
                self.draw_text('游戏结束!', 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.draw_text('按ESC退出', 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

            pygame.display.flip()

            # 游戏结束后按ESC退出
            if self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    running = False

        pygame.quit()


if __name__ == '__main__':
    game = TetrisGame()
    game.run()
