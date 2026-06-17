import numpy as np
import random

class SnakeAI:
    def __init__(self):
        params = np.load("weights.npz")
        self.W1, self.W2, self.W3 = params['W1'], params['W2'], params['W3']
        self.b1, self.b2, self.b3 = params['b1'], params['b2'], params['b3']

        self.training_data = []
        self.batch_size = 32
        self.gamma = 0.95
        self.epsilon = 1.0
        self.lr = 1e-3


    def forward(self, X): # X is input
        Z1 = self.W1.dot(X) + self.b1
        A1 = ReLU(Z1)
        Z2 = self.W2.dot(A1) + self.b2
        A2 = ReLU(Z2)
        Q = self.W3.dot(A2) + self.b3

        cache = {"Z1" : Z1, "A1" : A1, "Z2" : Z2, "A2" : A2}
        return Q, cache
    
    def get_ai_output(self, X):
        Q, _ = self.forward(X)
        return int(np.argmax(Q))

    def save_weights(self):
        np.savez("weights.npz", W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2, W3=self.W3, b3=self.b3)
    
    def train(self):
        if len(self.training_data) < self.batch_size:
            return

        idx = random.sample(range(len(self.training_data)), self.batch_size)
        batch = [self.training_data[i] for i in idx]

        X      = np.hstack([t[0] for t in batch])              # (29, B)
        action = np.array([t[1] for t in batch], dtype=np.int64)
        reward = np.array([t[2] for t in batch], dtype=np.float64)
        X_next = np.hstack([t[3] for t in batch])              # (29, B)
        done   = np.array([t[4] for t in batch], dtype=np.float64)

        # Build targets from the next state (no grad through this branch)
        Q_next, _ = self.forward(X_next)
        target = reward + self.gamma * np.max(Q_next, axis=0) * (1.0 - done)

        # Fresh forward on current states — cache is valid because weights haven't moved yet
        _, cache = self.forward(X)
        grads = self.backward(X, cache, action, target)

        self.W1 -= self.lr * grads["dW1"]
        self.b1 -= self.lr * grads["db1"]
        self.W2 -= self.lr * grads["dW2"]
        self.b2 -= self.lr * grads["db2"]
        self.W3 -= self.lr * grads["dW3"]
        self.b3 -= self.lr * grads["db3"]


    def backward(self, X, cache, action, target):
        Z1, A1, Z2, A2 = cache["Z1"], cache["A1"], cache["Z2"], cache["A2"]
        m = X.shape[1]  # batch size

        # dL/dQ — only the taken action has gradient (MSE on that entry)
        Q = self.W3.dot(A2) + self.b3
        dQ = np.zeros_like(Q)
        dQ[action, np.arange(m)] = (Q[action, np.arange(m)] - target) / m

        dW3 = dQ.dot(A2.T)
        db3 = np.sum(dQ, axis=1, keepdims=True)

        dA2 = self.W3.T.dot(dQ)
        dZ2 = dA2 * (Z2 > 0)          # ReLU'
        dW2 = dZ2.dot(A1.T)
        db2 = np.sum(dZ2, axis=1, keepdims=True)

        dA1 = self.W2.T.dot(dZ2)
        dZ1 = dA1 * (Z1 > 0)
        dW1 = dZ1.dot(X.T)
        db1 = np.sum(dZ1, axis=1, keepdims=True)

        return {"dW1": dW1, "db1": db1, "dW2": dW2, "db2": db2, "dW3": dW3, "db3": db3}
    

def ReLU(Z):
    return np.maximum(0, Z)

def softmax(Z):
    return np.exp(Z) / np.sum(np.exp(Z), axis=0, keepdims=True)