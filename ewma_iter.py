import numpy as np
import pandas as pd


class ewma_iter(object):
    def __init__(self, n, expected_length=5000):
        self.n = n
        alpha = 2/(n+1)
        self.a = alpha
        self.expected_length = expected_length
        self.weights = np.fromfunction(lambda x: (1-alpha)**x, (expected_length,))

    def __call__(self, s, ewma_=None, mask=None):
        n = len(s)
        weights = self.weights[:n]
        s_rev = s[::-1]
        inner = np.inner(weights, s_rev)
        sum_ = np.sum(weights)
        e = inner/sum_
        if ewma_ is not None:
            ewma_[-1] = e
        return e

def main():
    ewma20 = ewma_iter(20)

    n = 30
    p = np.arange(n)
    p_ewma = np.zeros(n)

    for i in range(n):
        ewma20(p[:i+1], p_ewma[:i+1])

    print(p_ewma)
    print(pd.ewma(p, span=20))

if __name__ == '__main__':
    main()


