# Gate phase diagram (alpha=0.1, eta=0.05, 2000 simulations per sequential cell)

P(admit) for a patch that always helps (help rate 0.5). From h >= eta admitting is an error.

| h | smoke 20 | smoke 50 | zero-tol 300 | fixed 300 | fixed 1000 | GK c=0.9 @300 | mixture @300 | mixture @1000 | mixture @2000 |
|---|---|---|---|---|---|---|---|---|---|
| 0.00% | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 0.10% | 0.98 | 0.95 | 0.74 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 0.25% | 0.95 | 0.88 | 0.47 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 0.30% | 0.94 | 0.86 | 0.41 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 1.00% | 0.82 | 0.61 | 0.05 | 1.00 | 1.00 | 0.95 | 0.97 | 1.00 | 1.00 |
| 2.00% | 0.67 | 0.36 | 0.00 | 0.92 | 1.00 | 0.65 | 0.69 | 1.00 | 1.00 |
| 3.00% | 0.54 | 0.22 | 0.00 | 0.59 | 0.97 | 0.36 | 0.34 | 0.78 | 0.97 |
| 5.00% (error if admitted) | 0.36 | 0.08 | 0.00 | 0.06 | 0.08 | 0.10 | 0.08 | 0.10 | 0.10 |
| 10.00% (error if admitted) | 0.12 | 0.01 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 |
| 20.00% (error if admitted) | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

Fixed-sample test accepts at most 9 harms in 300 draws and 40 in 1000 (exact one-sided bound below eta).

**Band where simple gates are wrong:** a zero-tolerance 300-draw gate keeps less than half of acceptable patches once h > 0.23%; a 20-draw smoke test still admits more than 10% of inadmissible patches until h reaches 10.9%. Band used by gate G3: [0.25%, 10%].

Mean draws used by the fixed-stake sequential rule at 300 draws (one patch, threshold 1/alpha = 10; with a family of K = 16 cells the threshold is 160 and the h = 0 value becomes 110): h=0.00%: 50, h=1.00%: 91, h=5.00%: 271, h=10.00%: 268.
