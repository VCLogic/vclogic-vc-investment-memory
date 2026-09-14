"""Portable defaults for investor wiki construction."""
import json
from pathlib import Path

MODEL = 'gpt-5.6-sol'
THIN_CORPUS_CHARS = 600_000
BATCH_CHARS = 30_000
TAXONOMY = json.loads(Path(__file__).with_name('taxonomy.json').read_text())
LABELS = {row['label']: row['coarse_parent'] for row in TAXONOMY}
DIMENSIONS = ('founder_team', 'market_opportunity', 'competition_defensibility',
              'product_solution', 'traction_growth', 'business_model_economics',
              'deal_terms_valuation', 'timing', 'investor_fit_constraints')
