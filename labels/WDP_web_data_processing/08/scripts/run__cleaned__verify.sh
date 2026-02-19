#!/bin/bash
set -e
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${PROJECT_ROOT}"

echo "========================================="
echo "Verification of generated data"
echo "========================================="

source "${PROJECT_ROOT}/_common/shell_utils/common_util.sh"
common::load_config "${PROJECT_ROOT}/scripts_pipeline_steps/p001__rtic_company_summaries/run__cleaned__extraction__config.json"

CATEGORIES=("INDUSTRIES" "ACTIVITIES" "PRODUCTS" "MARKETS" "REGIONS" "MODEL" "IS_MANUFACTURING" "MANUFACTURING_PROCESSES" "TECHNICAL_CAPABILITIES" "COMPANY_SUMMARY" "COMPANY_TRADING_NAME")
run_all_verifications "${CATEGORIES[@]}"

exit_code=$?
echo ""
exit $exit_code