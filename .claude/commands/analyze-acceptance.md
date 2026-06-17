# Acceptance & Coverage Analysis

Run the standard Service Smart Recommendation acceptance and coverage analysis on a CSV file.

**Usage:** `/analyze-acceptance <csv_filename>`

## Instructions

The argument is: $ARGUMENTS

1. Change directory to `C:\Users\Administrator\ClaudeProjects\ServiceSmartRecommendationAnalysis`
2. Run the analysis script using Bash:
   ```
   cd /c/Users/Administrator/ClaudeProjects/ServiceSmartRecommendationAnalysis && python analysis_acceptance.py "$ARGUMENTS"
   ```
3. Read and display the output file that was written to `validation_output/`.
4. Summarise the key figures: AI coverage rate, service attachment rate (AI vs non-AI), lift, and default acceptance rate — at both config level and contract level, for EMEA and Global.

## Analysis method (for reference)

- **AI recommended** = `defaultfrom == 'AI'`
- **Service selected** = `selectedfrom` is not empty
- **AI default kept** = `selectedfrom` contains `'Default'` but not `'Non-Default'`
- **Config level** = each row is one observation
- **Contract level** = each unique `contract_number` is one observation; contract is flagged AI if ANY line item had an AI recommendation
- **Lift** = AI attachment rate minus non-AI attachment rate (percentage points)
- Output is saved to `validation_output/acceptance_<filename>.txt`
