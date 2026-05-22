import arcade
import numpy as np
import math

from snake_env import SnakeEnv, GRID_COLS, GRID_ROWS, NUM_ACTIONS
from nn import SnakeAI
import edit_file as ef

CELL_SIZE = 50
SCREEN_WIDTH = GRID_COLS * CELL_SIZE
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE
SCREEN_TITLE = "Snake Viewer"


def cell_center(col, row):
    x = col * CELL_SIZE + CELL_SIZE / 2
    y = row * CELL_SIZE + CELL_SIZE / 2
    return x, y


class SnakeViewer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.env = SnakeEnv()
        self.ai = SnakeAI()
        self.env.reset()
        self.time_since_move = 0.0
        self.move_interval = 0.0
        self.paused = False
        self.training = False
        self.steps_taken, self.high_score = ef.load_data()
        self.ai.epsilon = 0 # chance to make random move

    def select_action(self):
        X = self.env._observe()
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

        arcade.draw_text(f"Score: {self.env.score}", 8, SCREEN_HEIGHT - 22,
                         arcade.color.WHITE, 14)
        
        arcade.draw_text(f"High Score: {self.high_score}", 8, SCREEN_HEIGHT - 42,
                         arcade.color.WHITE, 14)
        
        arcade.draw_text(f"Total Steps Taken: {self.steps_taken}", 8, SCREEN_HEIGHT - 62,
                         arcade.color.WHITE, 14)
        
        arcade.draw_text(f"Force Random Timer: {int(self.env.steps_since_food*100/(10*len(self.env.snake)))}%", 8, SCREEN_HEIGHT - 82,
                         arcade.color.WHITE, 14)
        
        arcade.draw_text(f"Move Interval: {self.move_interval} seconds", 8, SCREEN_HEIGHT - 102,
                         arcade.color.WHITE, 14)
        
        arcade.draw_text(f"Epsilon: {self.ai.epsilon}", 8, SCREEN_HEIGHT - 122,
                         arcade.color.WHITE, 14)
        
        arcade.draw_text("State: Training(T to toggle)" if self.training else "State: Testing(T to toggle)", 8, SCREEN_HEIGHT - 152,
                         arcade.color.WHITE, 14)

        if self.paused and not self.env.game_over:
            arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.WHITE, 36, anchor_x="center")

        if self.env.game_over:
            arcade.draw_text("Dead", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 16,
                             arcade.color.RED, 40, anchor_x="center")

    def on_update(self, delta_time):
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
            self.ai.epsilon = 0.005+0.95*math.e**(-0.00001*self.steps_taken)
        else:
            self.ai.epsilon = 0

        if self.env.steps_since_food > 10 * len(self.env.snake):
            self.ai.epsilon = 1.01
            self.env.steps_since_food = 0

        if self.env.score > self.high_score:
            self.high_score = self.env.score
            ef.replace_high_score(self.high_score)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        
        if key == arcade.key.T:
            self.training = not self.training

        if key == arcade.key.UP:
            self.move_interval += 0.01

        if key == arcade.key.DOWN:
            self.move_interval -= 0.01
            if self.move_interval < 0:
                self.move_interval = 0
    
    def on_close(self):
        self.ai.save_weights()
        ef.replace_steps_taken(self.steps_taken)
        super().on_close()


def main():
    SnakeViewer()
    arcade.run()


if __name__ == "__main__":
    main()
