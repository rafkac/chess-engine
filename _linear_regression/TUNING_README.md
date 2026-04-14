# Linear Regression Tuning Pipeline

Tune your evaluation weights by learning from Stockfish-evaluated positions,
using existing public datasets.

## Approach

Your `ClassicEvaluator` has two layers:

1. **Material + PeSTO piece-square tables** — already well-optimised, kept **fixed**
2. **Tunable features** — mobility, pawn structure, bishop pair, tempo — weights **learned by regression**

The regression target is the *residual* between Stockfish's evaluation and the fixed PST baseline:

```
residual = stockfish_eval - pst_baseline(board)
residual ≈ dot(weights, tunable_features) + bias
```

At inference:  `score = pst_baseline(board) + dot(weights, features) + bias`


## Which Dataset to Use

### Recommended: Kaggle "Chess Evaluations" (ronakbadhe)

**URL:** https://www.kaggle.com/datasets/ronakbadhe/chess-evaluations

This is the easiest option. It contains **~13 million positions** with pre-computed
Stockfish 11 evaluations at **depth 22**.

- Format: CSV with columns `FEN` and `Evaluation` (centipawns as integers, mate as `#+N` / `#-N`)
- Download: one file, `chessData.csv` (~1.5 GB)
- No need to run Stockfish yourself
- Depth 22 gives high-quality ground truth

**Why this one:** ready to use out of the box, large enough for robust regression,
deep evaluations, simple CSV format. For a university project this is the sweet spot
between quality and convenience.


### Alternative: Lichess Evaluation Database

**URL:** https://database.lichess.org/#evals

The official Lichess evaluation database has **~363 million positions** evaluated by
various Stockfish versions at varying depths.

- Format: JSONL (`lichess_db_eval.jsonl.zst`, ~7 GB compressed, ~35 GB decompressed)
- Each line: `{"fen": "...", "evals": [{"depth": 36, "pvs": [{"cp": 150}]}]}`
- Filter by depth for quality (recommend depth ≥ 20)
- Needs decompression with `zstd`

**When to use this:** if you want the largest, most diverse dataset and don't mind
the extra decompression step. The `load_dataset.py` script handles the JSONL format.


### Also available: HuggingFace mirror

**URL:** https://huggingface.co/datasets/Lichess/chess-position-evaluations

Same Lichess data in a denormalised format accessible via the `datasets` library.
Convenient if you're already in a Python/HuggingFace workflow.


## Quick Start

### Step 1: Download the dataset

Download `chessData.csv` from Kaggle (requires a free Kaggle account) and place
it in your project, e.g. `data/chessData.csv`.


### Step 2: Prepare the data

```bash
python tools/load_dataset.py \
    --input data/chessData.csv \
    --format kaggle \
    --output data/training_set.csv \
    --sample 50000
```

This loads the Kaggle CSV, filters out mate positions, randomly samples 50,000
positions, and saves a clean CSV.  Adjust `--sample` as needed (more data = better
regression, but slower feature extraction). For a first run, 50k is a good balance.
For production, try 200k–500k.


### Step 3: Train weights

```bash
python tools/train_weights.py \
    --data data/training_set.csv \
    --output src/chess_engine/learned_weights.json \
    --alpha 1.0
```

This extracts features, computes the fixed PST baseline for each position, and
runs ridge regression on the residuals.  Output includes:

- Learned weights compared to your hand-tuned values
- Train/test RMSE, MAE, R²
- End-to-end comparison: "PST only" vs "PST + learned features"
- Error distribution analysis

The `--alpha` flag controls L2 regularisation.  Start with 1.0; if weights look
unreasonable, increase to 5–10. If underfitting, try 0.1.


### Step 4: Compare against ClassicEvaluator

```bash
python tools/compare_evaluators.py \
    --stockfish /opt/homebrew/bin/stockfish \
    --weights src/chess_engine/learned_weights.json
```

Runs both evaluators on the 31 standard test positions and shows which is
closer to Stockfish for each.


### Step 5: Use in your engine

```python
from chess_engine.learned_evaluator import LearnedEvaluator
from chess_engine.search import SearchEngine

evaluator = LearnedEvaluator("src/chess_engine/learned_weights.json")
engine = SearchEngine(evaluator)

best_move, score, elapsed = engine.get_best_move(board, depth=4)
```

Drop-in replacement — same `.evaluate(board)` interface as `ClassicEvaluator`.
No performance impact since feature extraction is lightweight.


## Tunable Features (10 total)

| # | Feature | Description | Hand-tuned |
|---|---------|-------------|------------|
| 0 | `knight_mobility` | Net knight mobility (squares available) | 4cp/sq |
| 1 | `bishop_mobility` | Net bishop mobility | 5cp/sq |
| 2 | `rook_mobility` | Net rook mobility | 2cp/sq |
| 3 | `queen_mobility` | Net queen mobility | 1cp/sq |
| 4 | `doubled_pawns` | Doubled pawn count difference | −15cp |
| 5 | `isolated_pawns` | Isolated pawn count difference | −20cp |
| 6 | `passed_pawn_count` | Passed pawn count difference | ~20cp |
| 7 | `passed_pawn_advancement` | Rank-weighted passed pawn advantage | ~10cp |
| 8 | `bishop_pair` | Bishop pair indicator difference | 30cp |
| 9 | `tempo` | +1 white to move, −1 black | 15cp |


## What Stays Fixed

- PeSTO piece-square tables (midgame + endgame, all 6 piece types)
- PeSTO material values (P=82/94, N=337/281, B=365/297, R=477/512, Q=1025/936)
- Tapered evaluation formula (game phase calculation)

These are well-established values from the chess programming community and
don't benefit from re-tuning with this approach.


## Expected Results

With 50,000 positions from the Kaggle dataset:
- **Residual R² ≈ 0.15–0.40** — the tunable features explain a meaningful portion of the
  residual after PST, but the remaining variance comes from non-linear effects
  (king safety patterns, tactical motifs, piece coordination)
- **End-to-end RMSE improvement ≈ 5–15%** over PST-only baseline
- **Mobility weights** often shift noticeably from hand-tuned values
- **Pawn structure weights** tend to be refined (your biggest test errors are in
  pawn structure positions, so this is where improvement is most likely)


## File Structure

```
src/chess_engine/
    features.py              # Feature extraction + fixed PST baseline
    learned_evaluator.py     # Evaluator: fixed PST + learned weights
    learned_weights.json     # (generated) trained weights

tools/
    load_dataset.py          # Load Kaggle CSV or Lichess JSONL
    train_weights.py         # Train linear regression
    compare_evaluators.py    # Compare evaluators on test suite

data/
    chessData.csv            # (downloaded) raw Kaggle dataset
    training_set.csv         # (generated) prepared training data
```
