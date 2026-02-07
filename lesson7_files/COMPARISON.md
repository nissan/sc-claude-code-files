# Refactoring Comparison: Original vs New

This document captures the detailed comparison between the original outputs (`EDA_Refactored-original.ipynb`, `dashboard-original.py`) and the corrected versions (`EDA_Refactored.ipynb`, `dashboard.py`), explaining what changed and why.

---

## Part 1: Notebook Comparison

**Files:** `EDA_Refactored-original.ipynb` (27 cells) vs `EDA_Refactored.ipynb` (27 cells)

### Structure

| Cell Range | Original | New | Status |
|---|---|---|---|
| 0-4 | TOC, Intro, Config, Loading header, Imports | Same | Identical |
| 5 | Data loading | Uses `loader.load_summary` | Different |
| 6-12 | Dictionary, Prep, Sales data, Comparison, Metrics header, Report, Revenue header | Same | Identical |
| 13-14 | Revenue deep dive + chart | Emojis and threshold removed | Different |
| 15-21 | Product, Geo, Customer sections | Thresholds removed | Different |
| 22-23 | Summary header + executive summary | Emojis removed | Different |
| 24-25 | Recommendations section | Rewritten without emojis/thresholds | Different |
| 26 | Closing markdown | Minor edit | Different |

### Significant Differences

#### 1. Data loading (cell 5)

**Original** relies on `data_loader.py` printing directly during `load_raw_data()`:

```
Loaded orders: 10000 records
Loaded order_items: 16047 records
...
```

**New** uses `loader.load_summary` to control output:

```python
for name, info in loader.load_summary.items():
    print(f"  {name}: {info['records']:,} records ({info['status']})")
```

The new approach is better -- the notebook owns its output formatting rather than depending on side effects from a library call.

#### 2. Revenue analysis (cell 13)

**Original** has an emoji-based conditional interpretation:

```python
if revenue_metrics['revenue_growth_rate'] > 0:
    print("\n\u2705 Positive revenue growth indicates business expansion")
else:
    print("\n\u26a0\ufe0f Negative revenue growth requires attention")
```

**New** removes this entirely -- just presents the numbers.

#### 3. Product analysis (cell 16)

**Original** has a hardcoded threshold judgment:

```python
print(f"Market Concentration: {'High' if top_5_share > 70 else 'Moderate' if top_5_share > 50 else 'Low'}")
```

**New** removes this line, renames "CATEGORY INSIGHTS" to "CATEGORY SUMMARY", and reports the percentage factually.

#### 4. Geographic analysis (cell 18)

**Original** has:

```python
print(f"Geographic Diversity: {'High' if total_states > 40 else 'Moderate' if total_states > 20 else 'Low'}")
```

**New** removes this, renames "GEOGRAPHIC INSIGHTS" to "GEOGRAPHIC SUMMARY".

#### 5. Customer satisfaction (cell 20)

**Original** has a threshold-based rating and emoji indicators:

```python
satisfaction_level = 'Excellent' if avg_score >= 4.5 else 'Good' if avg_score >= 4.0 else ...
print(f"Overall Satisfaction Level: {satisfaction_level}")
if satisfaction_metrics['score_4_plus_percentage'] >= 80:
    print("\u2705 Strong customer satisfaction (80%+ give 4+ stars)")
```

**New** removes all of this -- just shows the raw percentages.

#### 6. Delivery analysis (cell 21)

**Original** has:

```python
delivery_rating = 'Excellent' if avg_delivery <= 3 else 'Good' if ... else 'Poor'
print(f"Delivery Performance Rating: {delivery_rating}")
print("\u26a0\ufe0f High percentage of slow deliveries needs attention")
```

**New** removes the rating and emoji, keeps only the factual delivery-satisfaction data.

#### 7. Executive summary (cell 23)

**Original** uses emojis as section prefixes:

```
\ud83d\udcca FINANCIAL PERFORMANCE:
   \u2022 Revenue Growth: \ud83d\udcc9 -2.5% vs 2022
\ud83d\udecd\ufe0f PRODUCT PERFORMANCE:
\ud83d\uddfa\ufe0f GEOGRAPHIC PERFORMANCE:
\u2b50 CUSTOMER EXPERIENCE:
```

**New** uses plain text headers without emojis or bullet characters.

#### 8. Recommendations section (cells 24-25)

**Original** has emoji-laden, threshold-driven prescriptive recommendations:

```python
recommendations.append("\ud83d\udd34 PRIORITY: Address negative revenue growth...")
recommendations.append("\ud83d\ude9a PRIORITY: Optimize logistics...")
```

**New** replaces this with a factual "Areas for Further Investigation" section that states observations with numbers rather than making judgments:

```python
observations.append(
    f"Revenue changed by {growth:+.1f}% year-over-year "
    f"(${revenue_metrics['total_revenue']:,.0f} vs "
    f"${revenue_metrics['previous_year_revenue']:,.0f})")
```

#### 9. Monthly trends label (cell 14)

Minor: "MONTHLY PERFORMANCE INSIGHTS:" (original) vs "MONTHLY PERFORMANCE:" (new).

#### 10. Saved outputs

**Original** has cached outputs from a prior run (actual data tables, chart images, print output). **New** has no cached outputs -- it's a clean notebook that needs to be run.

### Evaluation Against Success Criteria

| Criterion | Original | New |
|---|---|---|
| No icons/emojis in print or markdown | Fails (13+ emojis across 5 cells) | Passes |
| No assumed business thresholds | Fails (4 threshold systems) | Passes |
| Maintain all existing analyses | All metrics + prescriptive recommendations | All metrics + factual observations |
| Factual data presentation | Mixed -- data plus opinionated judgments | Pure data, reader draws conclusions |

**Where the original is arguably better:**

- It has cached outputs, so you can see results without running it.
- The Strategic Recommendations section adds value as a template for how to interpret results -- though it violates both the emoji and threshold rules.
- The emoji section headers in the executive summary are more visually scannable (if you don't mind the emoji rule).

**Where the new version is clearly better:**

- Correctly follows the "no icons" requirement.
- Correctly follows the "no business thresholds" requirement.
- Notebook controls its own output (cell 5) rather than depending on library print side effects.
- Cleaner separation of concerns -- the notebook presents data; the reader interprets it.

**Bottom line:** The original is a richer document with more commentary, but it violates two explicit success criteria. The new version trades that commentary for correctness against the spec.

---

## Part 2: Dashboard Comparison

**Files:** `dashboard-original.py` (530 lines) vs `dashboard.py` (542 lines)

### Structure

| | Original | New |
|---|---|---|
| Imports | 7 imports (incl. unused `plotly.express`, `make_subplots`, `datetime`, `BusinessMetricsCalculator`) | 5 imports (only what's used) |
| CSS | Same styling | Same styling (minor padding tweak) |
| Helpers | 2 functions (`format_currency`, `format_trend`) | 4 functions (renamed `format_currency_short`, `format_trend`, plus `_tick_currency`, `_nice_step`) |
| Chart builders | 4 functions | 4 functions (same set, rewritten) |
| Main layout | Same structure | Same structure |

### Significant Differences

#### 1. Y-axis tick formatting -- `$300K` vs `$300,000`

This is the single biggest functional difference.

**Original** uses Plotly's built-in `tickformat='$,.0f'`:

```python
yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickformat='$,.0f')
```

This produces axis labels like `$250,000`, `$300,000`.

**New** computes custom tick values with `_nice_step()` and `_tick_currency()`:

```python
tick_vals = list(np.arange(0, y_max + step, step))
tick_text = [_tick_currency(v) for v in tick_vals]
yaxis=dict(..., tickvals=tick_vals, ticktext=tick_text)
```

This produces `$0`, `$100K`, `$200K`, `$300K` -- matching the spec requirement.

Applied to both the revenue trend Y-axis and the category chart X-axis.

#### 2. Previous year line color -- consistent palette

**Original**: previous year uses orange `#ff7f0e`

**New**: previous year uses light blue `#7baaf0` (stays within the blue palette)

#### 3. Satisfaction chart -- avoids mutating input data

**Original** writes directly to the passed-in DataFrame:

```python
sales_data['delivery_category'] = sales_data['delivery_days'].apply(categorize_delivery)
```

This mutates the caller's data, which could cause side effects if the same DataFrame is reused.

**New** makes a copy first:

```python
tmp = sales_data.copy()
tmp['delivery_bucket'] = tmp['delivery_days'].apply(_bucket)
```

#### 4. Review score card -- layout order and empty stars

**Original** renders label on top, value in middle, stars below:

```html
<p class="metric-label">Average Review Score</p>
<p class="metric-value">4.1/5.0</p>
<p class="stars">\u2605\u2605\u2605\u2605</p>
```

**New** renders value on top, stars in middle, label as subtitle below -- matching the spec ("Large number with stars, Subtitle: Average Review Score"):

```html
<p class="metric-value">4.1/5.0</p>
<p class="stars">\u2605\u2605\u2605\u2605\u2606</p>
<p class="metric-label">Average Review Score</p>
```

Also adds empty star outlines to always show 5 positions, rather than only showing filled stars.

#### 5. `format_trend` -- edge case handling

**Original** only guards `previous == 0`:

```python
if previous == 0:
    return "N/A"
```

**New** also guards `pd.isna(previous)`:

```python
if previous == 0 or pd.isna(previous):
    return "N/A"
```

#### 6. `format_trend` -- zero-change boundary

**Original** treats exactly zero change as negative (green only for `> 0`):

```python
arrow = "\u2197" if change_pct > 0 else "\u2198"
```

**New** treats zero as positive (green for `>= 0`):

```python
arrow = "\u2197" if change_pct >= 0 else "\u2198"
```

#### 7. CSS -- minor tweaks

- Card padding: `1rem` (original) vs `1rem 1.25rem` (new) -- slightly more horizontal padding.
- Trend font size: `0.8rem` (original) vs `0.85rem` (new) -- slightly larger trend text.

#### 8. Code organization

**Original** is one flat file with no section separators.

**New** uses section comment banners grouping code into Data loading, Formatting helpers, Chart builders, and Main.

#### 9. Unused imports removed

**Original** imports `plotly.express`, `make_subplots`, `datetime`, and `BusinessMetricsCalculator` -- none of which are used.

**New** removes all of them.

### What's Identical

- Overall layout structure: Header (3-col), KPI row (4-col), Charts grid (2x2), Bottom row (2-col)
- Data flow: `load_and_process_data()` -> `create_sales_dataset()` -> metrics -> cards + charts
- All 4 chart types: revenue trend, category bar, choropleth map, satisfaction vs delivery
- KPI cards: same 4 metrics (Total Revenue, Monthly Growth, AOV, Total Orders)
- Bottom cards: same 2 metrics (Delivery Time with trend, Review Score with stars)
- Trend colors: green `#28a745` / red `#dc3545`
- Two decimal places on all trend indicators
- Blues colorscale on category chart and choropleth
- No emojis/icons anywhere
- Filters update all charts correctly

### Evaluation Against Spec

| Spec Requirement | Original | New |
|---|---|---|
| Y-axis as `$300K` | Fails -- shows `$300,000` | Passes |
| Blue gradient on categories | Passes (`Blues` colorscale) | Passes |
| Blue gradient on map | Passes | Passes |
| Dashed previous period line | Passes | Passes |
| Grid lines on revenue chart | Passes | Passes |
| Two decimal trend indicators | Passes | Passes |
| No icons | Passes | Passes |
| Uniform card heights | Passes (CSS) | Passes (CSS) |
| Review card: large number + stars + subtitle | Partially -- label on top, no empty stars | Passes -- value on top, filled+empty stars, subtitle below |
| Consistent color palette | Mixed -- orange for previous year | Passes -- light blue stays in blue family |
| Doesn't mutate input data | Fails -- writes to input DataFrame | Passes -- copies first |
| No unused imports | Fails -- 4 unused imports | Passes |

**The new version is the better output.** The critical improvement is the `$300K` axis formatting which the original couldn't do with Plotly's built-in `tickformat`. The review card layout, consistent blue palette, and defensive data handling are additional refinements.
