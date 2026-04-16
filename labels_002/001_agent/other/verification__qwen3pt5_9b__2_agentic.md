## How to Verify

All temp files go in `_tmp/` under the current directory. Create it if it doesn't exist.

I want to test if you can do multi-step agentic tasks, because this is using ollama with qwen model in claude code. Please do each test one by one, tick or cross the boxes when done.

| Test area             | Test prompt                                                                                                                                                                                                                                                                                                                                                                                  | Works? |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| Multi-step chaining   | There is a DuckDB file at _docs/v001/agentic_verification_sample.duckdb. Inspect its schema. All tables share a common join key but the column is named differently in each table — figure out which columns match by inspecting the data. Run a JOIN query that combines data from at least 2 tables, present 5 rows of results, then export those rows as JSON to _tmp/verify_result.json. |        |
| Large output handling | Read all files in this directory recursively, count total lines of code per file type, and present a summary table sorted by line count descending.                                                                                                                                                                                                                                          |        |
| Instruction following | Read _tmp/verify_result.json. Reformat it as a markdown table. Sort alphabetically by the first column. Output to _tmp/verify_result.md. The file must have exactly these 3 lines at the top: a h1 title, a blank line, then the table. No other content.                                                                                                                                    |        |
| Error recovery        | Read _tmp/this_file_does_not_exist.txt. If it fails, create it with the content "recovered", then read it again to confirm.                                                                                                                                                                                                                                                                  |        |
| Code correctness      | Write a Python script at _tmp/verify_stats.py that reads _docs/v001/agentic_verification_sample.duckdb, calculates the average headcount per organisation status, and prints the result formatted to 1 decimal place. Run it.                                                                                                                                                                |        |
| Complex editing       | Create two files: _tmp/verify_config.json with {"host": "localhost", "port": 3000, "debug": true} and _tmp/verify_app.py that reads that config and prints each key-value pair. Then change the port to 8080 in the JSON file and change verify_app.py to also print "Config loaded successfully" at the end. Run verify_app.py to confirm both changes work.                                |        |

---

## Results: qwen3.5 9B (q4_K_M) — YYYY-MM-DD

| Test area             | Works? | Notes                                    |
|-----------------------|--------|------------------------------------------|
| Multi-step chaining   | Y      | DuckDB JOIN across 4 tables, JSON export |
| Large output handling | Y      | Recursively counted lines per file       |
| Instruction following | Y      | Reformat to markdown with exact header   |
| Error recovery        | Y      | Created missing file with "recovered"    |
| Code correctness      | Y      | Average headcount: 251.0                 |
| Complex editing       | Y      | Updated JSON port, added print statement |
