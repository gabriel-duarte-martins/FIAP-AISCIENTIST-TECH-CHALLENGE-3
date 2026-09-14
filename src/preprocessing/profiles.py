import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import OneHotEncoder
from src.config import NUMERIC, CATEGORICAL, LOG_COLUMNS, CONFIG


def weighted_median(values, weights):
    valid = np.isfinite(values) & (weights > 0)
    if not valid.any():
        return 0.0
    values, weights = values[valid], weights[valid]
    order = np.argsort(values, kind='stable')
    values, weights = values[order], weights[order]
    return float(values[np.searchsorted(np.cumsum(weights), weights.sum()/2)])


class ProfilePreprocessor(TransformerMixin, BaseEstimator):
    """Imputação e escala ponderadas pela multiplicidade real de cada perfil.

    Fitted somente no treino; uma linha comprimida pode representar muitos alunos.
    """
    def __init__(self, numeric=None, categorical=None):
        self.numeric = numeric
        self.categorical = categorical

    def _numeric(self, X):
        matrix = X[self.numeric_].apply(pd.to_numeric, errors='coerce').to_numpy(dtype=float,na_value=np.nan)
        matrix[~np.isfinite(matrix)] = np.nan
        for j, col in enumerate(self.numeric_):
            if col in LOG_COLUMNS:
                matrix[:,j] = np.log1p(np.maximum(matrix[:,j],0))
        return matrix

    def _categorical(self, X):
        return X[self.categorical_].astype('string').fillna('__ausente__').astype(str)

    def fit(self, X, y=None, sample_weight=None):
        self.numeric_ = list(NUMERIC if self.numeric is None else self.numeric)
        self.categorical_ = list(CATEGORICAL if self.categorical is None else self.categorical)
        w = np.ones(len(X)) if sample_weight is None else np.asarray(sample_weight,dtype=float)
        a = self._numeric(X)
        self.medians_ = np.array([weighted_median(a[:,j],w) for j in range(a.shape[1])])
        filled = np.where(np.isnan(a),self.medians_,a)
        self.means_ = np.average(filled,axis=0,weights=w)
        self.scales_ = np.sqrt(np.average((filled-self.means_)**2,axis=0,weights=w))
        self.scales_[self.scales_<1e-12] = 1
        self.encoder_ = OneHotEncoder(handle_unknown='ignore',sparse_output=False)
        self.encoder_.fit(self._categorical(X))
        return self

    def transform(self, X):
        a = self._numeric(X)
        missing = np.isnan(a).astype(float)
        a = (np.where(np.isnan(a),self.medians_,a)-self.means_)/self.scales_
        return np.column_stack([a,missing,self.encoder_.transform(self._categorical(X))])

    def get_feature_names_out(self, input_features=None):
        return np.array(self.numeric_+[f'{c}__ausente' for c in self.numeric_]+
                        list(self.encoder_.get_feature_names_out(self.categorical_)))


def split_profiles(frame):
    if frame.id_municipio.isna().any():
        raise ValueError('Município ausente impede partição segura')
    splitter = GroupShuffleSplit(n_splits=1,test_size=.2,random_state=CONFIG['seed_test'])
    develop_i,test_i = next(splitter.split(frame,groups=frame.id_municipio))
    develop = frame.iloc[develop_i]
    inner = GroupShuffleSplit(n_splits=1,test_size=.25,random_state=CONFIG['seed_validation'])
    train_i,val_i = next(inner.split(develop,groups=develop.id_municipio))
    parts = dict(treino=develop.iloc[train_i].copy(),validacao=develop.iloc[val_i].copy(),teste=frame.iloc[test_i].copy())
    sets = [set(x.id_municipio) for x in parts.values()]
    if sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2]:
        raise AssertionError('Município presente em mais de uma partição')
    return parts
