import itertools
import unittest
from gatekeeper_ext.robust_cert import AdaptiveHarmCert,BalancedHarmCert,binomial_cdf,fixed_iut_pvalue,holm


class StatisticalContracts(unittest.TestCase):
    def test_predictable_stakes_and_null_expectation(self):
        for size in range(7):
            for history in itertools.product([False,True],repeat=size):
                cert=AdaptiveHarmCert(.05)
                for x in history:cert.update(x)
                lam=cert.stake()
                self.assertGreaterEqual(lam,0);self.assertLess(lam,1/.95)
                for h in [.05,.1,.5,1]:
                    expected=(1-h)*(1+lam*.05)+h*(1+lam*(.05-1))
                    self.assertLessEqual(expected,1+1e-14)

    def test_enumerated_small_sample_mean_wealth(self):
        for factory in (AdaptiveHarmCert,BalancedHarmCert):
            for h in (.05,.2):
                total=0
                for sequence in itertools.product([False,True],repeat=8):
                    cert=factory(.05)
                    for x in sequence:cert.update(x)
                    total+=h**sum(sequence)*(1-h)**(8-sum(sequence))*cert.value
                self.assertLessEqual(total,1+1e-12)

    def test_exact_binomial_tail(self):
        self.assertAlmostEqual(binomial_cdf(0,80,.05),.95**80)
        self.assertAlmostEqual(binomial_cdf(2,4,.5),11/16)
        self.assertEqual(binomial_cdf(-1,3,.2),0)

    def test_iut_keeps_harm_and_mean_nulls(self):
        self.assertEqual(fixed_iut_pvalue([[0,False]]*300,300,.2,.05),1)
        self.assertGreater(fixed_iut_pvalue([[-1,False]]*250+[[1,True]]*50,300,.2,.05),.9)
        self.assertLess(fixed_iut_pvalue([[-1,False]]*300,300,.2,.05),.1/6)

    def test_holm_keeps_entire_family(self):
        self.assertEqual(holm({'a':.02,'b':.9,'c':.9,'d':.9,'e':.9,'f':.9},.1),[])
        self.assertEqual(holm({'a':.01,'b':.019,'c':.9},.1),['a','b'])

    def test_total_variation_excess_loss_factor(self):
        # Under the usual TV=sup_A|P(A)-Q(A)| convention, range [-1,1] needs 2*TV.
        p,q=.1,.2
        self.assertAlmostEqual((2*q-1)-(2*p-1),2*abs(q-p))


if __name__=='__main__': unittest.main(verbosity=2)
