import unittest
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from src.config import NUMERIC,CATEGORICAL,FEATURES
from src.preprocessing.profiles import ProfilePreprocessor,split_profiles


def fixture():
    rows=[]
    for i in range(30):
        for y in [0,1]:
            rows.append({**{c:float(i+1) for c in NUMERIC},'codigo_uf':str(i%3),
                         'rede':'Municipal','id_municipio':f'{3500000+i}',
                         'alvo_alfabetizado':y,'peso':1+(i+y)%4})
    out=pd.DataFrame(rows)
    out.loc[out.index%7==0,NUMERIC[0]]=np.nan
    return out


class ContractTests(unittest.TestCase):
    def test_group_isolation(self):
        frame=fixture(); parts=split_profiles(frame)
        a,b,c=[set(p.id_municipio) for p in parts.values()]
        self.assertFalse(a&b or a&c or b&c)
        self.assertEqual(sum(len(p) for p in parts.values()),len(frame))

    def test_weighted_compression_matches_expanded_logistic(self):
        frame=fixture()
        expanded=frame.loc[frame.index.repeat(frame.peso)].reset_index(drop=True)
        def model():
            return Pipeline([('preprocess',ProfilePreprocessor()),('model',LogisticRegression(C=.01,max_iter=2000))])
        compressed=model().fit(frame[FEATURES],frame.alvo_alfabetizado,
            preprocess__sample_weight=frame.peso,model__sample_weight=frame.peso)
        full=model().fit(expanded[FEATURES],expanded.alvo_alfabetizado)
        np.testing.assert_allclose(compressed.predict_proba(frame[FEATURES]),full.predict_proba(frame[FEATURES]),atol=1e-5)

    def test_unseen_categories_and_empty_values(self):
        frame=fixture(); pre=ProfilePreprocessor().fit(frame[FEATURES],sample_weight=frame.peso)
        before=pre.medians_.copy()
        new=frame.iloc[:2][FEATURES].copy()
        new[NUMERIC]=np.nan; new['rede']='Inédita'
        self.assertTrue(np.isfinite(pre.transform(new)).all())
        np.testing.assert_array_equal(before,pre.medians_)

    def test_no_forbidden_predictor(self):
        forbidden={'alvo_alfabetizado','alfabetizado','proficiencia','id_aluno','id_escola','id_municipio','peso','atingiu_meta','gap_para_meta'}
        self.assertFalse(set(FEATURES)&forbidden)


if __name__=='__main__':
    unittest.main()
