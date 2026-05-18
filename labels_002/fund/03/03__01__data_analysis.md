## Data sources and Trust Tier

| Tier | Class                             |
|------|-----------------------------------|
| 1    | Issuer-filed mandatory regulatory |
| 1    | Funder-published official         |
| 2    | Listed-platform                   |
| 3    | Company-issued first-party        |
| 4    | Trade press                       |
| 5    | Aggregators                       |

| Tier | Ref | Source                                                                                 |
|------|-----|----------------------------------------------------------------------------------------|
| 1    | 1A  | CH `/charges` API (MR01 + MR04 events)                                                 |
| 1    | 1B  | CH `/filing-history` API                                                               |
| 1    | 1C  | CH `/persons-with-significant-control` API                                             |
| 1    | 1D  | CH SH01 (return of allotment) — PDF + marker_md                                        |
| 1    | 1E  | CH SH02–SH08 (other allotment variants)                                                |
| 1    | 1F  | CH AA (annual accounts)                                                                |
| 1    | 1G  | CH CS01 (confirmation statement)                                                       |
| 1    | 1H  | CH AD01 (registered office change)                                                     |
| 1    | 1I  | CH AP01 (director appointment)                                                         |
| 1    | 1J  | CH TM01 (director termination)                                                         |
| 1    | 1K  | CH RES (resolutions, RES01–RES15)                                                      |
| 1    | 1L  | CH CERT (certificates, e.g. CERT15)                                                    |
| 1    | 1M  | RNS via Investegate (LSE Regulatory News Service)                                      |
| 1    | 1N  | SEC EDGAR Form D                                                                       |
| 1    | 1O  | SEC EDGAR 8-K                                                                          |
| 1    | 1P  | SEC EDGAR S-1 / 10-K                                                                   |
| 1    | 1Q  | The Gazette                                                                            |
| 1    | 1R  | UKRI Gateway to Research                                                               |
| 1    | 1S  | British Business Bank reports                                                          |
| 2    | 2A  | Crowdcube                                                                              |
| 2    | 2B  | Seedrs                                                                                 |
| 2    | 2C  | Republic / WeFunder                                                                    |
| 3    | 3A  | Company blog / press releases / portfolio pages                                        |
| 4    | 4A  | Trade press (TechCrunch, Sifted, Bdaily, Insider Media, Prolific North, City AM, etc.) |
| 5    | 5A  | Paid aggregators (Crunchbase, PitchBook, Beauhurst, Dealroom, …)                       |

## Company and Data Source Usage

| Company             | 1A | 1B | 1C | 1D | 1E | 1F | 1G | 1H | 1I | 1J | 1K | 1L | 1M | 1N | 1O | 1P | 1Q | 1R | 1S | 2A | 2B | 2C | 3A | 4A | 5A | Verdict            |
|---------------------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|--------------------|
| 00059535 Kodak      | 6  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 3  | 0  | No-rounds          |
| 00071835 Brandauer  | 4  | 0  | 0  | 10 | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 12 | 0  | 0  | 0  | 0  | 0  | 0  | 0  | T1-only            |
| 00076928 Chamberlin | 0  | 0  | 1  | 14 | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | T1-only            |
| 00086662 Chemring   | 2  | 0  | 0  | 9  | 0  | 5  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | T1-only            |
| 00156663 Helical    | 0  | 0  | 0  | 3  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 2  | 2  | 0  | T3-T4-load-bearing |
| 00166023 Invensys   | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 1  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 12 | 0  | T4-dominant        |
| 00484244 Camlab     | 1  | 1  | 1  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 2  | 2  | 0  | Mixed-light        |
| 00630968 LCG        | 2  | 0  | 0  | 57 | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | T1-only            |
| 00639690 Stange     | 6  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | T1-only            |
| 00781553 Kimpton    | 2  | 0  | 2  | 2  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 2  | 0  | Mixed-light        |

### Company and Data Source Usage Count

| Ref                                 | Total citations | Companies using |
|-------------------------------------|-----------------|-----------------|
| 1A CH `/charges`                    | 23              | 7               |
| 1B CH `/filing-history`             | 1               | 1 (Camlab)      |
| 1C CH PSC                           | 5               | 4               |
| 1D CH SH01                          | 97              | 8               |
| 1E CH SH02–SH08                     | 0               | 0               |
| 1F CH AA                            | 5               | 1 (Chemring)    |
| 1G CH CS01                          | 0               | 0               |
| 1H CH AD01                          | 0               | 0               |
| 1I CH AP01                          | 1               | 1 (Invensys)    |
| 1J CH TM01                          | 0               | 0               |
| 1K CH RES                           | 1               | 1 (Invensys)    |
| 1L CH CERT                          | 1               | 1 (Invensys)    |
| 1M RNS via Investegate              | 0               | 0               |
| 1N SEC EDGAR Form D                 | 0               | 0               |
| 1O SEC EDGAR 8-K                    | 0               | 0               |
| 1P SEC EDGAR S-1 / 10-K             | 0               | 0               |
| 1Q The Gazette                      | 0               | 0               |
| 1R UKRI Gateway                     | 12              | 1 (Brandauer)   |
| 1S British Business Bank            | 0               | 0               |
| 2A Crowdcube                        | 0               | 0               |
| 2B Seedrs                           | 0               | 0               |
| 2C Republic / WeFunder              | 0               | 0               |
| 3A Company blog / press / portfolio | 6               | 4               |
| 4A Trade press                      | 21              | 5               |
| 5A Paid aggregators                 | 0               | 0               |
