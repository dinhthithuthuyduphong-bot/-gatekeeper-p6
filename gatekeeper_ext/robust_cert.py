"""Exploratory harm certificates; never substitutes for a frozen primary rule.

Under H0: E[X_t | past] >= eta, each nonnegative factor
1 + lambda_t*(eta-X_t) has conditional expectation <= 1.
Stakes use only past data. Mixture weights are fixed before observing outcomes.
"""
import math


class AdaptiveHarmCert:
    def __init__(self, eta=.05, prior_weight=2.0, cap=.99):
        if not 0 < eta < 1 or prior_weight <= 0 or not 0 < cap < 1:
            raise ValueError("invalid certificate parameters")
        self.eta, self.prior_weight, self.cap = eta, prior_weight, cap
        self.n, self.harms, self.log_w = 0, 0, 0.0

    def stake(self):
        estimate = (self.eta*self.prior_weight+self.harms)/(self.prior_weight+self.n)
        return max(0.0, min(self.cap/(1-self.eta), (self.eta-estimate)/(self.eta*(1-self.eta))))

    def update(self, regressed):
        lam = self.stake()  # strictly before this observation
        self.log_w += math.log1p(lam*(self.eta-int(bool(regressed))))
        self.n += 1
        self.harms += int(bool(regressed))
        return self.value

    @property
    def value(self):
        return math.exp(self.log_w)


class BalancedHarmCert:
    def __init__(self, eta=.05):
        if not 0 < eta < 1: raise ValueError("invalid eta")
        self.eta = eta
        self.fractions = (.1,.2,.3,.4,.5,.6,.7,.8,.9,.99)
        self.logs = [0.0]*len(self.fractions)

    def update(self, regressed):
        for i,c in enumerate(self.fractions):
            self.logs[i] += math.log1p(c/(1-self.eta)*(self.eta-int(bool(regressed))))
        return self.value

    @property
    def value(self):
        top = max(self.logs)
        return math.exp(top)*sum(math.exp(v-top) for v in self.logs)/len(self.logs)


def binomial_cdf(x, n, p):
    """Lower binomial tail, exact model calculation (floating-point arithmetic)."""
    if x < 0: return 0.0
    if x >= n or p == 0: return 1.0
    if p == 1: return 0.0
    logs = [math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)
            +i*math.log(p)+(n-i)*math.log1p(-p) for i in range(x+1)]
    peak = max(logs)
    return min(1.0, math.exp(peak)*sum(math.exp(v-peak) for v in logs))


def fixed_iut_pvalue(trace, n, theta, eta):
    """Union null: insufficient mean benefit OR harm >= eta.

    max(p_benefit,p_harm) is a valid p-value for this union null. Do not divide
    alpha by two inside this intersection-union decision. Fixed n only.
    """
    if len(trace) < n or n < 1: raise ValueError("incomplete fixed-size observations")
    observations=trace[:n]
    if any(z not in (-1,0,1) or bool(h) != (z>0) for z,h in observations):
        raise ValueError("invalid binary-loss paired trace")
    mean = -sum(z for z,_ in observations)/n
    p_ben = math.exp(-n*max(0,mean-theta)**2/2)  # Hoeffding, range length 2
    p_harm = binomial_cdf(sum(bool(h) for _,h in observations),n,eta)
    return max(p_ben,p_harm)


def holm(pvalues, alpha):
    selected=[]
    ranked=sorted(pvalues.items(),key=lambda x:x[1])
    for i,(name,p) in enumerate(ranked):
        if not math.isfinite(p) or not 0 <= p <= 1: raise ValueError("invalid p-value")
        if p > alpha/(len(ranked)-i): break
        selected.append(name)
    return selected
