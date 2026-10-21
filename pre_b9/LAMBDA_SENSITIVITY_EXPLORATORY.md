# Exploratory analytic sensitivity: harm-certificate λ

**NOT prospective evidence.** Analytic Bernoulli scenarios, not observed target outcomes.
The frozen implementation uses `lambda = frac/(1-eta)` with `frac=0.9`.
Rows with alternative fractions are hypothetical; do not overwrite frozen settings.

| frac | λ | true h | E[log wealth per draw] | draws to 1/α with 0 regressions |
|---:|---:|---:|---:|---:|
| 0.3 | 0.3158 | 0.00 | +0.01567 | 147 |
| 0.3 | 0.3158 | 0.02 | +0.00822 | 147 |
| 0.3 | 0.3158 | 0.05 | -0.00295 | 147 |
| 0.3 | 0.3158 | 0.10 | -0.02157 | 147 |
| 0.5 | 0.5263 | 0.00 | +0.02598 | 89 |
| 0.5 | 0.5263 | 0.02 | +0.01159 | 89 |
| 0.5 | 0.5263 | 0.05 | -0.00998 | 89 |
| 0.5 | 0.5263 | 0.10 | -0.04594 | 89 |
| 0.7 | 0.7368 | 0.00 | +0.03618 | 64 |
| 0.7 | 0.7368 | 0.02 | +0.01138 | 64 |
| 0.7 | 0.7368 | 0.05 | -0.02583 | 64 |
| 0.7 | 0.7368 | 0.10 | -0.08784 | 64 |
| 0.9 | 0.9474 | 0.00 | +0.04628 | 50 |
| 0.9 | 0.9474 | 0.02 | -0.00070 | 50 |
| 0.9 | 0.9474 | 0.05 | -0.07116 | 50 |
| 0.9 | 0.9474 | 0.10 | -0.18861 | 50 |

At the null boundary `h=eta`, expected *wealth multiplier* equals 1;
expected log growth can be negative by Jensen's inequality.
The no-regression crossing count is a conditional best-case path,
NOT expected admission time or statistical power.
Power and stopping-time distributions require separately labeled Monte Carlo
simulations or actual prospective draws.
