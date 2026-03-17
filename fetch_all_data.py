"""
fetch_all_data.py
Orchestrates all data fetchers in the correct order.
Run locally or via GitHub Actions daily.

Usage:
    python scripts/fetch_all_data.py

Environment variables required:
    CENSUS_API_KEY, BLS_API_KEY, BEA_API_KEY
"""
import sys, os, json, time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import OUTPUT_FILES, DATA_DIR, DOCS_DIR
from scripts.fetchers.utils import save_json

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

def run_step(name, fn, *args, **kwargs):
    print(f"\n{'='*60}")
    print(f"  STEP: {name}")
    print(f"{'='*60}")
    t0 = time.time()
    try:
        result = fn(*args, **kwargs)
        elapsed = time.time() - t0
        print(f"  ✓ {name} completed in {elapsed:.1f}s")
        return result
    except Exception as e:
        import traceback
        print(f"  ✗ {name} FAILED: {e}")
        traceback.print_exc()
        return None

def main():
    print(f"\n{'='*60}")
    print(f"  NY Economic Dashboard — Data Refresh")
    print(f"  Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    from scripts.fetchers import census_pep, census_bfs, census_acs
    from scripts.fetchers import bls_laus, bls_ces, bls_jolts
    from scripts.fetchers import bea_gdp, irs_migration

    # 1. Population estimates first (needed by BFS for per-capita)
    pop_df = run_step("Census PEP (Population)", census_pep.fetch)

    # 2. Business Formation Statistics (uses pop_df for per capita)
    run_step("Census BFS (Business Formation)", census_bfs.fetch, population_df=pop_df)

    # 3. ACS demographics, housing, income, poverty
    run_step("Census ACS (Demographics/Housing/Income/Poverty)", census_acs.fetch)

    # 4. BLS labor force
    run_step("BLS LAUS (Labor Force)", bls_laus.fetch)

    # 5. BLS employment by industry
    run_step("BLS CES (Employment by Industry)", bls_ces.fetch)

    # 6. BLS job openings
    run_step("BLS JOLTS (Job Openings)", bls_jolts.fetch)

    # 7. BEA GDP (most API calls — keep at end, rate limit cautious)
    run_step("BEA GDP (State GDP)", bea_gdp.fetch)

    # 8. IRS Migration
    run_step("IRS Migration", irs_migration.fetch)

    # 9. Write metadata
    meta = {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_updated_display": datetime.utcnow().strftime("%B %d, %Y"),
    }
    save_json(meta, OUTPUT_FILES["metadata"])

    print(f"\n{'='*60}")
    print("  All data fetching complete.")
    print(f"  Data saved to: ./{DATA_DIR}/")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
