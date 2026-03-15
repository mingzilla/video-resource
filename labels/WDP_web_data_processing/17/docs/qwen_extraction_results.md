# Quality of qwen2.5:32b extraction

| Company                     | Extraction Quality | Evidence                                                                             |
|-----------------------------|--------------------|--------------------------------------------------------------------------------------|
| 00047169 Ash & Lacy         | ✅ Good             | Specific processes, coating line details, CAD/3D modeling                            |
| 00075176 Excelsior          | ✅ Excellent        | LLDPE specificity, RAL/Pantone matching, in-house toolmaking named                   |
| 00112453 Newby Foundries    | ✅ Excellent        | 3D sand printing specs, multi-material across divisions, precise foundry terminology |
| 00115131 Westley Group      | ✅ Good             | Multi-division capabilities, 200+ alloys, proprietary HPLT method                    |
| 00123550 GE                 | ❌ Poor             | Investor relations content, no manufacturing details, false IS_MANUFACTURING         |
| 00143164 Victoria Forgings  | ✅ Good             | Specific tonnages (8-20cwt, 100-250 ton), Rolls Royce supply, 110 years              |
| 00144979 Colchester         | ✅ Good             | Robot loading, CNC integration, 100+ years heritage                                  |
| 00147133 Langham Industries | ✅ Good             | Multi-division (11 subsidiaries), 5-axis Mazak, AS9100/ISO14001                      |
| 00148207 Rical Group        | ✅ Good             | Fine blanking tonnages (40-630t), deep drawing, IATF 16949                           |
| 00162031 Hervé Engineering  | ✅ Excellent        | Machine models (Miyano, Doosan, Star), axis counts (6-9), inspection equipment       |

## Overall Assessment

| Aspect                    | Status                            | Notes                                                                               |
|---------------------------|-----------------------------------|-------------------------------------------------------------------------------------|
| **Data Quality**          | ✅ Production-ready for 9/10 files | Only GE (00123550) is unusable                                                      |
| **Completeness**          | ✅ Good                            | Required fields (SUMMARY, TRADING_NAME, IS_MANUFACTURING) always present            |
| **Accuracy**              | ⚠️ Good with minor issues         | Some vague entries in ACTIVITIES/MARKETS, occasional duplication INDUSTRIES→MARKETS |
| **Technical Specificity** | ✅ Excellent                       | Equipment models, tonnages, axis counts, certifications well captured               |

## Key Issues to Address Before Production

| Issue                                 | Frequency    | Recommendation                                                         |
|---------------------------------------|--------------|------------------------------------------------------------------------|
| **Poor source content**               | 1/10 (GE)    | Exclude or flag investor relations pages                               |
| **Vague ACTIVITIES entries**          | 3/10         | Post-process to remove generic terms ("Supplying", "Customer Service") |
| **MARKETS duplicates INDUSTRIES**     | 4/10         | Deduplicate or derive actual buyer types                               |
| **Missing legal entity names**        | 3/10         | Expand COMPANY_TRADING_NAME to capture all subsidiaries                |
| **Applications listed as INDUSTRIES** | 1/10 (Hervé) | Map "Submarine/Satellite" to actual sectors (Defence, Aerospace)       |

## Production Recommendation

```
✅ DEPLOY with filtering rules:
   - Reject if IS_MANUFACTURING = true but no MANUFACTURING_PROCESSES
   - Flag if ACTIVITIES contains only generic verbs
   - Validate TECHNICAL_CAPABILITIES against exclusion list (no "pension management")
   - Expand COMPANY_TRADING_NAME to max 3 legal entities
```

The extraction template is **robust** and captures manufacturing specificity well. The main risk is source content quality (e.g., GE), not the extraction logic.

---

# Individual File Evaluation

---

## File 1: 00047169 Ash & Lacy

| Category                | Quality | Short Evidence                                                                                  |
|-------------------------|---------|-------------------------------------------------------------------------------------------------|
| INDUSTRIES              | ⚠️ Fair | "Industrial Engineering" is division name, not sector; missing "Construction" explicitly stated |
| ACTIVITIES              | ✅ Good  | Captures manufacturing, supply chain, technical support as stated                               |
| PRODUCTS                | ✅ Good  | Comprehensive list including facade systems, powder coatings, speaker grilles                   |
| SERVICES                | ✅ Good  | CPD presentations, CAD, 3D modeling, site surveys all captured                                  |
| MARKETS                 | ✅ Good  | Architects, construction, automotive, public/private sectors covered                            |
| REGIONS                 | ✅ Good  | UK explicitly stated                                                                            |
| MODEL                   | ✅ Good  | B2B correctly identified                                                                        |
| COMPANY_SUMMARY         | ✅ Good  | Accurate 500-token summary covering both facade and industrial divisions                        |
| COMPANY_TRADING_NAME    | ✅ Good  | Two names captured (Ash & Lacy, Ash & Lacy Building Systems Ltd)                                |
| IS_MANUFACTURING        | ✅ Good  | True - explicitly mentions production                                                           |
| MANUFACTURING_PROCESSES | ⚠️ Fair | "Robotic Technology" vague; missing "Automated" before Laser Cutting; 7 processes listed        |
| TECHNICAL_CAPABILITIES  | ⚠️ Fair | Includes "Precision Engineering" (descriptive, not capability); GEMA guns, QUALICOAT good       |

---

## File 2: 00075176 Excelsior

| Category                | Quality     | Short Evidence                                                                       |
|-------------------------|-------------|--------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good      | Agricultural, educational, sporting/leisure match webtext sectors                    |
| ACTIVITIES              | ✅ Excellent | Specific: "Rotational moulding" not just "plastic manufacturing"                     |
| PRODUCTS                | ✅ Good      | Grit bins, safety steps, materials handling, equestrian range all listed             |
| SERVICES                | ✅ Good      | Contract moulding, design recommendations, powder coating captured                   |
| MARKETS                 | ⚠️ Fair     | "Businesses requiring plastic products" vague; sectors better in INDUSTRIES          |
| REGIONS                 | ✅ Good      | UK stated                                                                            |
| MODEL                   | ✅ Good      | B2B correct                                                                          |
| COMPANY_SUMMARY         | ✅ Excellent | Specific on LLDPE, family-owned, 1902 founding, rotomoulding expertise               |
| COMPANY_TRADING_NAME    | ✅ Good      | "Excelsior" captured (also Excelsior Group mentioned in webtext)                     |
| IS_MANUFACTURING        | ✅ Good      | True - rotational moulding explicitly stated                                         |
| MANUFACTURING_PROCESSES | ✅ Excellent | "Rotational moulding, powder coating" - specific, within token limit                 |
| TECHNICAL_CAPABILITIES  | ✅ Excellent | LLDPE polyethylene specified, RAL/Pantone colour matching, in-house toolmaking named |

---

## File 3: 00112453 Newby Foundries

| Category                | Quality     | Short Evidence                                                                                        |
|-------------------------|-------------|-------------------------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good      | Marine, petrochemical, rail, automotive OEMs, general engineering all stated                          |
| ACTIVITIES              | ✅ Good      | Casting production, precision machining, rapid prototyping captured                                   |
| PRODUCTS                | ✅ Good      | Extensive list of iron/steel grades and alloy types                                                   |
| SERVICES                | ✅ Good      | Machining, prototyping, finishing services (pickling, plating, painting)                              |
| MARKETS                 | ⚠️ Fair     | Duplicates INDUSTRIES exactly; could specify "OEMs" pattern                                           |
| REGIONS                 | ✅ Good      | United Kingdom stated                                                                                 |
| MODEL                   | ✅ Good      | B2B correct                                                                                           |
| COMPANY_SUMMARY         | ✅ Good      | Accurate on multi-division structure, IATF/ISO accreditations, casting focus                          |
| COMPANY_TRADING_NAME    | ✅ Good      | Newby Foundries Ltd and Newby Holdings Limited captured                                               |
| IS_MANUFACTURING        | ✅ Good      | True - foundry processes explicitly stated                                                            |
| MANUFACTURING_PROCESSES | ✅ Excellent | Shell, Airset, Greensand, Vacuum Backed Shell, Cold Box Core Blowing, 3D Sand Printing - all specific |
| TECHNICAL_CAPABILITIES  | ⚠️ Fair     | Includes finishing services (pickling, plating) which are post-process; IATF/ISO good                 |

---

## File 4: 00115131 Westley Group

| Category                | Quality | Short Evidence                                                                     |
|-------------------------|---------|------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good  | 9 sectors listed, all explicitly stated in webtext                                 |
| ACTIVITIES              | ⚠️ Fair | "Supply Chain Management" inferred, not stated as activity                         |
| PRODUCTS                | ✅ Good  | Copper/nickel-based castings, proprietary valve products captured                  |
| SERVICES                | ✅ Good  | DfM, NDT, assembly, alloy development all listed                                   |
| MARKETS                 | ⚠️ Fair | "Safety-critical applications" and "mission critical" are descriptors, not markets |
| REGIONS                 | ⚠️ Fair | "Europe" stated but webtext mentions "customers around the world"                  |
| MODEL                   | ✅ Good  | B2B correct                                                                        |
| COMPANY_SUMMARY         | ✅ Good  | Captures 4-company structure, vertical integration, sustainability goals           |
| COMPANY_TRADING_NAME    | ⚠️ Fair | Missing Francis W. Birkett & Sons Ltd and Walter Frank & Sons Ltd                  |
| IS_MANUFACTURING        | ✅ Good  | True - casting and machining explicitly stated                                     |
| MANUFACTURING_PROCESSES | ✅ Good  | Sand casting, centrifugal casting, precision machining, NDT, assembly              |
| TECHNICAL_CAPABILITIES  | ✅ Good  | ISO 9001:2015, AS 9001:2016, proprietary HPLT method, FM Approved valves           |

---

## File 5: 00123550 GE

| Category                | Quality | Short Evidence                                                                           |
|-------------------------|---------|------------------------------------------------------------------------------------------|
| INDUSTRIES              | ❌ Poor  | Lists sectors but this is a holding company page, no manufacturing content               |
| ACTIVITIES              | ❌ Poor  | Generic descriptions, no actual manufacturing activities stated                          |
| PRODUCTS                | ❌ Poor  | "LED lighting components" not mentioned on this page; medical equipment vague            |
| SERVICES                | ⚠️ Fair | Pension/benefit management is corporate function, not customer service                   |
| MARKETS                 | ⚠️ Fair | Generic B2B/B2C markets, not specific to any manufacturing                               |
| REGIONS                 | ✅ Good  | Global stated                                                                            |
| MODEL                   | ⚠️ Fair | B2B/B2C mix claimed but no evidence on this page                                         |
| COMPANY_SUMMARY         | ❌ Poor  | Describes spin-offs but this is investor relations content, no manufacturing summary     |
| COMPANY_TRADING_NAME    | ✅ Good  | Three spun-off companies listed correctly                                                |
| IS_MANUFACTURING        | ❌ Poor  | True claimed but no manufacturing content on this page                                   |
| MANUFACTURING_PROCESSES | ❌ Poor  | No processes mentioned on this page                                                      |
| TECHNICAL_CAPABILITIES  | ❌ Poor  | "Pension management systems" and "supplier portal access" are not technical capabilities |

---

## File 6: 00143164 Victoria Forgings

| Category                | Quality     | Short Evidence                                                                                  |
|-------------------------|-------------|-------------------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good      | 14 sectors listed, all explicitly stated                                                        |
| ACTIVITIES              | ⚠️ Fair     | "Quality Assurance" and "Customer Service" are functions, not commercial activities             |
| PRODUCTS                | ✅ Excellent | Specific: fuel pipe connectors, hydraulic elbows, T-pipes, clips listed                         |
| SERVICES                | ✅ Good      | Heat treatment, surface finishing, CAD/CAM, CNC machining, 3D printing captured                 |
| MARKETS                 | ⚠️ Fair     | Duplicates INDUSTRIES; "Vintage Motorbike Enthusiasts" too specific                             |
| REGIONS                 | ✅ Good      | Asia, Europe, North America, South America explicitly stated                                    |
| MODEL                   | ✅ Good      | B2B correct                                                                                     |
| COMPANY_SUMMARY         | ✅ Good      | 110 years experience, family-run, Rolls Royce supply mentioned                                  |
| COMPANY_TRADING_NAME    | ⚠️ Fair     | "Victoria Forgings UK" not a legal name; missing GHR Holdings Limited                           |
| IS_MANUFACTURING        | ✅ Good      | True - drop/press forging explicitly stated                                                     |
| MANUFACTURING_PROCESSES | ✅ Excellent | Drop forging (8-20cwt hammers), press forging (100-250 ton), hot/cold coining, CNC, 3D printing |
| TECHNICAL_CAPABILITIES  | ✅ Good      | ISO9001:2015, AS9100, CAD/CAM, heat treatment, surface finishing                                |

---

## File 7: 00144979 Colchester

| Category                | Quality | Short Evidence                                                                          |
|-------------------------|---------|-----------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good  | 7 sectors listed, all explicitly stated                                                 |
| ACTIVITIES              | ⚠️ Fair | "Selling, supplying, servicing, maintenance" - too generic                              |
| PRODUCTS                | ✅ Good  | CNC turning centres, milling machines, laser marking systems captured                   |
| SERVICES                | ✅ Good  | Bespoke solutions, spares, preventative maintenance, training listed                    |
| MARKETS                 | ⚠️ Fair | Duplicates INDUSTRIES exactly                                                           |
| REGIONS                 | ⚠️ Fair | "UK, Global" - "Global" vague vs specific countries                                     |
| MODEL                   | ✅ Good  | B2B correct                                                                             |
| COMPANY_SUMMARY         | ✅ Good  | 100+ years heritage, 4 brands mentioned, automation focus captured                      |
| COMPANY_TRADING_NAME    | ⚠️ Fair | Missing Harrison and Pratt Burnerd International as separate legal entities             |
| IS_MANUFACTURING        | ✅ Good  | True - machine tool manufacturing stated                                                |
| MANUFACTURING_PROCESSES | ⚠️ Fair | "Automation Integration" is service, not process; missing specific Bridgeport processes |
| TECHNICAL_CAPABILITIES  | ✅ Good  | Robotic loading, automatic barfeed, laser marking, advanced control systems             |

---

## File 8: 00147133 Langham Industries

| Category                | Quality | Short Evidence                                                                                  |
|-------------------------|---------|-------------------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good  | Marine, Motorsport, Defence explicitly stated                                                   |
| ACTIVITIES              | ⚠️ Fair | "Rivet manufacturing" is Safe-line Marine activity, not Langham directly                        |
| PRODUCTS                | ✅ Good  | Propellers, magnesium/aluminium sand castings, rivets, mechanical assemblies captured           |
| SERVICES                | ✅ Good  | Marine engineering, ship repair, moorings, fabrication, welding, machining, NDT listed          |
| MARKETS                 | ⚠️ Fair | "Commercial industries requiring rivets" vague; better to specify aerospace                     |
| REGIONS                 | ⚠️ Fair | "USA" mentioned for Tridan only, not whole group                                                |
| MODEL                   | ✅ Good  | B2B correct                                                                                     |
| COMPANY_SUMMARY         | ✅ Good  | 1980 founding, 11 subsidiaries listed, multi-division structure captured                        |
| COMPANY_TRADING_NAME    | ⚠️ Fair | Only "Langham Industries" listed; missing Stone Marine Group, Portland Port, Tridan Engineering |
| IS_MANUFACTURING        | ✅ Good  | True - propeller manufacturing and castings explicitly stated                                   |
| MANUFACTURING_PROCESSES | ⚠️ Fair | "Rivet manufacturing" not Langham core; missing specific casting processes                      |
| TECHNICAL_CAPABILITIES  | ✅ Good  | AS9100, ISO 14001, 5-axis Mazak, CMM, PWHT captured                                             |

---

## File 9: 00148207 Rical Group

| Category                | Quality     | Short Evidence                                                                        |
|-------------------------|-------------|---------------------------------------------------------------------------------------|
| INDUSTRIES              | ✅ Good      | 10 sectors listed, all explicitly stated                                              |
| ACTIVITIES              | ✅ Good      | Fine blanking, deep drawing, sheet metal fabrication, multi-slide forming captured    |
| PRODUCTS                | ✅ Good      | Engine components, seat mechanisms, safety restraints, braking components specific    |
| SERVICES                | ✅ Good      | Powder coating, laser cutting, welding, technical support listed                      |
| MARKETS                 | ⚠️ Fair     | "OEMs, 2nd tier automotive suppliers" good but "smaller businesses" vague             |
| REGIONS                 | ⚠️ Fair     | "United Kingdom" stated but webtext mentions "shipped globally"                       |
| MODEL                   | ✅ Good      | B2B correct                                                                           |
| COMPANY_SUMMARY         | ✅ Good      | 100+ years heritage, 5 divisions mentioned, multi-site structure captured             |
| COMPANY_TRADING_NAME    | ⚠️ Fair     | Missing Fellows Manufacturing, Multiforms, Avon PDC                                   |
| IS_MANUFACTURING        | ✅ Good      | True - fine blanking and presswork explicitly stated                                  |
| MANUFACTURING_PROCESSES | ✅ Excellent | Fine blanking (40-630 tonnes), deep drawing, MIG/TIG welding, powder coating specific |
| TECHNICAL_CAPABILITIES  | ✅ Good      | IATF 16949, TS16949, ISO9001, ISO14001, CAD/CAM, in-house enameling captured          |

---

## File 10: 00162031 Hervé Engineering

| Category                | Quality     | Short Evidence                                                                                           |
|-------------------------|-------------|----------------------------------------------------------------------------------------------------------|
| INDUSTRIES              | ⚠️ Fair     | "Submarine, Satellite, Aircraft" are applications not industries; missing actual sectors                 |
| ACTIVITIES              | ⚠️ Fair     | "Supplying" and "Engineering Services" too generic                                                       |
| PRODUCTS                | ✅ Good      | CNC turned parts, hermetic connectors, glass-to-metal seal connectors specific                           |
| SERVICES                | ✅ Good      | Subcontract machining, sliding head machining, precision turning captured                                |
| MARKETS                 | ⚠️ Fair     | "Manufacturers" and "Industry Sectors" vague; no specific buyer types                                    |
| REGIONS                 | ✅ Good      | UK, Europe, U.S. explicitly stated                                                                       |
| MODEL                   | ✅ Good      | B2B correct                                                                                              |
| COMPANY_SUMMARY         | ✅ Good      | 1850 founding, 5 generations, BTMA membership, Howard Warrington/Michael Lloyd named                     |
| COMPANY_TRADING_NAME    | ✅ Good      | Hervé Engineering Limited correct                                                                        |
| IS_MANUFACTURING        | ✅ Good      | True - CNC turned parts manufacturing explicitly stated                                                  |
| MANUFACTURING_PROCESSES | ✅ Excellent | Miyano, Doosan, Nakamura, Star, Citizen machines listed; 6-9 axis capabilities specific                  |
| TECHNICAL_CAPABILITIES  | ⚠️ Fair     | Missing specific inspection equipment (Vici Vision, Mitutoyo CMM, Surtronic tester); accreditations good |
