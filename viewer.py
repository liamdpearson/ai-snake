import arcade
import numpy as np
import math

from snake_env import SnakeEnv, GRID_COLS, GRID_ROWS, NUM_ACTIONS, DIRECTIONS
from nn import SnakeAI
import edit_file as ef

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()

CELL_SIZE = SCREEN_WIDTH//50
FONT_SIZE = SCREEN_WIDTH//150
SNAKE_WIDTH = GRID_COLS * CELL_SIZE
SNAKE_HEIGHT = GRID_ROWS * CELL_SIZE
SCREEN_TITLE = "Snake Viewer"


def cell_center(col, row):
    x = col * CELL_SIZE + CELL_SIZE / 2
    y = (row * CELL_SIZE + CELL_SIZE / 2) + SCREEN_HEIGHT - SNAKE_HEIGHT
    return x, y


class SnakeViewer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
        arcade.set_background_color(arcade.color.BLACK)
        self.set_location(0,0)
        self.env = SnakeEnv()
        self.ai = SnakeAI()
        self.env.reset()
        self.time_since_move = 0.0
        self.move_interval = 0.1
        self.paused = False
        self.training = False
        self.show_nn = False
        self.steps_taken, self.high_score = ef.load_data()
        self.ai.epsilon = 0 # chance to make random move
        self.input_n_output = None
        self.pressed_keys = []

        self.init_draw_nn()

    def init_draw_nn(self):
        self.num_layers = 4

        self.region_left = SNAKE_WIDTH + CELL_SIZE
        self.region_right = SCREEN_WIDTH - CELL_SIZE
        self.region_top = SCREEN_HEIGHT - CELL_SIZE
        self.region_bottom = CELL_SIZE
        self.region_width = self.region_right - self.region_left
        self.region_height = self.region_top - self.region_bottom
        self.input_labels = ["Food", "Body", "Wall"] * 8 + ["Up", "Right", "Down", "Left", "Fatigue"]

        self.node_radius = min(self.region_height / 70,
                          self.region_width / 24)

        self.spacing = self.region_height / 29
        self.center_y = (self.region_top + self.region_bottom) / 2
        self.layer_positions = []
        for i, size in enumerate([29,20,12,3]):
            x = self.region_left + self.region_width * (i + 0.5) / self.num_layers
            layer_top = self.center_y + self.spacing * size / 2
            ys = [layer_top - self.spacing * (j + 0.5) for j in range(size)]
            self.layer_positions.append([(x, y) for y in ys])
        
        
    def draw_nn(self, W1, W2, W3):
        weights = [W1, W2, W3]
        for layer_idx in range(self.num_layers - 1):
            W = weights[layer_idx]
            for from_idx, (fx, fy) in enumerate(self.layer_positions[layer_idx]):
                for to_idx, (tx, ty) in enumerate(self.layer_positions[layer_idx + 1]):
                    color = arcade.color.BLUE if W[to_idx, from_idx] >= 0 else arcade.color.RED
                    arcade.draw_line(fx, fy, tx, ty, color, 1)

        for positions in self.layer_positions:
            for x, y in positions:
                arcade.draw_circle_filled(x, y, self.node_radius, arcade.color.WHITE)
                arcade.draw_circle_outline(x, y, self.node_radius, arcade.color.BLACK, 1)

        if self.input_n_output:
            input = self.input_n_output[0]
            output = self.input_n_output[1]

            for i, pos in enumerate(self.layer_positions[0]):
                if input[i] != 0:
                    arcade.draw_circle_filled(pos[0], pos[1], self.node_radius-5, arcade.color.GREEN)

            arcade.draw_circle_filled(self.layer_positions[-1][output][0], self.layer_positions[-1][output][1], self.node_radius-5, arcade.color.GREEN)

            arcade.draw_text("Left", self.layer_positions[-1][0][0] + FONT_SIZE*2, self.layer_positions[-1][0][1] - FONT_SIZE/2,
                         arcade.color.WHITE, FONT_SIZE)
            
            arcade.draw_text("Straight", self.layer_positions[-1][1][0] + FONT_SIZE*2, self.layer_positions[-1][1][1] - FONT_SIZE/2,
                         arcade.color.WHITE, FONT_SIZE)
            
            arcade.draw_text("Right", self.layer_positions[-1][2][0] + FONT_SIZE*2, self.layer_positions[-1][2][1] - FONT_SIZE/2,
                         arcade.color.WHITE, FONT_SIZE)

            for i, pos in enumerate(self.layer_positions[0]):
                if i < len(self.input_labels):
                    arcade.draw_text(self.input_labels[i], pos[0] - FONT_SIZE*2, pos[1] - FONT_SIZE/2,
                                 arcade.color.WHITE, FONT_SIZE, anchor_x="right")
                    if self.input_labels[i] in ("Wall", "Left"):
                        line_y = pos[1] - self.spacing / 2
                        arcade.draw_line(1145, line_y, 1245, line_y, arcade.color.WHITE, 1)
    

    def draw_snake_sight(self):
        hx, hy = cell_center(*self.env.snake[0])
        for dcol, drow in DIRECTIONS:
            arcade.draw_line(hx, hy, hx + dcol * 1500, hy + drow * 1500,
                             arcade.color.RED, 1)


    def select_action(self):
        X = self.env.observe()
        if np.random.rand() < self.ai.epsilon:
            action = np.random.randint(NUM_ACTIONS)
        else:
            action = self.ai.get_ai_output(X)
        
        return X, action


    def on_draw(self):
        arcade.start_render()

        fx, fy = cell_center(*self.env.food)
        arcade.draw_rectangle_filled(fx, fy, CELL_SIZE - 2, CELL_SIZE - 2, arcade.color.RED)

        for i, (col, row) in enumerate(self.env.snake):
            x, y = cell_center(col, row)
            color = arcade.color.LIME_GREEN if i == 0 else arcade.color.GREEN
            arcade.draw_rectangle_filled(x, y, CELL_SIZE - 1, CELL_SIZE - 1, color)

        arcade.draw_text(f"Score: {self.env.score}", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_text(f"High Score: {self.high_score}", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE*2.5 - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_text(f"Total Steps Taken: {self.steps_taken}", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE*4 - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_text(f"Fatigue: {int((self.env.steps_since_food*100)/(len(self.env.snake) * 60))}%", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE*5.5 - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_text(f"Move Interval: {self.move_interval} seconds(Arrow keys)", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE*7 - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_text(f"Epsilon: {self.ai.epsilon}", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE*8.5 - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_text("State: Training(T to toggle)" if self.training else "State: Testing(T to toggle)", 8, SCREEN_HEIGHT-SNAKE_HEIGHT - FONT_SIZE*10 - 5,
                         arcade.color.WHITE, FONT_SIZE)
        
        arcade.draw_rectangle_outline(SNAKE_WIDTH/2, SCREEN_HEIGHT - SNAKE_HEIGHT/2, SNAKE_WIDTH, SNAKE_HEIGHT, arcade.color.WHITE)

        if self.paused and not self.env.game_over:
            arcade.draw_text("PAUSED", SNAKE_WIDTH / 2, SCREEN_HEIGHT-SNAKE_HEIGHT / 2,
                             arcade.color.WHITE, FONT_SIZE*2, anchor_x="center")

        if self.env.game_over:
            arcade.draw_text("Dead", SNAKE_WIDTH / 2, SCREEN_HEIGHT-SNAKE_HEIGHT / 2 + 16,
                             arcade.color.RED, FONT_SIZE*2, anchor_x="center")
        
        if self.show_nn:
            self.draw_nn(self.ai.W1, self.ai.W2, self.ai.W3)


    def on_update(self, delta_time):
        if arcade.key.UP in self.pressed_keys:
            self.move_interval += 0.01

        if arcade.key.DOWN in self.pressed_keys:
            self.move_interval -= 0.01
            if self.move_interval < 0:
                self.move_interval = 0

        if self.paused:
            return
        if self.env.game_over:
            self.env.reset()
            self.time_since_move = 0.0
            self.paused = False
            return
        self.time_since_move += delta_time
        if self.time_since_move < self.move_interval:
            return
        self.time_since_move = 0.0

        X, action = self.select_action()
        self.input_n_output = (X, action)
        X_next, r, done = self.env.step(action)

        if self.training:
            self.ai.training_data.append((X, action, r, X_next, done))
            if len(self.ai.training_data) > 50000:
                self.ai.training_data.pop(0)
            self.ai.train()
            if self.steps_taken % 1000 == 0:
                self.ai.save_weights()
                ef.replace_steps_taken(self.steps_taken)
                if self.steps_taken % 50000 == 0:
                    print(self.high_score, self.steps_taken)
            self.steps_taken += 1
            self.ai.epsilon = 0.001+0.999*math.e**(-0.00001*self.steps_taken)
        else:
            self.ai.epsilon = 0

        if self.env.score > self.high_score:
            self.high_score = self.env.score
            ef.replace_high_score(self.high_score)

    def on_key_press(self, key, modifiers):
        self.pressed_keys.append(key)

        if key == arcade.key.SPACE:
            self.paused = not self.paused
        
        if key == arcade.key.T:
            self.training = not self.training

        if key == arcade.key.N:
            self.show_nn = not self.show_nn

    def on_key_release(self, key, modifiers):
        self.pressed_keys.remove(key)
    
    def on_close(self):
        self.ai.save_weights()
        ef.replace_steps_taken(self.steps_taken)
        super().on_close()


def main():
    SnakeViewer()
    arcade.run()


if __name__ == "__main__":
    main()
