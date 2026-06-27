# Model Equations & Coefficient Explanations
**Project:** Retail Chain — Monthly Sales Driver Analysis

---

## Simple Regression Equations

### SLR 1: Footfall Model
```
monthly_sales = 445,051 + 35.68 × footfall
```
**R² = 0.7363**

| Term | Value | Plain English |
|------|-------|---------------|
| 445,051 | Intercept | Predicted sales if zero visitors walk in (theoretical baseline) |
| 35.68 | Coefficient | Every additional visitor to the store is associated with £35.68 more in monthly sales |

**Business meaning:** Footfall is the single strongest individual predictor of sales. A store with 1,000 more monthly visitors than another should generate approximately £35,680 more in sales, all else equal.

---

### SLR 2: Marketing Spend Model
```
monthly_sales = 560,720 + 2.13 × marketing_spend
```
**R² = 0.1672**

| Term | Value | Plain English |
|------|-------|---------------|
| 560,720 | Intercept | Baseline sales with zero marketing spend |
| 2.13 | Coefficient | Every £1 extra in marketing is associated with £2.13 more in monthly sales |

**Business meaning:** Shows a positive but weak return. Marketing alone explains only 16.7% of sales variance — many other factors matter more. The £2.13 return per £1 spent sounds good but is inflated because busier stores both spend more on marketing and have more sales.

---

### SLR 3: Staff Count Model
```
monthly_sales = 399,986 + 16,984 × staff_count
```
**R² = 0.6523**

| Term | Value | Plain English |
|------|-------|---------------|
| 399,986 | Intercept | Baseline sales with zero staff (theoretical) |
| 16,984 | Coefficient | Each additional staff member is associated with £16,984 more in monthly sales |

**Business meaning:** Staff count is strongly linked to sales. Note: this doesn't mean hiring more staff will automatically increase sales — larger, busier stores both need more staff and naturally generate more sales (reverse causation risk).

---

## Multiple Regression Equation (Final Model)

```
monthly_sales =   69,233
              +    1.1748 × marketing_spend
              +   27.8879 × footfall
              + 3,112.45  × inventory_availability_pct
              - 51,589.43 × avg_discount_pct           [NOT significant]
              + 13,389.48 × customer_rating
              +  3,187.73 × staff_count
              + 14,744.34 × holiday_flag
              +  5,419.91 × region_North               [NOT significant]
              + 19,519.27 × region_South
              + 19,257.58 × region_West
              - 22,607.77 × store_High Street
              - 11,777.77 × store_Mall                 [NOT significant]
              - 42,015.45 × store_Residential
```
**R² = 0.8380 | Adjusted R² = 0.8311**

---

## Coefficient Explanations (Plain English)

### Numeric Variables

| Variable | Coefficient | Meaning |
|----------|-------------|---------|
| marketing_spend | +1.1748 | Each £1 extra in marketing → +£1.17 in sales (after controlling for footfall and other factors) |
| footfall | +27.8879 | Each additional monthly visitor → +£27.89 in sales |
| inventory_availability_pct | +3,112.45 | Each 1 percentage point better stock availability → +£3,112 in sales |
| avg_discount_pct | −51,589 | **Not significant (p=0.15)** — discount % has no reliably measurable effect in this model |
| customer_rating | +13,389 | Each 1-star improvement in rating → +£13,389 in sales |
| staff_count | +3,188 | Each additional staff member → +£3,188 in sales (much smaller than SLR because footfall is now controlled) |
| holiday_flag | +14,744 | Holiday months generate £14,744 more than non-holiday months |

---

## Dummy Variable Explanations

### What is a Dummy Variable?

A dummy variable converts a category (like "region") into a number the regression can use. It is always 0 or 1 — like a switch.

**Example for region:**
- East = reference (baseline) — represented by all region dummies being 0
- North store → region_North = 1, region_South = 0, region_West = 0
- South store → region_North = 0, region_South = 1, region_West = 0

The coefficient tells us: *"How much more (or less) does this category earn compared to the reference?"*

---

### Region Dummies (Reference Category = **East**)

| Dummy | Coefficient | Meaning |
|-------|-------------|---------|
| region_North | +5,420 | **Not significant (p=0.44)** — North performs similarly to East |
| region_South | +19,519 | South stores earn £19,519 more per month than East stores (p=0.006) |
| region_West | +19,258 | West stores earn £19,258 more per month than East stores (p=0.002) |

**Why East as reference?** East has the most stores and is the baseline market. All other regions are compared against it.

**Interpretation:** A store in South or West will generate roughly £19,000–£20,000 more per month than a comparable East store, holding all other factors constant.

---

### Store Type Dummies (Reference Category = **Airport**)

| Dummy | Coefficient | Meaning |
|-------|-------------|---------|
| store_High Street | −22,608 | High Street stores earn £22,608 LESS per month than Airport stores (p=0.014) |
| store_Mall | −11,778 | **Not significant (p=0.22)** — Mall stores perform similarly to Airport stores |
| store_Residential | −42,015 | Residential stores earn £42,015 LESS per month than Airport stores (p<0.001) |

**Why Airport as reference?** Airport stores are a distinct premium category. Comparing all other types against Airport reveals how much the location type impacts sales.

**Interpretation:** Airport stores are the best-performing store type. Residential stores are the weakest, earning over £42,000 less per month than equivalent Airport stores.

---

## Final Model Selected

**Model 4 — Multiple Linear Regression** is the final model.

**Reasons:**
1. Highest R² (0.8380) — explains 83.8% of sales variation
2. Only model that controls for confounders (e.g. staff_count effect is isolated from footfall)
3. Includes both numeric and categorical (dummy) variables
4. Statistically significant overall (F-test p < 0.0001)
5. Most actionable — gives a separate lever for each business decision
6. Adjusted R² (0.8311) is close to R² — model is not overfitted

**Variables NOT to over-interpret:**
- `avg_discount_pct` (p=0.15) — not significant, discount strategy unclear from this data alone
- `region_North` (p=0.44) — North is statistically indistinguishable from East
- `store_Mall` (p=0.22) — Mall performs similarly to Airport, no significant gap
