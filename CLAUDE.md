# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Run

- Play / train: `python viewer.py` — opens the arcade window. Toggle training with `T`, pause with `Space`. Weights autosave every 1000 steps and on window close.
- Initialize fresh weights: `python init_weights.py` — **destructive**, overwrites `weights.npz`. Only run when intentionally resetting the model.

There are no tests, linter, or build step.

## Architecture

A from-scratch Deep Q-Network for Snake. NumPy only — no PyTorch/TensorFlow. The network, training loop, and game loop are all driven by `arcade`'s `on_update` callback in `viewer.py`.

Four files form the core loop:

- `snake_env.py` — game logic and the **28-dim observation vector**. For each of 8 directions around the head, three slots encode (food seen, body seen, wall distance as `1/distance`); the final 4 slots one-hot the current cardinal heading. Actions are relative (`0=turn left, 1=straight, 2=turn right`), not absolute. Reward shaping constants live at the top of the file (`FOOD_REWARD`, `DEATH_REWARD`, `TOWARDS_REWARD`, `AWAY_REWARD`) — tuning these is the main lever for changing learned behavior.
- `nn.py` — `SnakeAI`: 28→32→24→3 MLP with ReLU, hand-written forward/backward, experience replay (deque-style list capped at 50k in viewer), batch size 32, γ=0.95. Loads `weights.npz` on construction; `init_weights.py` must have been run at least once first.
- `viewer.py` — owns the env, the agent, and the training/inference toggle. Epsilon decays as `0.05 + 0.95 * e^(-1e-5 * steps_taken)` during training and is forced to 0 during testing. Replay buffer is trimmed to 50k by `pop(0)`.
- `edit_file.py` — reads/writes `data.txt`, a two-line plaintext file storing `steps_taken` (line 1) and `high_score` (line 2). Persisted across sessions; `viewer.on_close` flushes both.

State persistence quirks worth knowing:
- `weights.npz` is the model. It is committed to the repo and overwritten in place during training. Back it up (cf. `saved_weights/`) before experimenting.
- Training and weight-saving are interleaved on the UI thread; `MOVE_INTERVAL = 0` means it runs as fast as arcade will tick.
