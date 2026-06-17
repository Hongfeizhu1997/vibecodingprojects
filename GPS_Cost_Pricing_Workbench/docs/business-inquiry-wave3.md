Subject: GPS Pricing Workbench — Input Needed for Stage 4 & 5 Enhancements

Hi team,

We've completed two rounds of improvements to the GPS Cost Pricing Workbench based on your feedback (Summary of Observations v2). Before we proceed with the next set, we need your input on three items where the business logic needs to be defined first.

---

1. GTN / Backend Rebate in Stage 5 (List Price Derivation)

Currently, GP Floor is calculated as:
    GP% = (Channel Price − Sales Cost) / Channel Price

You noted that GP Floor reflects net bookings and should account for GTN / backend rebate.

To implement this, we need to confirm:
  a) What is the source of GTN data? (System? Spreadsheet?)
  b) At what granularity does GTN apply — per PN, per GEO, per Tier, or as a flat %?
  c) Where in the calculation chain should GTN be applied — before or after list price derivation? After channel price but before GP%?
  d) Is GTN a fixed value per cycle or does it vary by product family / term / delivery type?

---

2. AI PC vs. Non-AI PC Rule in Stage 4 (GVE / Cross-Check)

You asked whether we can add a rule dimension for AI PC vs. Non-AI PC components. This is not tier-linked and likely scope-based.

To proceed, we need to clarify:
  a) How is "AI PC" identified in the data? (SDF code? A specific field? Attribute flag?)
  b) Who maintains this classification and how often does it change?
  c) Should this be a standalone rule factor, or should it be embedded within existing tier/scope rules?

---

3. FX / Inflation Impact & Multi-Currency Export in Stage 5

You highlighted that some Geos (e.g. LA) need forward-looking FX rates or inflation adjustments for longer-term pricing, and asked whether the tool can handle local currency exports.

To scope this:
  a) Where do the quarterly FX rates come from? (Internal finance feed? Manual upload?)
  b) Which Geos require this — all, or a specific subset?
  c) Should the tool store FX rates per cycle and auto-convert, or export everything in USD and let teams convert externally?
  d) Does inflation adjustment follow a Geo-specific index, or a standard rate?

---

We're ready to build all three once these points are clarified. A brief reply with your answers — even rough notes — is enough to get us started.

Thanks,
Hongfei
