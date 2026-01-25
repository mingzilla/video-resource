#!/bin/bash
set -e

# --- Project Root Setup (as per user request) ---
# This script is located at: work/llm_text_summary/scripts_sh/ex_003_data_analysis/show_data_distribution.sh
# To reach the desired project root (work/llm_text_summary), we need to go up 2 directories.
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${PROJECT_ROOT}"

# --- Configuration (Hardcoded as per user request) ---
# Path relative to the new PROJECT_ROOT (work/llm_text_summary)
INPUT_FILE="../_app_data_output/cleaned_web_text.parquet"
TABLE_NAME="" # If this is a DuckDB file, this should be set to the table name, otherwise leave empty.
WEBTEXT_COLUMN_NAME="webtext_cleaned" # The column containing the text to analyze

# --- Internal Variables ---
# Resolve INPUT_FILE to an absolute path from PROJECT_ROOT
ABSOLUTE_INPUT_FILE="${PROJECT_ROOT}/${INPUT_FILE}"
FILE_EXT="${ABSOLUTE_INPUT_FILE##*.}" # Extract file extension
DB_FILE_ARG=""
SQL_SOURCE=""

# --- Determine SQL Source based on file type and hardcoded variables ---
if [ "$FILE_EXT" = "duckdb" ]; then
    if [ -z "$TABLE_NAME" ]; then
        echo "Error: TABLE_NAME must be set in the script for .duckdb files." >&2
        exit 1
    fi
    DB_FILE_ARG="${ABSOLUTE_INPUT_FILE}"
    SQL_SOURCE="${TABLE_NAME}"
    echo "Analyzing DuckDB file: ${ABSOLUTE_INPUT_FILE}, Table: ${SQL_SOURCE}"

elif [ "$FILE_EXT" = "parquet" ]; then
    # DuckDB will use an in-memory database
    SQL_SOURCE="read_parquet('${ABSOLUTE_INPUT_FILE}')"
    echo "Analyzing Parquet file: ${ABSOLUTE_INPUT_FILE}"

else
    echo "Error: Unsupported file type '${FILE_EXT}' derived from INPUT_FILE. Please ensure INPUT_FILE points to a .duckdb or .parquet file." >&2
    exit 1
fi

# --- SQL Query Definition ---
# The query is now defined directly in the execution block below.

# --- Execution ---
echo ""
echo "--- Text Length Distribution Report (Column: ${WEBTEXT_COLUMN_NAME}) ---"
echo ""
# Pipe the SQL query directly into DuckDB's standard input.
# This is more robust for complex, multi-line queries than using -c with a variable.
duckdb ${DB_FILE_ARG:+"$DB_FILE_ARG"} << EOM
WITH lengths AS (
    -- This is the single, efficient pass over your data source.
    SELECT LENGTH(${WEBTEXT_COLUMN_NAME}) AS len FROM ${SQL_SOURCE} WHERE ${WEBTEXT_COLUMN_NAME} IS NOT NULL
),
deciles AS (
    -- This calculates all the stats we need from the list of lengths.
    SELECT
        -- APPROX_QUANTILE finds the length value at the 10th, 20th, etc., percentile.
        APPROX_QUANTILE(len, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]) AS threshold_lengths,
        MAX(len) AS max_len
    FROM lengths
)
-- UNNEST turns the array of thresholds into rows.
-- WITH ORDINALITY gives us a row number (1, 2, 3...) which we use to calculate the percentage.
SELECT
    threshold AS text_length,
    (threshold * 100.0 / max_len)::DECIMAL(5, 2) AS "%_vs_max_length",
    (ordinality * 10) AS "%_records_below_length"
FROM
    deciles,
    UNNEST(threshold_lengths) WITH ORDINALITY AS t(threshold, ordinality);
EOM

echo ""
echo "Columns:"
echo "- text_length - characters of the text field to check"
echo "- %_vs_max_length - text_length / max_length_value_length * 100"
echo "- %_records_below_length - % of records shorter than this length"
echo ""
