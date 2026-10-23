"""Mixture harm certificate (Study H secondary rule): wealth = sum_k w_k prod(1 + c_k eta/(1-eta)
... ) over fixed fractions c_k of the maximal stake, i.e. a mixture of likelihood ratios
Bern(h')/Bern(eta).  A fixed-weight average of test supermartingales for the same null is a
test supermartingale, so validity is unchanged; it keeps positive growth for true h between
~0.4 eta and eta, where the fixed stake c = 0.9 does not."""
import math

GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


class MixtureHarmCert:
    def __init__(self, eta, top=0.99, top_weight=0.5, grid=GRID):
        self.eta = eta
        self.cs = (top,) + tuple(grid)
        self.ws = (top_weight,) + tuple((1 - top_weight) / len(grid) for _ in grid)
        self.logw = [0.0] * len(self.cs)

    def update(self, regressed):
        for i, c in enumerate(self.cs):
            lam = c / (1 - self.eta)
            self.logw[i] += math.log(max(1 + lam * (self.eta - (1.0 if regressed else 0.0)), 1e-300))

    @property
    def value(self):
        return sum(w * math.exp(l) for w, l in zip(self.ws, self.logw))
