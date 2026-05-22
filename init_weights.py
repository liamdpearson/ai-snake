# DO NOT RUN WILL OVERRIDE WEIGHTS


import numpy as np

# init weights
W1 = np.random.randn(40, 28) * np.sqrt(2.0 / 28)
b1 = np.zeros((40, 1))
W2 = np.random.randn(24, 40) * np.sqrt(2.0 / 40)
b2 = np.zeros((24, 1))
W3 = np.random.randn(3, 24) * np.sqrt(2.0 / 24)
b3 = np.zeros((3, 1))

np.savez("weights.npz", W1=W1, b1=b1, W2=W2, b2=b2, W3=W3, b3=b3)