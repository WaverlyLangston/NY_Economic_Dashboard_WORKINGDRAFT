"""
Runs all data fetchers in the correct order.

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
        return result, True
    except Exception as e:
        import traceback
        print(f"  ✗ {name} FAILED: {e}")
        traceback.print_exc()
        return None, False

def main():
    print(f"\n{'='*60}")
    print(f"  NY Economic Dashboard — Data Refresh")
    print(f"  Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    from scripts.fetchers import census_pep, census_bfs, census_acs
    from scripts.fetchers import bls_laus, bls_ces, bls_jolts
    from scripts.fetchers import bea_gdp, irs_migration

    failed = []

    # 1. Population estimates first (needed by BFS for per-capita)
    pop_df, pep_ok = run_step("Census PEP (Population)", census_pep.fetch)
    if not pep_ok:
        failed.append("Census PEP")

    # 2. Business Formation Statistics (uses pop_df for per capita)
    #    Skip if PEP failed to preserve existing per-capita values in bfs.json
    if pep_ok:
        _, bfs_ok = run_step("Census BFS (Business Formation)", census_bfs.fetch, population_df=pop_df)
        if not bfs_ok:
            failed.append("Census BFS")
    else:
        print("\n  Skipping Census BFS: PEP dependency unavailable — keeping existing data")
        failed.append("Census BFS")

    # 3. ACS demographics, housing, income, poverty
    _, acs_ok = run_step("Census ACS (Demographics/Housing/Income/Poverty)", census_acs.fetch)
    if not acs_ok:
        failed.append("Census ACS")

    # 4. BLS labor force
    _, laus_ok = run_step("BLS LAUS (Labor Force)", bls_laus.fetch)
    if not laus_ok:
        failed.append("BLS LAUS")

    # 5. BLS employment by industry
    _, ces_ok = run_step("BLS CES (Employment by Industry)", bls_ces.fetch)
    if not ces_ok:
        failed.append("BLS CES")

    # 6. BLS job openings
    _, jolts_ok = run_step("BLS JOLTS (Job Openings)", bls_jolts.fetch)
    if not jolts_ok:
        failed.append("BLS JOLTS")

    # 7. BEA GDP (most API calls — keep at end, rate limit cautious)
    _, bea_ok = run_step("BEA GDP (State GDP)", bea_gdp.fetch)
    if not bea_ok:
        failed.append("BEA GDP")

    # 8. IRS Migration
    _, irs_ok = run_step("IRS Migration", irs_migration.fetch)
    if not irs_ok:
        failed.append("IRS Migration")

    # 9. Write metadata only if all sources succeeded; otherwise preserve existing timestamps
    if not failed:
        meta = {
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_updated_display": datetime.utcnow().strftime("%B %d, %Y"),
        }
        save_json(meta, OUTPUT_FILES["metadata"])
        print("\n  All sources updated — metadata timestamp refreshed.")
    else:
        print(f"\n  ⚠ Failed sources: {', '.join(failed)}")
        print("  Metadata timestamp NOT updated — existing dates reflect cached data.")

    print(f"\n{'='*60}")
    print("  All data fetching complete.")
    print(f"  Data saved to: ./{DATA_DIR}/")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
