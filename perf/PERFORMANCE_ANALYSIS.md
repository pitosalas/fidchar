# Performance Analysis Results

## ✅ OPTIMIZATION COMPLETE

**BEFORE optimization:** 55.2 seconds
**AFTER optimization:** 17-18 seconds
**SPEEDUP:** 3x faster (67% reduction)

**Total function calls:** 74,367,582 calls → Significantly reduced

## Major Bottlenecks Identified

### 1. 🔴 **Charity Evaluations** (51.8s / 93.8% of total time)
**File:** `charity_evaluator.py:13(get_charity_evaluations)`

- **Time:** 51.851 seconds
- **Calls:** 1 time
- **Problem:** Evaluating 203 charities sequentially

**Breakdown:**
- `evaluate_charity()`: 30.6s (203 calls × 0.151s each)
  - **Sleep delays**: 21.1s (203 × 0.104s) - Rate limiting!
  - CharityNavigator API: 14.4s (66 calls × 0.215s each)
  - YAML config loading: 13.9s (814 loads!)
  - Client initialization: 11.1s (609 times!)

### 2. 🟡 **Configuration Loading** (13.9s / 25% of total time)
**File:** Multiple YAML loads

- **Time:** 13.9 seconds
- **Calls:** 814 times
- **Problem:** Loading config.yaml 814 times (should be once!)
  - 203 charities × 4 = ~812 loads (once per API client per charity)

### 3. 🟡 **Client Initialization** (11.1s / 20% of total time)
**File:** `base_client.py:11(__init__)`

- **Time:** 11.1 seconds
- **Calls:** 609 times
- **Problem:** Creating new API clients for each charity evaluation
  - 203 charities × 3 clients each = 609 initializations

### 4. 🟢 **Network I/O** (8.4s / 15% of total time)
- SSL handshakes: 2.5s (66 connections)
- Socket connections: 2.0s
- Reading responses: 8.4s
- **Note:** This is acceptable - network calls are inherently slow

## Recommendations (Priority Order)

### HIGH PRIORITY

**1. Cache Configuration Loading** ⚡ **CRITICAL**
```python
# Currently: Loading config 814 times
# Fix: Load once and reuse
config = load_config_once()  # Save ~13.9s
```

**2. Reuse API Clients** ⚡ **CRITICAL**
```python
# Currently: Creating 609 client instances
# Fix: Create 3 clients (ProPublica, CharityAPI, CharityNavigator) and reuse
clients = create_clients_once(config)  # Save ~11.1s
```

**3. Parallel Charity Evaluations** ⚡ **HIGH**
```python
# Currently: 203 charities × 0.151s = 30.6s sequential
# Fix: Use ThreadPoolExecutor or multiprocessing
# Potential speedup: 5-10x on multi-core system
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(evaluate_charity, charity_list)
# Estimated savings: ~25-28s
```

### MEDIUM PRIORITY

**4. Reduce Sleep Time** 🔧
```python
# Currently: 21.1s sleeping for rate limiting
# Fix: Only sleep when actually calling CharityNavigator
# Estimated savings: ~15s (sleep only for 66 calls instead of 203)
```

**5. Batch CharityNavigator Queries** 🔧
```python
# Currently: 66 individual GraphQL calls
# CharityNavigator supports bulk queries via afterEin
# Could reduce to 1-3 API calls
# Estimated savings: ~12-13s
```

### LOW PRIORITY

**6. Cache Charity Evaluations** 💾
```python
# Cache evaluation results to disk
# Only re-evaluate if data is stale (e.g., > 7 days old)
```

## Expected Performance Improvements

| Optimization | Time Saved | Difficulty | Priority |
|-------------|------------|------------|----------|
| Cache config loading | ~13.9s | Easy | ⚡ HIGH |
| Reuse API clients | ~11.1s | Easy | ⚡ HIGH |
| Parallel evaluations | ~25s | Medium | ⚡ HIGH |
| Smart rate limiting | ~15s | Easy | 🔧 MEDIUM |
| Batch CN queries | ~13s | Hard | 🔧 MEDIUM |

**Total potential speedup:** 55s → 5-10s (5-10x faster!)

## ✅ Implemented Optimizations

### 1. ✅ **Batch Evaluation with Shared Resources** - COMPLETE
**Implementation:** Created `batch_evaluate()` function in `charapi/api/charity_evaluator.py`

**Changes:**
- Load config once instead of 814 times → **Saves 13.9s**
- Create API clients once instead of 609 times → **Saves 11.1s**
- Removed sleep calls from loop (cache handles most requests) → **Saves ~15s**

**Files modified:**
- `/Users/pitosalas/mydev/charapi/charapi/api/charity_evaluator.py` - Added `batch_evaluate()` function
- `/Users/pitosalas/mydev/fidchar/fidchar/reports/charity_evaluator.py` - Refactored to use `batch_evaluate()`

**Total time saved:** ~40 seconds (from 55s to 17s)

## Potential Future Optimizations

### 2. **Parallel Charity Evaluations** 🔧 (Not yet implemented)
```python
# Currently: 203 charities evaluated sequentially
# Could use: ThreadPoolExecutor for concurrent API calls
# Potential additional speedup: 2-3x (down to 5-8 seconds)
```

## Code Locations to Fix

1. `charity_evaluator.py:50` - `_load_config()` called 203 times
2. `charity_evaluator.py:57` - `_create_clients()` called 203 times
3. `charity_evaluator.py:16` - `evaluate_charity()` runs sequentially
4. `charity_evaluator.py` - Sleep in every evaluation (should be conditional)

## Detailed Profiling Commands

```bash
# Run basic profiling
uv run python -m cProfile -s cumulative main.py 2>&1 | head -100

# Save detailed profile
uv run python -m cProfile -o profile.stats main.py

# Analyze interactively
python -m pstats profile.stats
>>> sort cumtime
>>> stats 30
```
