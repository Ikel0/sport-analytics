"""Recommendation Model Evaluation — Precision@K, Recall@K, Coverage, Diversity."""
import logging, random
from pathlib import Path
import joblib, numpy as np
from models.recommender import SportRecommender, UserProfile
from models.train import build_catalog

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)
MODEL_PATH = Path("models/recommender.pkl")


def generate_test_users(catalog, n_users=100):
    nba_items  = [c.content_id for c in catalog if c.sport == "nba"]
    foot_items = [c.content_id for c in catalog if c.sport == "football"]
    cases = []
    for i in range(n_users):
        is_nba = random.random() > 0.5
        pref   = {"nba": 0.8, "football": 0.2} if is_nba else {"nba": 0.2, "football": 0.8}
        pool   = nba_items if is_nba else foot_items
        history = random.sample(pool, min(10, len(pool)))
        remaining = [x for x in pool if x not in history]
        ground_truth = random.sample(remaining, min(20, len(remaining)))
        cases.append((UserProfile(f"test_{i:03d}", pref, [], [], history), ground_truth))
    return cases


def precision_at_k(rec, rel, k): return len(set(rec[:k]) & set(rel)) / k if k else 0.0
def recall_at_k(rec, rel, k):    return len(set(rec[:k]) & set(rel)) / len(rel) if rel else 0.0

def catalog_coverage(all_recs, catalog):
    return len(set(item for recs in all_recs for item in recs)) / len(catalog)

def diversity(rec_ids, recommender):
    if len(rec_ids) < 2: return 0.0
    df  = recommender.content_df
    idx = df.index[df["content_id"].isin(rec_ids)].tolist()
    if len(idx) < 2: return 0.0
    from sklearn.metrics.pairwise import cosine_similarity
    sim = cosine_similarity(recommender.feature_matrix[idx])
    n   = len(idx)
    return sum(1 - sim[i][j] for i in range(n) for j in range(i+1, n)) / (n*(n-1)/2)


def evaluate():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No model at {MODEL_PATH}. Run `make train` first.")
    recommender = joblib.load(MODEL_PATH)
    catalog     = build_catalog()
    test_users  = generate_test_users(catalog)
    K           = [5, 10, 20]
    results     = {k: {"precision": [], "recall": []} for k in K}
    all_recs, divs = [], []

    for profile, gt in test_users:
        recs   = recommender.recommend(profile, n=max(K))
        ids    = recs["content_id"].tolist()
        all_recs.append(ids)
        for k in K:
            results[k]["precision"].append(precision_at_k(ids, gt, k))
            results[k]["recall"].append(recall_at_k(ids, gt, k))
        divs.append(diversity(ids[:10], recommender))

    print("\n" + "="*55)
    print("  SPORT RECOMMENDER — EVALUATION REPORT")
    print("="*55)
    for k in K:
        print(f"  Precision@{k:<3} = {np.mean(results[k]['precision']):.4f}")
        print(f"  Recall@{k:<5}    = {np.mean(results[k]['recall']):.4f}")
        print()
    print(f"  Catalog Coverage   = {catalog_coverage(all_recs, catalog):.2%}")
    print(f"  Avg Diversity@10   = {np.mean(divs):.4f}")
    print("="*55 + "\n")


if __name__ == "__main__":
    evaluate()
