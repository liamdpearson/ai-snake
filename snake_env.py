import random
import numpy as np
import edit_file as ef

GRID_COLS = 20
GRID_ROWS = 20

UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UPRIGHT = (1, 1)
DOWNRIGHT = (1, -1)
DOWNLEFT = (-1, -1)
UPLEFT = (-1, 1)

CARDINAL_DIRS = [UP, RIGHT, DOWN, LEFT]
DIRECTIONS = [UP, UPRIGHT, RIGHT, DOWNRIGHT, DOWN, DOWNLEFT, LEFT, UPLEFT]

OBS_DIM = 28
NUM_ACTIONS = 3  # 0 = turn left, 1 = straight, 2 = turn right

FOOD_REWARD = 15
DEATH_REWARD = -7.5
TOWARDS_REWARD = 0.09
AWAY_REWARD = -0.16


class SnakeEnv():
    def __init__(self):
        self.snake = []
        self.direction = RIGHT
        self.food = (0, 0)
        self.game_over = False
        self.score = 0

    def reset(self):
        cx = GRID_COLS // 2
        cy = GRID_ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.game_over = False
        self.score = 0
        self.steps_since_food = 0
        self.place_food()
        return self._observe()

    def place_food(self):
        snake_set = set(self.snake)
        while True:
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            if (col, row) not in snake_set:
                self.food = (col, row)
                return

    def step(self, action):
        if self.game_over:
            return self._observe(), 0.0, True
        
        self.steps_since_food += 1

        shift = action - 1
        new_dir_idx = (CARDINAL_DIRS.index(self.direction) + shift) % 4
        self.direction = CARDINAL_DIRS[new_dir_idx]

        head_col, head_row = self.snake[0]
        dcol, drow = self.direction
        new_head = (head_col + dcol, head_row + drow)

        if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                new_head[1] < 0 or new_head[1] >= GRID_ROWS):
            self.game_over = True
            return self._observe(), DEATH_REWARD, True

        if new_head in self.snake[:-1]:
            self.game_over = True
            return self._observe(), DEATH_REWARD, True

        self.snake.insert(0, new_head)

        fx, fy = self.food
        old_dist = abs(head_col-fx) + abs(head_row-fy)   # before moving
        new_dist = abs(new_head[0]-fx) + abs(new_head[1]-fy)
        reward = TOWARDS_REWARD if new_dist < old_dist else AWAY_REWARD


        if new_head == self.food:
            self.score += 1
            reward = FOOD_REWARD
            self.place_food()
            self.steps_since_food = 0
        else:
            self.snake.pop()

        return self._observe(), reward, False

    def _observe(self):
        obs = np.zeros((OBS_DIM, 1))
        head = self.snake[0]
        for i, dir in enumerate(DIRECTIONS):
            wall_found = False
            distance = 1
            while not wall_found:
                x = head[0] + distance * dir[0]
                y = head[1] + distance * dir[1]
                cur_check = (x, y)
                if cur_check == self.food:
                    obs[3*i, 0] = 1
                if cur_check in self.snake:
                    obs[3*i + 1, 0] = 1
                    break
                if x >= GRID_COLS or x < 0 or y >= GRID_ROWS or y < 0:
                    obs[3*i + 2, 0] = 1/distance
                    wall_found = True
                distance += 1

        obs[24 + CARDINAL_DIRS.index(self.direction), 0] = 1
        return obs


def main():
    env = SnakeEnv()
    env.reset()


if __name__ == "__main__":
    main()
