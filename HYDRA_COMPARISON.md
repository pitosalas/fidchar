# Hydra Refactoring Comparison

This document shows the differences between the original and Hydra-based `main.py`.

## Files Created

1. **fidchar/conf/config.yaml** - Hydra config (replaces root config.yaml)
2. **fidchar/config_schema.py** - Type-safe config dataclasses (optional but recommended)
3. **fidchar/main.py** - Refactored with Hydra
4. **fidchar/main_original.py** - Backup of original version

## Key Differences

### 1. Configuration Loading

**BEFORE (Original):**
```python
def load_config():
    """Load configuration from YAML file"""
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print("Warning: config.yaml not found, using defaults")
        return {
            "input_file": "../data.csv",
            "generate_html": False,
            # ... hardcoded defaults
        }

def main():
    config = load_config()
    input_file = config["input_file"]
```

**AFTER (Hydra):**
```python
@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    # Config automatically loaded and injected!
    input_file = cfg.input_file
```

**Benefits:**
- ✅ No manual YAML loading code
- ✅ Automatic config validation
- ✅ Type hints with DictConfig
- ✅ Defaults handled by Hydra

---

### 2. Extracting Nested Config

**BEFORE (Original):**
```python
# Awkward list comprehension with next()
consistent_config = next(
    (s.get("options", {}) for s in config.get("sections", [])
     if isinstance(s, dict) and s.get("name") == "consistent"),
    {}
)
min_years = consistent_config.get("min_years", 5)
min_amount = consistent_config.get("min_amount", 500)
```

**AFTER (Hydra):**
```python
# Cleaner helper function
consist_cfg = _get_section_options(cfg, "consistent")
min_years = consist_cfg.get("min_years", 5)
min_amount = consist_cfg.get("min_amount", 500)

# Helper is simpler to read:
def _get_section_options(cfg: DictConfig, section_name: str) -> dict:
    for section in cfg.sections:
        if isinstance(section, DictConfig) and section.get("name") == section_name:
            return section.get("options", {})
    return {}
```

**Benefits:**
- ✅ More readable
- ✅ Reusable function
- ✅ Type-safe with DictConfig

---

### 3. CLI Overrides

**BEFORE (Original):**
```bash
# Had to edit config.yaml or use env vars
python main.py
```

**AFTER (Hydra):**
```bash
# Override ANY config value from command line!
python main.py generate_html=false
python main.py input_file=../data2.csv
python main.py charity_navigator.app_id=1234
python main.py sections[2].options.min_years=15
```

**Benefits:**
- ✅ No need to edit config files for experiments
- ✅ Can override deeply nested values
- ✅ Great for testing different parameters

---

### 4. Config Visibility

**BEFORE (Original):**
```bash
# No way to see what config was used
```

**AFTER (Hydra):**
```python
# At end of main.py:
print("\n--- Configuration Used ---")
print(OmegaConf.to_yaml(cfg))
```

**Output:**
```yaml
--- Configuration Used ---
input_file: ../data.csv
output_dir: ../output
generate_html: false
generate_markdown: false
generate_textfile: true
charity_navigator:
  app_id: '3069'
  app_key: null
# ... full resolved config
```

**Benefits:**
- ✅ Always know exactly what config was used
- ✅ Great for debugging
- ✅ Reproducibility

---

### 5. Multi-Run Capability

**BEFORE (Original):**
```bash
# Had to manually run multiple times
python main.py  # edit config.yaml
python main.py  # edit config.yaml again
python main.py  # edit config.yaml again
```

**AFTER (Hydra):**
```bash
# Automatically run with different parameters!
python main.py -m sections[2].options.min_years=5,10,15

# Creates 3 separate output directories:
# outputs/2025-10-09/12-00-00/  (min_years=5)
# outputs/2025-10-09/12-00-01/  (min_years=10)
# outputs/2025-10-09/12-00-02/  (min_years=15)
```

**Benefits:**
- ✅ Parameter sweeps made easy
- ✅ Each run gets its own output directory
- ✅ Perfect for experiments and optimization

---

## Usage Examples

### Basic Usage
```bash
# Use default config
uv run python main.py

# Override single value
uv run python main.py generate_html=false

# Override multiple values
uv run python main.py generate_html=false generate_markdown=true
```

### Advanced Usage
```bash
# Override nested config
uv run python main.py charity_navigator.app_id=9999

# Override array elements
uv run python main.py sections[2].options.min_years=20

# Multi-run experiments
uv run python main.py -m sections[2].options.min_years=5,10,15,20
```

### View Config Without Running
```bash
# Show what config would be used
uv run python main.py --cfg job

# Show config structure
uv run python main.py --cfg all
```

---

## What Changed in Code

### Additions
- `import hydra` and `from omegaconf import DictConfig, OmegaConf`
- `@hydra.main()` decorator on main function
- Path handling for Hydra's working directory changes
- `OmegaConf.to_container()` to convert config to dict for backwards compatibility
- Config printing at end

### Removals
- `load_config()` function (no longer needed)
- Manual YAML loading with `yaml.safe_load()`
- Hardcoded default config dictionary

### Line Count
- **Original:** 129 lines
- **Hydra:** 156 lines
- **Difference:** +27 lines (mostly comments and config printing)

---

## How to Revert

**Status: Hydra version is now ACTIVE**

Original files have been archived:
- `archive/main_original.py` - Original main.py
- `archive/config_original.yaml` - Original config.yaml

To revert to the original non-Hydra version:

```bash
cd /Users/pitosalas/mydev/fidchar
cp archive/main_original.py fidchar/main.py
cp archive/config_original.yaml fidchar/config.yaml
rm -rf fidchar/conf/  # Remove Hydra config directory
```

To restore Hydra version after reverting:
```bash
cd /Users/pitosalas/mydev/fidchar
git checkout fidchar/main.py fidchar/conf/
```

---

## Should You Adopt Hydra?

### Pros
- ✅ CLI overrides make experimentation easy
- ✅ Multi-run capability for parameter sweeps
- ✅ Better config organization
- ✅ Automatic logging of used config
- ✅ Type safety with structured configs
- ✅ Industry standard (used by Meta, many ML projects)

### Cons
- ❌ Adds dependency (`hydra-core`, `omegaconf`, `antlr4-python3-runtime`)
- ❌ Learning curve for team members
- ❌ Working directory changes can be confusing
- ❌ Slight overhead (+27 lines of code)

### Recommendation
**Use Hydra if:**
- You frequently experiment with different parameters
- You want reproducible research/analysis
- You're building a tool others will use
- You value CLI flexibility over simplicity

**Stick with current approach if:**
- Config rarely changes
- Only you use the tool
- Simplicity is paramount
- Don't want extra dependencies
