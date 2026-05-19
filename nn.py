import numpy as np


class SnakeAI:
    def __init__(self):

        W1 = np.random.randn(20, 32) * np.sqrt(2.0 / 32)   # He init
        b1 = np.zeros((20, 1))
        W2 = np.random.randn(12, 20) * np.sqrt(2.0 / 20)
        b2 = np.zeros((12, 1))
        W3 = np.random.randn(4, 12) * np.sqrt(2.0 / 12)
        b3 = np.zeros((4, 1))

        np.savez("weights.npz", W1=W1, b1=b1, W2=W2, b2=b2, W3=W3, b3=b3)

SnakeAI()