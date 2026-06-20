# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Run

- Play / train: `python viewer.py` — opens a fullscreen arcade window. Keys: `T` toggles training/testing, `Space` pauses, `N` toggles the live network visualization, `Up`/`Down` arrows raise/lower the move interval (game speed). Weights autosave every 1000 steps and on window close.
- Initialize fresh weights: `python init_weights.py` — **destructive**, overwrites `weights.npz` with He-initialized random weights. Only run when intentionally resetting the model; it must have been run at least once before `viewer.py` can load `weights.npz`.

There are no tests, linter, or build step.

## Architecture

A from-scratch Deep Q-Network for Snake. NumPy only — no PyTorch/TensorFlow. The network, training loop, and game loop are all driven by `arcade`'s `on_update` callback in `viewer.py`.

Four files form the core loop:

- `snake_env.py` — game logic and the **29-dim observation vector** (`OBS_DIM`). For each of 8 directions around the head (`DIRECTIONS`), three slots encode (food seen along the ray, body distance as `1/distance`, wall distance as `1/distance`) → 24 slots. Slots 24–27 one-hot the current cardinal heading; slot 28 is **fatigue** = `steps_since_food / (len(snake) * 60)`. Actions are relative (`0=turn left, 1=straight, 2=turn right`), not absolute. Three death conditions: wall, self-collision, and **starvation** (`steps_since_food >= 60 * len(snake)`). Reward shaping constants at the top of the file (`FOOD_REWARD=10`, `DEATH_REWARD=-10`, `TOWARDS_REWARD=0.1`, `AWAY_REWARD=-0.15`) are the main lever for changing learned behavior.
- `nn.py` — `SnakeAI`: 29→20→12→3 MLP with ReLU, hand-written forward/backward (MSE on the taken action's Q-value), experience replay, batch size 32, γ=0.95, learning rate 1e-3. Loads `weights.npz` on construction. The replay buffer (`training_data`) is a plain list; the viewer caps it at 50k.
- `viewer.py` — owns the env, the agent, and the training/inference toggle, plus all rendering (board, HUD, optional network graph). During training, epsilon decays as `0.05 + 0.95 * e^(-1e-5 * steps_taken)`; during testing it is forced to 0. Replay buffer is trimmed to 50k via `pop(0)`. `move_interval` starts at 0.05s and is adjustable live with the arrow keys.
- `edit_file.py` — reads/writes `data.txt`, a two-line plaintext file storing `steps_taken` (line 1) and `high_score` (line 2). Persisted across sessions; `viewer.on_close` flushes both.

State persistence quirks worth knowing:
- `weights.npz` is the model. It is committed to the repo and overwritten in place during training. Back it up before experimenting — saved snapshots live in `backup_weights/` (filenames encode steps, high score, and architecture, e.g. `876306s52hs29-20-12-3.npz`).
- Training and weight-saving are interleaved on the UI thread.
