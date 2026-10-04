import unittest
import numpy as np
import pandas as pd
from analyze import rank_corr, correlation, event_index
from pipeline import reflectance

class AnalysisTests(unittest.TestCase):
    def test_spearman_and_constant(self):
        self.assertAlmostEqual(rank_corr([1,2,3],[30,20,10]),-1)
        self.assertAlmostEqual(rank_corr([1,1,2],[3,3,4]),1)
        self.assertIsNone(rank_corr([1,1,1],[1,2,3]))
    def test_legacy_offset_is_not_subtracted_twice(self):
        item={'properties':{'earthsearch:boa_offset_applied':True},'assets':{'green':{'raster:bands':[{'scale':.0001,'offset':-.1}]}}}
        self.assertAlmostEqual(float(reflectance(item,'green',np.array([500.]))[0]),.05)
        item['properties']['earthsearch:boa_offset_applied']=False
        self.assertAlmostEqual(float(reflectance(item,'green',np.array([1500.]))[0]),.05)
    def test_permutation_and_bootstrap_on_known_order(self):
        result=correlation(pd.DataFrame({'x':range(6),'y':[0,2,4,8,16,32]}),'x','y')
        self.assertAlmostEqual(result['spearman_rho'],1)
        self.assertLess(result['p_two_sided_permutation'],.01)
        np.testing.assert_allclose(result['bootstrap_95_ci'],[1,1])
        self.assertGreater(result['valid_bootstraps'],9900)
    def test_empty_is_not_zero_correlation(self):
        s=correlation(pd.DataFrame(columns=['x','y']),'x','y')
        self.assertEqual(s['n'],0);self.assertIsNone(s['spearman_rho']);self.assertIsNone(s['p_two_sided_permutation'])
    def test_relative_auc_sign_and_no_single_date_curve(self):
        g=pd.DataFrame({'day_after_event':[1,3],'roof_snow_fraction':[1,0],'ground_snow_fraction':[1,1]})
        value,reason=event_index(g);self.assertAlmostEqual(value,.5);self.assertEqual(reason,'eligible')
        self.assertIsNone(event_index(g.iloc[:1])[0])
        g['ground_snow_fraction']=.25;self.assertIsNone(event_index(g)[0])
    def test_duplicate_same_day_not_independent(self):
        g=pd.DataFrame({'day_after_event':[2,2],'roof_snow_fraction':[1,0],'ground_snow_fraction':[1,1]})
        self.assertIsNone(event_index(g)[0])

if __name__=='__main__':unittest.main()
