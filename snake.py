import arcade
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Snake"

CELL_SIZE = 40
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

MOVE_INTERVAL = 0.06

UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def cell_center(col, row):
    x = col * CELL_SIZE + CELL_SIZE / 2
    y = row * CELL_SIZE + CELL_SIZE / 2
    return x, y


class SnakeGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.snake = []
        self.direction = RIGHT
        self.food = (0, 0)
        self.time_since_move = 0.0
        self.game_over = False
        self.score = 0

    def setup(self):
        cx = GRID_COLS // 2
        cy = GRID_ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.time_since_move = 0.0
        self.game_over = False
        self.score = 0
        self.place_food()

    def place_food(self):
        snake_set = set(self.snake)
        while True:
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            if (col, row) not in snake_set:
                self.food = (col, row)
                return

    def on_draw(self):
        arcade.start_render()

        fx, fy = cell_center(*self.food)
        arcade.draw_rectangle_filled(fx, fy, CELL_SIZE - 4, CELL_SIZE - 4, arcade.color.RED)

        for i, (col, row) in enumerate(self.snake):
            x, y = cell_center(col, row)
            color = arcade.color.LIME_GREEN if i == 0 else arcade.color.GREEN
            arcade.draw_rectangle_filled(x, y, CELL_SIZE - 2, CELL_SIZE - 2, color)

        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30,
                         arcade.color.WHITE, 18)

        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20,
                             arcade.color.WHITE, 50, anchor_x="center")
            arcade.draw_text("Press R to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30,
                             arcade.color.WHITE, 20, anchor_x="center")

    def on_update(self, delta_time):
        if self.game_over:
            return
        self.time_since_move += delta_time
        if self.time_since_move < MOVE_INTERVAL:
            return
        self.time_since_move = 0.0

        self.direction = 
        head_col, head_row = self.snake[0]
        dcol, drow = self.direction
        new_head = (head_col + dcol, head_row + drow)

        if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                new_head[1] < 0 or new_head[1] >= GRID_ROWS):
            self.game_over = True
            return

        if new_head in self.snake[:-1]:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()

    # def on_key_press(self, key, modifiers):
    #     if self.game_over:
    #         if key == arcade.key.R:
    #             self.setup()
    #         return

    #     if key == arcade.key.W and self.direction != DOWN:
    #         self.pending_direction = UP
    #     elif key == arcade.key.S and self.direction != UP:
    #         self.pending_direction = DOWN
    #     elif key == arcade.key.A and self.direction != RIGHT:
    #         self.pending_direction = LEFT
    #     elif key == arcade.key.D and self.direction != LEFT:
    #         self.pending_direction = RIGHT


def main():
    game = SnakeGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
