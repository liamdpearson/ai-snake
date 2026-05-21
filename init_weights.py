# DO NOT RUN WILL OVERRIDE WEIGHTS


import numpy as np

# init weights
W1 = np.random.randn(20, 28) * np.sqrt(2.0 / 28)
b1 = np.zeros((20, 1))
W2 = np.random.randn(12, 20) * np.sqrt(2.0 / 20)
b2 = np.zeros((12, 1))
W3 = np.random.randn(3, 12) * np.sqrt(2.0 / 12)
b3 = np.zeros((3, 1))

np.savez("weights.npz", W1=W1, b1=b1, W2=W2, b2=b2, W3=W3, b3=b3)