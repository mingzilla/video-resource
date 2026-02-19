## Context for Company Sampling Task - Used to select companies to verify

I have a DuckDB database work/__pipelines/2026_01__p002__rtic_company_capabilities/_output/match__step_01__company_capability_to_embed.duckdb with ~500 companies (table name companies). Each company has extracted fields including `MANUFACTURING_PROCESSES` and `TECHNICAL_CAPABILITIES` (summarized from webtext).

I also have a **customer-defined capability taxonomy** (CSV) with these top-level categories:

- **Joining** (Welding, Brazing, Soldering, etc.)
- **Casting** (Die casting, Investment casting, Sand casting, etc.)
- **Forming** (Forging, Rolling, Extrusion, Pressing, etc.)
- **Machining** (Milling, Turning, Drilling, Grinding, etc.)
- **Moulding** (Injection molding, Blow molding, Compression molding, etc.)
- **Additive Manufacturing** (3D printing, Powder bed fusion, etc.)
- **Composites** (Filament winding, Prepreg, Pultrusion, etc.)
- **Automation** (Robotics, Process control, Sensors, etc.)
- **Design** (CAD, Simulation, Prototyping, etc.)
- **Digital** (IoT, Data analytics, AI/ML, etc.)
- **Measurement/Testing** (Inspection, Metrology, NDT, etc.)
- **Biotech** (Fermentation, Downstream processing, etc.)

## Task

Select **10 company numbers** from my database that are **most likely to match these taxonomy domains**. Use the `webtext_summary` categorical labels to filter for companies in relevant industries.

**Prioritize companies whose extracted capabilities suggest**:

- Metal fabrication, machining, or forming
- Welding or joining processes
- Plastic molding or casting
- Industrial automation or robotics
- Composite manufacturing

**Avoid** (for this test):

- Construction materials (cement, asphalt)
- Paper/packaging
- Agriculture/animal feed
- Consumer electronics
- Chemicals without manufacturing processes

Return the company numbers and brief justification for each selection.

---

## Selected Companies

work/__pipelines/2026_01__p002__rtic_company_capabilities/_output__md__extract_and_vss__pipeline.sh 00143164 00112453 00047169 00144979 00123550

| CompanyNumber | Short Justification                                                                                                                                                                                                                                                                |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00143164      | **Victoria Drop Forgings** - Comprehensive forging operations (drop hammers 8-20cwt, forging presses 100-250 ton), hot/cold coining, in-house CNC die production, 3D printing, heat treatment. Covers Forming/Forging taxonomy extensively. Serves aerospace, automotive, defense. |
| 00112453      | **Newby Foundries** - Specialized casting processes (airset, shell moulding, vacuum-backed shell moulding), produces iron/steel castings 1kg-750kg. Perfect match for Casting taxonomy. IATF 16949:2016 certified with 3D sand printing capability.                                |
| 00047169      | **Ash & Lacy** - Metal fabrication combining laser cutting, CNC machining, welding, and advanced powder coating (5-stage pre-treatment). Strong match for Joining/Welding and Machining categories. Serves automotive and facade industries.                                       |
| 00144979      | **Colchester Machine Tool Solutions** - Automation specialist with robotic loading systems, CNC technology, automatic barfeed integration. Excellent for Automation/Robotics and Machining taxonomy. Serves aerospace, automotive, medical, defense.                               |
| 00123550      | **GE Aerospace** - Advanced manufacturing including additive manufacturing, 3D printing, precision machining, composites, ceramics. Covers Additive Manufacturing, Composites, and advanced Machining. Multi-industry leader (aerospace, energy, healthcare).                      |

Selected Companies:

1. 00143164 - Victoria Drop Forgings
    - Forming/Forging specialist with drop hammers (8-20cwt), forging presses (100-250 ton)
    - In-house CNC die production, 3D printing, heat treatment
    - AS9100 certified, serves aerospace/automotive/defense
2. 00112453 - Newby Foundries
    - Casting expert (airset, shell moulding, vacuum-backed shell moulding)
    - Produces iron/steel castings from 1kg to 750kg
    - IATF 16949:2016 certified with 3D sand printing capability
3. 00047169 - Ash & Lacy
    - Joining/Welding & Machining - laser cutting, CNC machining, welding, fabrication
    - Advanced powder coating with 5-stage pre-treatment
    - Serves automotive and facade/construction industries
4. 00144979 - Colchester Machine Tool Solutions
    - Automation/Robotics specialist with robotic loading systems
    - CNC technology with integrated robot systems for seamless automation
    - Serves aerospace, automotive, medical, defense sectors
5. 00123550 - GE Aerospace
    - Additive Manufacturing & Composites leader
    - Advanced 3D printing, precision machining, composites, ceramics
    - Multi-sector capabilities (aerospace, energy, healthcare)

These companies cover: Joining, Casting, Forming, Machining, Additive Manufacturing, Automation, and Composites from your taxonomy, while avoiding construction materials, paper, agriculture, and consumer electronics

### Kimi's verification:

| Company                              | CSV Category Match                                                                    | Quality   |
|--------------------------------------|---------------------------------------------------------------------------------------|-----------|
| **00143164** Victoria Drop Forgings  | **Forming > Forging** (drop hammers, forging presses)                                 | ⭐ Perfect |
| **00112453** Newby Foundries         | **Casting** (airset, shell moulding, vacuum-backed) + **Additive** (3D sand printing) | ⭐ Perfect |
| **00047169** Ash & Lacy              | **Joining/Welding** + **Machining** (laser cutting, CNC, welding)                     | ⭐ Perfect |
| **00144979** Colchester Machine Tool | **Automation > Robotics** + **Machining** (CNC + robot integration)                   | ⭐ Perfect |
| **00123550** GE Aerospace            | **Additive Manufacturing** + **Composites** + **Machining**                           | ⭐ Perfect |

## Second Set of 5 Companies:

work/__pipelines/2026_01__p002__rtic_company_capabilities/_output__md__extract_and_vss__pipeline.sh 00148207 00162031 00115131 00147133 00075176

| CompanyNumber | Short Justification                                                                                                                                                                                                                                                         |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00148207      | **William Mitchell** - Fine blanking & deep drawing specialist. High-volume precision forming combining cold extrusion and stamping. IATF 16949 certified. MIG/TIG welding, Trumpf punch machines, powder coating. Serves automotive, aerospace, medical, white goods.      |
| 00162031      | **Hervé Engineering** - Precision CNC turning with multi-axis machining, sub-spindle, twin turret capabilities. Advanced measurement with optical measuring, programmable CMM, premium height gauge. Serves aerospace, automotive, medical devices, satellites, submarines. |
| 00115131      | **Westley Group** - Sand casting (non-ferrous) and centrifugal casting (ferrous/non-ferrous) for tubes and rings. Vertically integrated with metallurgy, DfM, machining, assembly, critical NDT. ABS, Lloyds, DNV approved. AS 9001:2016 certified.                         |
| 00147133      | **Stone Marine Group** - Precision fabrication, welding, machining, mechanical assemblies, non-destructive testing (NDT). Specialized in marine propeller work (hot straightening, blade reshaping, re-tipping, polishing). CNC CMM for quality control.                    |
| 00075176      | **Excelsior** - Roto-moulding specialist for thermoplastic products. Rotational molding process creates hollow plastic parts for materials handling and industrial applications. Covers Moulding taxonomy for plastics manufacturing.                                       |

Second Set of 5 Companies:

1. 00148207 - William Mitchell (Fellows Manufacturing, Multiforms, Taurus Engineering)
    - Fine blanking & deep drawing specialist (Forming)
    - High-volume precision process combining cold extrusion and stamping
    - IATF 16949 certified, MIG/TIG welding, Trumpf punch machines
    - Serves automotive, aerospace, medical, white goods
2. 00162031 - Hervé Engineering
    - Precision CNC turning with multi-axis machining (Machining)
    - Sub-spindle, twin turret, power tooling capabilities
    - Advanced Measurement with optical measuring, programmable CMM
    - Serves aerospace, automotive, medical devices, satellites, submarines
3. 00115131 - Westley Group (Meighs & Westleys, Spunalloys)
    - Sand casting & centrifugal casting specialist (Casting)
    - Vertically integrated with metallurgy, DfM, machining, assembly, critical NDT
    - ABS, Lloyds, DNV approved; AS 9001:2016 certified
    - Serves aerospace, oil & gas, naval defense, power generation
4. 00147133 - Stone Marine Group (Tridan Engineering)
    - Welding, machining, mechanical assemblies, NDT (Joining & Measurement/Testing)
    - Specialized marine propeller work: hot straightening, blade reshaping, re-tipping
    - CNC CMM for quality control
    - Serves marine, motorsport, defense
5. 00075176 - Excelsior (Crossfield Excalibur)
    - Roto-moulding specialist for thermoplastics (Moulding)
    - Rotational molding creates hollow plastic parts
    - Serves plastics manufacturing, materials handling, industrial products

New taxonomy coverage: Fine blanking, Deep drawing, Precision turning/grinding, Centrifugal casting, NDT/Inspection, Roto-moulding, and additional Welding/Fabrication capabilities.

### Kimi's verification

| Company                         | Tier1 Coverage                                                   | Leaf Node Matches                                                                                                                                                                                                                                                   | Quality   |
|---------------------------------|------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| **00148207** William Mitchell   | **Forming** (primary), **Joining**                               | Fine blanking & deep drawing → `Forming > Pressing > Drawing` or `Forming > Pressing > Blanking`; Cold extrusion → `Forming > Forging > Impact extrusion` or `Forming > Extrusion`; MIG/TIG welding → `Joining > Welding > [Arc]`                                   | ⭐ Perfect |
| **00162031** Hervé Engineering  | **Machining** (primary), **Measurement OR Testing**              | Multi-axis CNC turning → `Machining > Turning > Multi-axis Turning`; Sub-spindle/twin turret → specific lathe operations; Optical measuring/CMM → `Measurement OR Testing > Metrology` or `Measurement OR Testing > Contact and non-contact coordinate measurement` | ⭐ Perfect |
| **00115131** Westley Group      | **Casting** (primary), **Machining**, **Measurement OR Testing** | Sand casting → `Casting > Sand casting`; Centrifugal casting → `Casting > Centrifugal industrial`; NDT → `Measurement OR Testing > Non Destructive testing`                                                                                                         | ⭐ Perfect |
| **00147133** Stone Marine Group | **Joining**, **Machining**, **Measurement OR Testing**           | Welding → `Joining > Welding`; CNC machining → various `Machining > *` leaf nodes; Hot straightening → `Forming > Straightening` or `Forming > Forging > [thermomechanical]`; CNC CMM → `Measurement OR Testing > Contact and non-contact coordinate measurement`   | ⭐ Perfect |
| **00075176** Excelsior          | **Moulding**                                                     | Roto-moulding → `Moulding > Rapid prototyping > Rotational molding`                                                                                                                                                                                                 | ⭐ Perfect |

---

## Original Prompt for this

```text
we have a csv file with capability taxonomy. this csv is converted into a vdb, we use text extracted from company webtext to do similarity search

this is how the input is created:
webtext 
-> use llm to extract company capabilities 
-> input to embed: if TECHNICAL_CAPABILITIES text length > 20 chars, only use TECHNICAL_CAPABILITIES , otherwise only use PRODUCTS + MANUFACTURING_PROCESSES
-> embedding is used to vss capabilities from vdb


we have proved that the vdb have distinct capabilities
we have proved the capabilities returned are inline with the webtext
we now have some good sample companies, and we want to verify if the vss response data is good

i will attach .md files with company number as the file names, please provide evaluation based on what i will give you afterwards (starting from the next message)
```

## Good Quality Capabilities are generated based on

```text
Extract company information from the website content provided above in British English.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: (optional) <comma-separated list>
ACTIVITIES: (optional) <comma-separated list>
PRODUCTS: (optional) <comma-separated list>
MARKETS: (optional) <comma-separated list>
REGIONS: (optional) <comma-separated list>
MODEL: (optional) <B2B or B2C or B2B2C or SaaS or marketplace or other>
COMPANY_SUMMARY: (mandatory) <A 500 tokens factual summary of what the company does>
COMPANY_TRADING_NAME: (mandatory) <comma-separated list>
IS_MANUFACTURING: (mandatory) <true if website specifically mentions goods production, reselling should be false>
MANUFACTURING_PROCESSES: (optional) <Summarize in 50-100 tokens HOW the company makes products. Use ONLY process names EXPLICITLY stated on website. NO inference from product types.>
TECHNICAL_CAPABILITIES: (optional) <Named technical systems, testing facilities, analytical methods, and manufacturing infrastructure. Include specific numbers and proprietary technology names where stated. Not product features or outcome descriptions.>RULES:

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
- COMPANY_SUMMARY is 100% required
- COMPANY_TRADING_NAME is required and return at most 3 names
- For MANUFACTURING_PROCESSES and TECHNICAL_CAPABILITIES: Use standard terminology and avoid listing duplicate or synonymous terms
- NEVER substitute specific terms with generic manufacturing vocabulary
- If manufacturing description is absent, output: "Not specified"
```

```json
{
  "text_max_chars_to_be_used": 16000,
  "llm_url": "http://localhost:11434/v1/chat/completions",
  "llm_model": "qwen2.5:32b"
}
```