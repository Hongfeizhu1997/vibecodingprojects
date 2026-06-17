# ISG SSR — Model Explainability: How Recommendations Are Made

> Audience: Business Stakeholders · Date: May 2026

---

## Infographic Quick Reference

> Condensed summary for infographic designers. Full details in sections below.

- **Core Question**: "Why was Service A recommended over Service B for this customer?"
- **Layer 1 — Recall** (Rule-Based): Engine I (cold-start, association rules) + Engine II (warm-start, popularity)
- **Layer 2 — Ranking** (XGBoost + SHAP): Multi-class softprob, K varies by Geo (NA=56, LA=31). Every prediction decomposable via SHAP
- **Layer 3 — Business Rules**: geo_availability, eol_check, compliance, baseline calibration
- **Layer 4 — Add-On**: Co-occurrence statistics per add-on module. Mutual exclusivity within each type
- **Custom Loss**: Single-direction price tilt (prob close → tilt toward higher-price service). Custom Loss = Accuracy Loss + β × Price Tilt (β dynamic: 0.5→0.1)
- **Safety Nets**: Three human-in-the-loop gates — Deployment Gate, GBB Review, Add-on Review
- **Explanations**: LLM (Vetraflow+ChatGPT) translates SHAP → natural language per audience (Internal / Customer)

---

## Executive Summary

The recommendation engine is **not a black box**. Every recommendation can be traced to specific factors. The system combines three layers of logic, all of which are auditable:

| Layer | Method | Transparency |
|-------|--------|-------------|
| **Recall** (Candidate Selection) | Association Rules + Popularity Statistics | Fully transparent — rule-based |
| **Ranking** (Scoring & Ordering) | XGBoost with Feature Importance | Model-driven, fully explainable via SHAP |
| **Business Rules** (Final Filter) | Explicit Business Logic | Fully transparent — human-defined rules |
| **Add-On** (Upsell) | Association Rules | Fully transparent — co-occurrence statistics |

---

## 1. What Drives Each Recommendation?

Every bid passes through the pipeline. At the Ranking stage, XGBoost scores each candidate service based on features extracted from the bid. We can decompose any single recommendation to answer: **"Why was Service A recommended over Service B for this customer?"**

### Top-Level Feature Categories (What the Model Considers)

| Category | Example Features | Business Meaning |
|----------|-----------------|------------------|
| **Hardware Fit** | Machine type, config specs, product family | "This service was designed for this hardware" |
| **Customer Context** | Segment, industry, DMU size | "Similar enterprise customers typically choose this" |
| **Geographic Norms** | Country, region | "This is the standard warranty in NA" |
| **Deal Economics** | Hardware value, contract type | "The service price is proportionate to the hardware" |
| **Historical Patterns** | Past attach rates for similar bids | "75% of comparable bids selected this service" |

### Per-Recommendation Explanation (SHAP)

For any single recommendation, we can produce a **waterfall chart** showing exactly which features pushed the score up or down:

```
Example: "Why 3-Year Onsite Warranty was ranked #1?"

  Base Rate  .......................................................... 0.45
  + Hardware is ThinkSystem SR650 .................................... +0.18
  + Customer Segment = Enterprise .................................... +0.12
  + Country = USA .................................................... +0.08
  + Hardware Value > $50K ............................................ +0.10
  - Contract Type = One-Time (not Subscription) ...................... -0.05
  ─────────────────────────────────────────────────────────────────────
  Final Score ........................................................ 0.88  → Rank #1
```

This is **not** a conceptual illustration — SHAP values are mathematically computed from the model and can be produced for every single prediction in real time.

---

## 2. The Transparent Parts (No ML Involved)

### Stage 3 — Recall (Fully Rule-Based)

**Engine I (Cold Start):** When a customer/product is brand new, the system uses explicit association rules:

> "Hardware X has historically been paired with Service Y in Z% of cases."
> → These are **countable, auditable statistics**, not black-box predictions.

**Engine II (Warm Start):** When historical data exists, it uses:
- **Popularity:** "In the US Enterprise segment, 68% of bids include this service."
- **Association:** "Customers who bought SR650 selected this warranty 82% of the time."

These are simple queries against historical data — business users can verify them independently.

### Stage 5 — Business Rules (Human-Defined)

After ML scoring, explicit rules override or filter results:

| Rule Type | Example |
|-----------|---------|
| Geo Restriction | "Service XYZ is not available in Brazil — remove from list." |
| EOL Filter | "Product ABC reached end-of-life — exclude related services." |
| Baseline Calibration | "Guarantee at least 3 options regardless of model confidence." |

These rules are **documented, version-controlled, and changeable** by business owners without retraining the model.

### Stage 5 — Add-On (Statistical, Not ML)

Add-on recommendations use co-occurrence mining:

> "Customers who selected Warranty A also selected Add-On B in 64% of historical bids."

This is a **simple frequency count**, not a model prediction. Business teams can review and approve the association rules.

---

## 3. Addressing Common Business Concerns

### "How do we know the model isn't biased toward expensive services?"

The **custom loss function** explicitly penalizes price-inappropriate recommendations:
- Over-recommending high-price services to small deals → penalty
- Under-recommending necessary coverage to large deals → penalty
- The β parameter (0.1–0.5) controls the price-vs-accuracy trade-off — this is a **tunable business dial**.

### "What if the model makes a bad recommendation?"

**Safety net #1:** Business rules catch obvious errors (EOL products, geo restrictions).

**Safety net #2:** GBB Branch logic — if model confidence is low (max_prob ≤ 0.75), the system falls back to price-sorted options instead of a strong recommendation.

**Safety net #3:** Auto-deployment gate — each new model version must **strictly outperform** the previous one on Accuracy + F1-Score before going live. If it fails, the old model stays.

### "Can we see why a specific bid got its recommendation?"

**Yes.** SHAP explanations can be generated per-prediction in real time and surfaced in the UI. A salesperson or business analyst can see, for any bid:

1. Which features most influenced the ranking
2. Why Service A was ranked higher than Service B
3. Which business rules were applied
4. How the Add-On probabilities were calculated

---

## 4. Summary: Transparency by Design

```
Black Box?  No.

┌──────────────┬─────────────────────────────────────┐
│ Stage        │ Explainability                      │
├──────────────┼─────────────────────────────────────┤
│ Recall       │ Rule-based, auditable statistics    │
│ Ranking      │ SHAP feature attribution per rec    │
│ Business     │ Human-defined, documented, mutable  │
│ Add-On       │ Frequency counts, reviewable        │
│ Deployment   │ Auto-gated, rollback-safe           │
└──────────────┴─────────────────────────────────────┘
```

The recommendation is not "the AI said so" — it is:
- **Historical evidence** (what worked for similar bids)
- **Business constraints** (geo, compliance, EOL)
- **Price optimization** (right service for the deal size)
- All **traceable** to specific factors per individual recommendation.

---

*Prepared for business stakeholder review. Technical details on SHAP implementation available upon request.*
