## Proposal of Implementation

```text
[data universe]
  |                   | 1A | 1B | 1C | 1D | 1E | 1F | 1G | 1H | 1I | 1J | 1K | .. |
[harvest API]         |    |    |    |    |    |    |    |    |    |    |    |    |
  |                   |                                                           |
[harvest data]        |    |    |    |    |    |    |    |    |    |    |    |    |
  |                   |                                                           |
[convert data]        |    |    |    |    |    |    |    |    |    |    |    |    |
  |
[lite processing]
  |
[LLM request]
  |
[final verification]

- Is it important?
- Have we done it?
```

## Proposal of Implementation

| Ref | Source                           | harvesting API — implemented? | harvesting data — implemented? | data format — identified? | extract data — implemented? |
|-----|----------------------------------|-------------------------------|--------------------------------|---------------------------|-----------------------------|
| 1A  | CH `/charges`                    | `(*2a)`                       | NA                             | json                      | NA                          |
| 1B  | CH `/filing-history`             | `(*2a)`                       | NA                             | json                      | NA                          |
| 1C  | CH PSC                           | `(*2a)`                       | NA                             | json                      | NA                          |
| 1D  | CH SH01                          | `(*2a)`                       | `(*4a)`                        | pdf                       | `(*4b)`+`(*4c)`             |
| 1E  | CH SH02–SH08                     | 0                             | 0                              | 0                         | 0                           |
| 1F  | CH AA                            | TODO                          | TODO                           | pdf                       | TODO                        |
| 1G  | CH CS01                          | 0                             | 0                              | 0                         | 0                           |
| 1H  | CH AD01                          | 0                             | 0                              | 0                         | 0                           |
| 1I  | CH AP01                          | TODO                          | TODO                           | pdf                       | TODO                        |
| 1J  | CH TM01                          | 0                             | 0                              | 0                         | 0                           |
| 1K  | CH RES                           | TODO                          | TODO                           | pdf                       | TODO                        |
| 1L  | CH CERT                          | TODO                          | TODO                           | pdf                       | TODO                        |
| 1M  | RNS via Investegate              | `(*4_5a)`                     | `(*4_5b)`                      | html                      | `(*4_5c)`                   |
| 1N  | SEC EDGAR Form D                 | 0                             | 0                              | 0                         | 0                           |
| 1O  | SEC EDGAR 8-K                    | 0                             | 0                              | 0                         | 0                           |
| 1P  | SEC EDGAR S-1 / 10-K             | 0                             | 0                              | 0                         | 0                           |
| 1Q  | The Gazette                      | 0                             | 0                              | 0                         | 0                           |
| 1R  | UKRI Gateway                     | `(*3a)`                       | NA                             | json                      | NA                          |
| 1S  | British Business Bank            | 0                             | 0                              | 0                         | 0                           |
| 2A  | Crowdcube                        | 0                             | 0                              | 0                         | 0                           |
| 2B  | Seedrs                           | 0                             | 0                              | 0                         | 0                           |
| 2C  | Republic / WeFunder              | 0                             | 0                              | 0                         | 0                           |
| 3A  | Company blog / press / portfolio | TODO                          | TODO                           | html                      | TODO                        |
| 4A  | Trade press                      | TODO                          | TODO                           | html                      | TODO                        |
| 5A  | Paid aggregators                 | 0                             | 0                              | 0                         | 0                           |

### Notes on the `TODO` rows for review

| Ref                          | Cohort citations  | What's at stake if you mark `0` instead of TODO                                                                                                                                         |
|------------------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1F CH AA                     | 5 (Chemring only) | Lose Chemring's $280M USPP narrative — AA Notes 3/4/9 are where it surfaces; without AA we miss Chemring USPP coverage                                                                  |
| 1I CH AP01                   | 1 (Invensys)      | Lose AP01-cluster signal for scheme-detection — Invensys £3.4bn ACQ stays harder to reach                                                                                               |
| 1K CH RES                    | 1 (Invensys)      | Lose resolution-text signal — supports Invensys scheme context                                                                                                                          |
| 1L CH CERT                   | 1 (Invensys)      | Lose CERT15 (effective-date signal) — supports Invensys scheme effective date                                                                                                           |
| 3A Company press / portfolio | 6 (4 cos)         | Lose company-issued context across Kodak, Helical, Camlab, Kimpton (all already `No-rounds` / `T3-T4-load-bearing` / `Mixed-light` — none are at H quality even with T1)                |
| 4A Trade press               | 21 (5 cos)        | Lose Invensys (12 of 16 round refs come from T4), Helical cashbox investor context, Camlab "Calibre Scientific" brand, Kodak operational-banking noise reasoning, Kimpton MBO editorial |
