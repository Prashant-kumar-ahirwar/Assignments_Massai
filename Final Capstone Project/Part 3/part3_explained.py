"""
PART 3 — REGRESSION ANALYSIS
==============================
This file explains every step done in Part 3.

Think of regression like this:
  You're a frontend dev. You notice that the more users visit your site (footfall),
  the more purchases happen (sales). You want to QUANTIFY that relationship:
  "For every 1 extra visitor, how many more £ do we make?"
  That's exactly what regression does.

Libraries:
  pandas      → table manipulation (like lodash for tables)
  numpy       → math (like JS Math object)
  statsmodels → statistics engine (like a calculator that also gives confidence scores)
  matplotlib  → charts (like Chart.js but for Python)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')   # no screen needed — saves to file
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD & UNDERSTAND THE DATA
# ─────────────────────────────────────────────────────────────────────────────

df = pd.read_excel('data/business_regression_data.xlsx')

print("=== DATASET OVERVIEW ===")
print(f"Shape: {df.shape}")          # (320, 14) = 320 rows, 14 columns
print(f"Columns: {list(df.columns)}")
print()

# Check for missing values — like checking for null/undefined in JS
print("=== MISSING VALUES ===")
print(df.isnull().sum())
# competitor_distance_km → 6 missing
# customer_rating        → 8 missing
print()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: HANDLE MISSING VALUES
# We use the MEDIAN to fill in missing values (more robust than mean)
# Like: value ?? median(column)  in JS
# ─────────────────────────────────────────────────────────────────────────────

df['competitor_distance_km'] = df['competitor_distance_km'].fillna(
    df['competitor_distance_km'].median()
)
df['customer_rating'] = df['customer_rating'].fillna(
    df['customer_rating'].median()
)

print("Missing values after imputation:", df.isnull().sum().sum())
# Should be 0 now


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: EXPLORE CORRELATIONS
# Correlation = how strongly do two variables move together?
# Range: -1 (perfect inverse) to +1 (perfect match), 0 = no relationship
# Like: does changing X always change Y in the same direction?
# ─────────────────────────────────────────────────────────────────────────────

numeric_cols = ['marketing_spend', 'footfall', 'avg_discount_pct', 'staff_count',
                'inventory_availability_pct', 'competitor_distance_km',
                'holiday_flag', 'customer_rating']

print("=== CORRELATIONS WITH monthly_sales ===")
for col in numeric_cols:
    r = df['monthly_sales'].corr(df[col])   # Pearson correlation coefficient
    bar = '█' * int(abs(r) * 20)            # simple visual bar
    direction = '+' if r > 0 else '-'
    print(f"  {col:<32} r={r:+.4f}  {direction}{bar}")
# Expected: footfall has highest positive correlation


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: SIMPLE LINEAR REGRESSION (SLR)
#
# Regression equation:  Y = β₀ + β₁·X
#   Y  = dependent variable (what we're predicting) = monthly_sales
#   X  = independent variable (the predictor)       = footfall
#   β₀ = intercept (value of Y when X = 0)          = like a starting point
#   β₁ = coefficient (how much Y changes per 1 unit of X)
#
# JS analogy: imagine a function:
#   function predictSales(footfall) {
#       return intercept + coefficient * footfall;
#   }
# Regression FINDS the best intercept and coefficient from the data.
# ─────────────────────────────────────────────────────────────────────────────

def run_slr(df, x_col, y_col='monthly_sales'):
    """
    Run a Simple Linear Regression.
    
    sm.add_constant() adds a column of 1s to represent the intercept (β₀).
    Without it, the regression would be forced through the origin (Y=0 when X=0).
    
    Like: [1, footfall] instead of just [footfall]
    The 'const' column handles the +b part of y = mx + b
    """
    X = sm.add_constant(df[[x_col]])   # add intercept column
    y = df[y_col]
    model = sm.OLS(y, X).fit()         # OLS = Ordinary Least Squares
    return model


# --- SLR Model 1: footfall ---
m1 = run_slr(df, 'footfall')
print("\n=== SLR 1: monthly_sales ~ footfall ===")
print(f"  Equation:     Sales = {m1.params['const']:,.0f} + {m1.params['footfall']:.4f} × footfall")
print(f"  R-squared:    {m1.rsquared:.4f}  ({m1.rsquared*100:.1f}% of sales variation explained)")
print(f"  P-value:      {m1.pvalues['footfall']:.2e}")
print(f"  Significant:  {'Yes' if m1.pvalues['footfall'] < 0.05 else 'No'}")
# R² = 0.7363 → footfall alone explains 73.6% of monthly sales variation → STRONG

# --- SLR Model 2: marketing_spend ---
m2 = run_slr(df, 'marketing_spend')
print("\n=== SLR 2: monthly_sales ~ marketing_spend ===")
print(f"  Equation:     Sales = {m2.params['const']:,.0f} + {m2.params['marketing_spend']:.4f} × marketing_spend")
print(f"  R-squared:    {m2.rsquared:.4f}  ({m2.rsquared*100:.1f}% of sales variation explained)")
print(f"  P-value:      {m2.pvalues['marketing_spend']:.2e}")
# R² = 0.1672 → marketing alone explains only 16.7% → WEAK on its own

# --- SLR Model 3: staff_count ---
m3 = run_slr(df, 'staff_count')
print("\n=== SLR 3: monthly_sales ~ staff_count ===")
print(f"  Equation:     Sales = {m3.params['const']:,.0f} + {m3.params['staff_count']:.0f} × staff_count")
print(f"  R-squared:    {m3.rsquared:.4f}  ({m3.rsquared*100:.1f}% of sales variation explained)")
print(f"  P-value:      {m3.pvalues['staff_count']:.2e}")
# R² = 0.6523 → 65.2% explained → STRONG but likely collinear with footfall


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: DUMMY VARIABLES
#
# Regression only works with NUMBERS.
# But our data has text categories: region ('East','North','South','West')
# and store_type ('Airport','High Street','Mall','Residential').
#
# Dummy variables convert categories into 0/1 numbers.
#
# Example for region (4 categories → 3 dummies):
#   East  → region_North=0, region_South=0, region_West=0  (reference)
#   North → region_North=1, region_South=0, region_West=0
#   South → region_North=0, region_South=1, region_West=0
#   West  → region_North=0, region_South=0, region_West=1
#
# WHY drop one? If we kept all 4, we'd have PERFECT multicollinearity
# (region_North + region_South + region_West + region_East always = 1).
# The dropped category becomes the "reference" — all other dummies
# are compared AGAINST it.
#
# JS analogy: like a radio button group — only one can be "active" at a time.
# ─────────────────────────────────────────────────────────────────────────────

# pd.get_dummies() is like: categories.map(c => ({ [c]: value === c ? 1 : 0 }))
dummies_region = pd.get_dummies(df['region'],     prefix='region', drop_first=True).astype(int)
dummies_store  = pd.get_dummies(df['store_type'], prefix='store',  drop_first=True).astype(int)

print("\n=== DUMMY VARIABLES CREATED ===")
print("Region dummies (reference = East):", list(dummies_region.columns))
print("Store type dummies (reference = Airport):", list(dummies_store.columns))
print()
print("Sample (first 5 rows):")
print(pd.concat([df[['store_id','region','store_type']], dummies_region, dummies_store], axis=1).head())


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: MULTIPLE REGRESSION
#
# Now we use ALL predictors at once.
# Equation: Y = β₀ + β₁·X₁ + β₂·X₂ + ... + βₙ·Xₙ
#
# The KEY advantage over SLR:
# "Holding all other factors constant, what is the effect of X on Y?"
#
# Example: staff_count coefficient in SLR = 16,984 (seems huge)
# But in MLR, once we control for footfall too, staff_count drops to 3,188.
# Why? Because in SLR, staff_count was "stealing credit" from footfall
# (busy stores need more staff AND generate more sales — confounding!).
#
# JS analogy: like A/B testing with multiple variables isolated.
# ─────────────────────────────────────────────────────────────────────────────

numeric_features = [
    'marketing_spend',
    'footfall',
    'inventory_availability_pct',
    'avg_discount_pct',
    'customer_rating',
    'staff_count',
    'holiday_flag'
]

# Combine numeric features with dummy variables
# Like: [...numericCols, ...dummyCols]
X_multi = pd.concat([df[numeric_features], dummies_region, dummies_store], axis=1)
X_multi = sm.add_constant(X_multi)   # add intercept

y = df['monthly_sales']
model_multi = sm.OLS(y, X_multi).fit()

print("\n=== MULTIPLE REGRESSION RESULTS ===")
print(f"R-squared:          {model_multi.rsquared:.4f}")
print(f"Adjusted R-squared: {model_multi.rsquared_adj:.4f}")
print(f"F-statistic p-value:{model_multi.f_pvalue:.2e}")
print()
print(f"{'Variable':<35} {'Coefficient':>14} {'P-value':>10} {'Sig?':>6}")
print("-" * 70)
for var in model_multi.params.index:
    coef = model_multi.params[var]
    pval = model_multi.pvalues[var]
    sig  = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else 'ns'))
    print(f"  {var:<33} {coef:>14,.2f} {pval:>10.4f} {sig:>6}")

print()
print("KEY INSIGHTS:")
print(f"  footfall:                 £{model_multi.params['footfall']:.2f} per visitor → STRONGEST driver")
print(f"  marketing_spend:          £{model_multi.params['marketing_spend']:.2f} per £1 spent")
print(f"  inventory_availability:   £{model_multi.params['inventory_availability_pct']:,.0f} per 1% improvement")
print(f"  customer_rating:          £{model_multi.params['customer_rating']:,.0f} per 1-star improvement")
print(f"  store_Residential:        £{model_multi.params['store_Residential']:,.0f} vs Airport (penalty)")
print(f"  avg_discount_pct:         p={model_multi.pvalues['avg_discount_pct']:.3f} → NOT significant")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: HOW TO INTERPRET KEY STATISTICS
#
# R-squared (R²):
#   "What % of the variation in Y does our model explain?"
#   R²=0.84 means: 84% of why sales differ between stores is captured by our variables.
#   The remaining 16% is unexplained (unmeasured factors).
#   JS analogy: like a test score — higher is better, max is 1.0 (100%).
#
# Adjusted R²:
#   Like R², but penalises for adding too many variables.
#   If you add a useless variable, R² goes up slightly but Adj-R² goes down.
#   Always compare models using Adj-R².
#
# P-value:
#   "If this variable had NO real effect, what's the probability we'd still
#    see a coefficient this large just by random chance?"
#   p < 0.05 → less than 5% chance it's random → we trust the result.
#   p > 0.05 → could be random noise → don't rely on this variable.
#   JS analogy: like a confidence level in an API response.
#
# Coefficient:
#   "For each 1-unit increase in X, Y changes by this much."
#   Positive = X and Y move in the same direction.
#   Negative = X and Y move in opposite directions.
#
# F-statistic:
#   Tests whether the ENTIRE model is significant (not just individual variables).
#   p < 0.05 → model as a whole explains something meaningful.
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: RESIDUAL ANALYSIS
#
# Residual = Actual Sales − Predicted Sales
#   Positive residual → store sold MORE than predicted (over-performer)
#   Negative residual → store sold LESS than predicted (under-performer)
#
# JS analogy: like the diff between expected API response time and actual time.
# If diff is huge, something unusual happened worth investigating.
# ─────────────────────────────────────────────────────────────────────────────

df['predicted'] = model_multi.fittedvalues    # model's predicted values
df['residual']  = df['monthly_sales'] - df['predicted']

print("\n=== TOP 5 POSITIVE RESIDUALS (over-performers) ===")
top5 = df.nlargest(5, 'residual')[['store_id','region','store_type','monthly_sales','predicted','residual']]
print(top5.to_string(index=False))

print("\n=== TOP 5 NEGATIVE RESIDUALS (under-performers) ===")
bot5 = df.nsmallest(5, 'residual')[['store_id','region','store_type','monthly_sales','predicted','residual']]
print(bot5.to_string(index=False))

print(f"\nAverage residual (should be ~0):  {df['residual'].mean():.4f}")
print(f"Std dev of residuals:             £{df['residual'].std():,.0f}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 9: CREATE A SCATTER PLOT (Actual vs Predicted)
# Like a Chart.js scatter chart — points close to the diagonal = good model
# ─────────────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Regression Diagnostics', fontsize=14, fontweight='bold')

# Chart 1: Actual vs Predicted
ax1 = axes[0]
ax1.scatter(df['predicted'], df['monthly_sales'], alpha=0.5, color='#2E75B6', s=30)
lim = [df['predicted'].min() - 10000, df['monthly_sales'].max() + 10000]
ax1.plot(lim, lim, 'r--', lw=2, label='Perfect prediction')
ax1.set_xlabel('Predicted Sales (£)')
ax1.set_ylabel('Actual Sales (£)')
ax1.set_title(f'Actual vs Predicted  (R²={model_multi.rsquared:.4f})')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Chart 2: Residuals histogram
ax2 = axes[1]
ax2.hist(df['residual'], bins=30, color='#2E75B6', edgecolor='white', alpha=0.8)
ax2.axvline(0, color='red', lw=2, linestyle='--', label='Zero line')
ax2.set_xlabel('Residual (£)')
ax2.set_ylabel('Frequency')
ax2.set_title('Residual Distribution\n(should be roughly bell-shaped around 0)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('residual_plots.png', dpi=120, bbox_inches='tight')
plt.close()
print("\nresidual_plots.png saved")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 10: PREDICTION EXAMPLE
# How to use the model to predict sales for a hypothetical store
# Like calling a function with new inputs
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== PREDICTION EXAMPLE ===")
print("Scenario: New Mall store in West region with average characteristics")

new_store = pd.DataFrame({
    'const':                      [1],
    'marketing_spend':            [55000],    # £55K marketing spend
    'footfall':                   [7000],     # 7,000 visitors/month
    'inventory_availability_pct': [90],       # 90% in stock
    'avg_discount_pct':           [0.12],     # 12% average discount
    'customer_rating':            [4.0],      # 4-star rating
    'staff_count':                [16],       # 16 staff
    'holiday_flag':               [0],        # non-holiday month
    'region_North':               [0],
    'region_South':               [0],
    'region_West':                [1],        # West region
    'store_High Street':          [0],
    'store_Mall':                 [1],        # Mall store type
    'store_Residential':          [0],
})

# Make sure column order matches training data
new_store = new_store[model_multi.model.exog_names]
predicted_sales = model_multi.predict(new_store)[0]
print(f"Predicted monthly sales: £{predicted_sales:,.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION CONCEPTS SUMMARY (for a JS developer)
# ─────────────────────────────────────────────────────────────────────────────
"""
CONCEPT               PLAIN ENGLISH                              JS ANALOGY
────────────────────────────────────────────────────────────────────────────────
Regression            Find best-fit line through data points     Array.reduce to find best params
Y = β₀ + β₁X         Sales = intercept + coef × footfall        f(x) = b + m*x
R-squared (R²)        % of Y variation explained by model        Test score: 0–1, higher is better
P-value               Probability result is random luck          Confidence score: < 0.05 = trust it
Coefficient (β)       Y changes by this per 1 unit of X         Multiplier in the equation
Intercept (β₀)        Y value when all X = 0                    Default/starting value
Dummy variable        Category converted to 0/1                 Boolean flag for each category
Reference category    The "default" dummy (all others vs this)  Default case in a switch statement
Residual              Actual − Predicted                         Error margin / diff from expected
Adj R-squared         R² penalised for too many variables        Like R² but penalises overfitting
F-statistic           Is the WHOLE model significant?           Global test before testing each var
OLS                   Method to find best-fit line               Minimises sum of (actual−predicted)²
Multicollinearity     Two predictors are correlated each other   Like two state vars that always change together
Overfitting           Model memorises data, can't generalise    Like memorising test answers vs understanding
"""

print("\nPart 3 explanation complete!")
print(f"\nFINAL MODEL SUMMARY:")
print(f"  Type: Multiple Linear Regression")
print(f"  R²: {model_multi.rsquared:.4f} — explains {model_multi.rsquared*100:.1f}% of sales variation")
print(f"  Top drivers: footfall > inventory > store_type > customer_rating > marketing")
print(f"  Not significant: avg_discount_pct, region_North, store_Mall")
print(f"  Recommendation: Drive footfall, improve inventory & ratings, prefer Airport/Mall locations")
