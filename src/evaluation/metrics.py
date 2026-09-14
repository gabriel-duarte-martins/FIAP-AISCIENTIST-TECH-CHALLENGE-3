import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score,balanced_accuracy_score,brier_score_loss,
    roc_auc_score,average_precision_score,precision_score,recall_score,f1_score,confusion_matrix)


def metrics(y,p,w,risk_threshold=.5):
    y,p,w = np.asarray(y,dtype=int),np.asarray(p,dtype=float),np.asarray(w,dtype=float)
    risk = 1-p
    pred_risk = risk>=risk_threshold
    yt = 1-y
    both = len(np.unique(y))==2
    return {
        'alunos':int(w.sum()),'prevalencia_nao_alfabetizado':float(np.average(yt,weights=w)),
        'accuracy':float(accuracy_score(yt,pred_risk,sample_weight=w)),
        'balanced_accuracy':float(balanced_accuracy_score(yt,pred_risk,sample_weight=w)),
        'brier':float(brier_score_loss(y,p,sample_weight=w)),
        'roc_auc':float(roc_auc_score(yt,risk,sample_weight=w)) if both else None,
        'average_precision_risco':float(average_precision_score(yt,risk,sample_weight=w)) if both else None,
        'precision_risco':float(precision_score(yt,pred_risk,sample_weight=w,zero_division=0)),
        'recall_risco':float(recall_score(yt,pred_risk,sample_weight=w,zero_division=0)),
        'f1_risco':float(f1_score(yt,pred_risk,sample_weight=w,zero_division=0)),
        'fracao_sinalizada':float(np.average(pred_risk,weights=w)),
        'limiar_risco':float(risk_threshold),
        'confusion_risco':confusion_matrix(yt,pred_risk,sample_weight=w,labels=[0,1]).astype(int).tolist(),
    }


def bootstrap_municipal(frame, p, threshold, repeats=250):
    ids,codes = np.unique(frame.id_municipio,return_inverse=True)
    rng = np.random.default_rng(2026)
    result = []
    keys = ['roc_auc','brier','recall_risco','balanced_accuracy']
    for _ in range(repeats):
        freq = np.bincount(rng.integers(0,len(ids),len(ids)),minlength=len(ids))
        weights = frame.peso.to_numpy(dtype=float)*freq[codes]
        mask = weights>0
        m = metrics(frame.alvo_alfabetizado.to_numpy()[mask],p[mask],weights[mask],threshold)
        result.append({k:m[k] for k in keys})
    return {k:{'low':float(np.quantile([r[k] for r in result],.025)),
               'high':float(np.quantile([r[k] for r in result],.975))} for k in keys}


def calibration(y,p,w):
    bins = np.minimum((np.asarray(p)*10).astype(int),9)
    rows=[]
    for b in range(10):
        mask=bins==b
        if np.any(mask):
            rows.append(dict(bin=b,n=float(w[mask].sum()),previsto=float(np.average(p[mask],weights=w[mask])),
                             observado=float(np.average(y[mask],weights=w[mask]))))
    return pd.DataFrame(rows)
