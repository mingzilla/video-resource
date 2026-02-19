#!/bin/bash
set -e
# ======================
# Common utilities for verifying generated summary data
# ======================

# Load configuration from JSON file
# Usage: common::load_config <config_file_path>
# This function handles all printing and exits on failure
function common::load_config() {
    local config_file="$1"

    echo "Config file: ${config_file}"
    echo ""

    if [[ ! -f "${config_file}" ]]; then
        echo "ERROR: Config file not found at ${config_file}" >&2
        exit 1
    fi

    # Export config values
    export OUTPUT_DB_PATH=$(jq -r '.output_db_path' "${config_file}")
    export OUTPUT_TABLE=$(jq -r '.output_table' "${config_file}")
    export OUTPUT_SUMMARY_COLUMN=$(jq -r '.output_summary_column' "${config_file}")

    echo "✓ Config loaded from: ${config_file}"
    echo "  Output DB: ${OUTPUT_DB_PATH}"
    echo "  Table: ${OUTPUT_TABLE}"
    echo "  Summary column: ${OUTPUT_SUMMARY_COLUMN}"
    return 0
}

# Check if output database exists
# Usage: common::check_output_exists
function common::check_output_exists() {
    if [[ ! -f "${OUTPUT_DB_PATH}" ]]; then
        echo "ERROR: Output database not found at ${OUTPUT_DB_PATH}" >&2
        echo "Please run the generation script first." >&2
        return 1
    fi
    echo "✓ Output database exists: ${OUTPUT_DB_PATH}"
    return 0
}

# Get clean numeric row count
# Usage: get_row_count
function get_row_count() {
    local count_query="SELECT COUNT(*) FROM ${OUTPUT_TABLE};"
    local raw_result
    raw_result=$(duckdb "${OUTPUT_DB_PATH}" -noheader -csv <<< "${count_query}" 2>/dev/null || echo "0")
    # Extract just the number (remove CSV formatting if any)
    echo "${raw_result}" | grep -E '^[0-9]+$' || echo "0"
}

function get_row_count_with_verification() {
    local total_rows
    total_rows=$(get_row_count)

    if [[ "${total_rows}" -eq "0" ]]; then
        echo "   Result: Table is empty (0 rows)" >&2
        return 1
    fi

    echo "   Total rows in table: ${total_rows}" >&2
    echo "${total_rows}"
}

# Verify structure/order of categories
# Usage: summaries::verify_structure <categories_array> [include_colon]
# include_colon: "true" to include ":" when checking (default), "false" to check without ":"
function summaries::verify_structure() {
    local args=("$@")
    local include_colon="true"
    local categories=()

    # Check if last parameter is "true" or "false" - if so, it's the include_colon flag
    if [[ "${args[-1]}" == "true" ]] || [[ "${args[-1]}" == "false" ]]; then
        include_colon="${args[-1]}"
        # All but the last parameter are categories
        categories=("${args[@]:0:${#args[@]}-1}")
    else
        # All parameters are categories
        categories=("${args[@]}")
    fi

    echo ""
    echo "1. STRUCTURE VERIFICATION:"
    echo "   Checking categories appear in correct order (optional categories are handled)"
    echo "   Categories: ${categories[*]}"
    echo "   Include colon in check: ${include_colon}"

    local total_rows=$(get_row_count_with_verification)

    local case_when_conditions=""
    for i in $(seq 0 $((${#categories[@]} - 2))); do
        local cat1="${categories[$i]}"
        local cat2="${categories[$i+1]}"

        # Add colon if include_colon is "true"
        if [[ "${include_colon}" == "true" ]]; then
            cat1="${cat1}:"
            cat2="${cat2}:"
        fi

        local condition="(INSTR(${OUTPUT_SUMMARY_COLUMN}, '${cat1}') = 0 OR INSTR(${OUTPUT_SUMMARY_COLUMN}, '${cat2}') = 0 OR INSTR(${OUTPUT_SUMMARY_COLUMN}, '${cat1}') < INSTR(${OUTPUT_SUMMARY_COLUMN}, '${cat2}'))"

        if [[ -z "${case_when_conditions}" ]]; then
            case_when_conditions="${condition}"
        else
            case_when_conditions="${case_when_conditions} AND ${condition}"
        fi
    done

    local query="SELECT
        SUM(CASE WHEN ${case_when_conditions} THEN 1 ELSE 0 END) as correct_structure_count
    FROM ${OUTPUT_TABLE};"

    echo "   (Checking order of categories if they appear in text)"

    local result
    result=$(duckdb "${OUTPUT_DB_PATH}" -noheader -csv <<< "${query}" 2>/dev/null || echo "0")
    result=$(echo "${result}" | grep -E '^[0-9]+$' || echo "0")

    if [[ "${total_rows}" -gt 0 ]]; then
        local percentage=$(echo "scale=2; ${result} * 100 / ${total_rows}" | bc)
        echo "   Result: ${result}/${total_rows} rows have correct structure (${percentage}%)"
    else
        echo "   Result: No rows found in table"
    fi

    # Return code: 0 if all rows have correct structure, 1 otherwise
    if [[ "${total_rows}" -gt 0 ]] && [[ "${result}" -eq "${total_rows}" ]]; then
        return 0
    else
        return 1
    fi
}

# Verify COMPANY_SUMMARY field exists
# Usage: summaries::verify_company_summary
function summaries::verify_company_summary() {
    echo ""
    echo "2. COMPANY_SUMMARY CHECK:"

    local total_rows=$(get_row_count_with_verification)

    local query="SELECT
        SUM(CASE WHEN ${OUTPUT_SUMMARY_COLUMN} LIKE '%COMPANY_SUMMARY:%' THEN 1 ELSE 0 END) as has_summary_count
    FROM ${OUTPUT_TABLE};"
    
    local result
    result=$(duckdb "${OUTPUT_DB_PATH}" -noheader -csv <<< "${query}" 2>/dev/null || echo "0")
    result=$(echo "${result}" | grep -E '^[0-9]+$' || echo "0")
    
    if [[ "${total_rows}" -gt 0 ]]; then
        local percentage=$(echo "scale=2; ${result} * 100 / ${total_rows}" | bc)
        echo "   Result: ${result}/${total_rows} rows have COMPANY_SUMMARY (${percentage}%)"
    else
        echo "   Result: No rows found in table"
    fi
    
    # Return code: 0 if all rows have COMPANY_SUMMARY, 1 otherwise
    if [[ "${total_rows}" -gt 0 ]] && [[ "${result}" -eq "${total_rows}" ]]; then
        return 0
    else
        return 1
    fi
}

# Verify COMPANY_TRADING_NAME field exists
# Usage: summaries::verify_company_trading_name
function summaries::verify_company_trading_name() {
    echo ""
    echo "3. COMPANY_TRADING_NAME CHECK:"

    local total_rows=$(get_row_count_with_verification)

    local query="SELECT
        SUM(CASE WHEN ${OUTPUT_SUMMARY_COLUMN} LIKE '%COMPANY_TRADING_NAME:%' THEN 1 ELSE 0 END) as has_trading_name_count
    FROM ${OUTPUT_TABLE};"

    local result
    result=$(duckdb "${OUTPUT_DB_PATH}" -noheader -csv <<< "${query}" 2>/dev/null || echo "0")
    result=$(echo "${result}" | grep -E '^[0-9]+$' || echo "0")

    if [[ "${total_rows}" -gt 0 ]]; then
        local percentage=$(echo "scale=2; ${result} * 100 / ${total_rows}" | bc)
        echo "   Result: ${result}/${total_rows} rows have COMPANY_TRADING_NAME (${percentage}%)"
    else
        echo "   Result: No rows found in table"
    fi

    # Return code: 0 if all rows have COMPANY_TRADING_NAME, 1 otherwise
    if [[ "${total_rows}" -gt 0 ]] && [[ "${result}" -eq "${total_rows}" ]]; then
        return 0
    else
        return 1
    fi
}

# Show record reusing statistics
# Usage: records::show_reusing_stats
function records::show_reusing_stats() {
    echo ""
    echo "4. RECORD REUSING STATISTICS:"

    local query="SELECT
        count(*) as total_records,
        count(*) FILTER (WHERE same_as_lowest_id IS NULL) as planned_records_to_create,
        count(*) FILTER (WHERE same_as_lowest_id IS NOT NULL) as planned_records_to_reuse,
        count(DISTINCT webtext_summary) as actual_distinct_summaries_generated,
        count(*) - count(DISTINCT webtext_summary) as actual_records_that_reused
    FROM companies c
    JOIN input_text_duplicate_mappings m ON c.CompanyNumber = m.input_id;"

    local result
    result=$(duckdb "${OUTPUT_DB_PATH}" -csv <<< "${query}" 2>/dev/null)

    if [[ -z "${result}" ]]; then
        echo "   ERROR: Failed to execute query" >&2
        return 1
    fi

    # Parse CSV result (header + data row)
    local header=$(echo "${result}" | head -n 1)
    local data=$(echo "${result}" | tail -n 1)

    # Split data into array
    IFS=',' read -r total_records planned_create planned_reuse actual_distinct actual_reused <<< "${data}"

    echo "   Total records: ${total_records}"
    echo "   Planned records to create: ${planned_create}"
    echo "   Planned records to reuse: ${planned_reuse}"
    echo "   Actual distinct summaries generated: ${actual_distinct}"
    echo "   Actual records that reused: ${actual_reused}"

    # Calculate and show percentages
    if [[ "${total_records}" -gt 0 ]]; then
        local planned_reuse_pct=$(echo "scale=2; ${planned_reuse} * 100 / ${total_records}" | bc)
        local actual_reuse_pct=$(echo "scale=2; ${actual_reused} * 100 / ${total_records}" | bc)
        echo ""
        echo "   Planned reuse rate: ${planned_reuse_pct}%"
        echo "   Actual reuse rate: ${actual_reuse_pct}%"
    fi

    return 0
}

# Create a new DuckDB file with extracted category columns
# Usage: duckdb::create_with_extracted_values <categories_array>
# Requires: OUTPUT_DB_PATH, OUTPUT_TABLE, OUTPUT_SUMMARY_COLUMN to be set
function duckdb::create_with_extracted_values() {
    local categories=("$@")

    echo ""
    echo "========================================="
    echo "Creating extracted database with category columns..."
    echo "========================================="

    if [ ${#categories[@]} -eq 0 ]; then
        echo "ERROR: No categories provided" >&2
        return 1
    fi

    # Build a comprehensive regex pattern to match any category boundary
    local all_categories_pattern=""
    for cat in "${categories[@]}"; do
        if [ -z "$all_categories_pattern" ]; then
            all_categories_pattern="${cat}:"
        else
            all_categories_pattern="${all_categories_pattern}|${cat}:"
        fi
    done

    # Build column extraction SQL for each category
    local columns=""
    for cat in "${categories[@]}"; do
        # Strategy:
        # 1. Use regexp_extract to capture text between "CATEGORY: " and the next category (or end)
        # 2. Pattern: CATEGORY:\s*(.*?)(?=NEXT_CATEGORY:|NEXT_CATEGORY2:|...|$)
        # But since DuckDB doesn't support lookahead, we'll use a different approach:
        # - Extract everything after "CATEGORY:" then use regexp_replace to remove from the next category onwards

        local extract_expr="
        CASE
            WHEN INSTR(${OUTPUT_SUMMARY_COLUMN}, '${cat}:') > 0 THEN
                TRIM(
                    REGEXP_REPLACE(
                        SUBSTRING(${OUTPUT_SUMMARY_COLUMN}, INSTR(${OUTPUT_SUMMARY_COLUMN}, '${cat}:') + LENGTH('${cat}:'))
                        , '(${all_categories_pattern})[\\s\\S]*', ''
                    )
                )
            ELSE NULL
        END"

        local cleaned_expr="CASE WHEN REGEXP_MATCHES(COALESCE(${extract_expr}, ''), '[a-zA-Z0-9]') THEN ${extract_expr} ELSE NULL END"
        columns="${columns}    ,${cleaned_expr} AS ${cat}
"
    done

    # Create new database path with __extracted suffix
    local base_name="${OUTPUT_DB_PATH%.duckdb}"
    local new_db_path="${base_name}__extracted.duckdb"

    # Remove existing file if it exists
    if [ -f "${new_db_path}" ]; then
        echo "Removing existing extracted database..."
        rm -f "${new_db_path}"
    fi

    echo "Source database: ${OUTPUT_DB_PATH}"
    echo "Target database: ${new_db_path}"
    echo "Table name: ${OUTPUT_TABLE}"
    echo "Extracting ${#categories[@]} categories: ${categories[*]}"
    echo ""

    # Build and execute SQL to create new database with extracted columns
    duckdb "${OUTPUT_DB_PATH}" << EOM
ATTACH '${new_db_path}' AS extracted_db;

CREATE TABLE extracted_db.${OUTPUT_TABLE} AS
SELECT
    *
${columns}FROM ${OUTPUT_TABLE};

DETACH extracted_db;
EOM

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo ""
        echo "✓ Successfully created extracted database"

        # Get row count from new database
        local row_count=$(duckdb "${new_db_path}" -noheader -csv <<< "SELECT COUNT(*) FROM ${OUTPUT_TABLE};" 2>/dev/null || echo "0")
        echo "  Rows extracted: ${row_count}"
        echo "  Location: ${new_db_path}"
        echo ""
        return 0
    else
        echo ""
        echo "✗ Failed to create extracted database" >&2
        return 1
    fi
}

# Run all verification checks
# Usage: run_all_verifications <categories_array>
function run_all_verifications() {
    local categories=("$@")
    local all_passed=true

    echo "========================================="
    echo "Running verification checks..."
    echo "========================================="

    # Check output exists
    if ! common::check_output_exists; then
        return 1
    fi

    # Run the three verification functions
    if ! summaries::verify_structure "${categories[@]}" "true"; then
        all_passed=false
    fi

    if ! summaries::verify_structure "${categories[@]}" "false"; then
        all_passed=false
    fi

    if ! summaries::verify_company_summary; then
        all_passed=false
    fi

    if ! summaries::verify_company_trading_name; then
        all_passed=false
    fi

    records::show_reusing_stats

    echo ""
    echo "========================================="
    if $all_passed; then
        echo "✓ All verification checks passed!"
    else
        echo "⚠ Some verification checks failed"
    fi
    echo "========================================="

    if $all_passed; then
        return 0
    else
        return 1
    fi
}