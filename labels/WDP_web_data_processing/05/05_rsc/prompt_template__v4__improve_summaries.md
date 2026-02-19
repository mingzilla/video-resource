## Prompt V4 - Improve Summary

```text
Extract company information from the website content provided above.

OUTPUT FORMAT - Start immediately with the first category:

INDUSTRIES: (optional) <comma-separated list>
ACTIVITIES: (optional) <comma-separated list>
PRODUCTS: (optional) <comma-separated list>
MARKETS: (optional) <comma-separated list>
REGIONS: (optional) <comma-separated list>
MODEL: (optional) <B2B or B2C or B2B2C or SaaS or marketplace or other>
FULL_SUMMARY_DESCRIPTION: (mandatory) <A 500 tokens factual summary of what the company does>

RULES:
- Use ONLY explicit information from the website content above
- Do not add, infer, or guess anything not stated
- Skip any category with no information
- No preamble, no introduction, no explanations
- Start output immediately with first category
- FULL_SUMMARY_DESCRIPTION is 100% required

```

### Enhancement

- Inactive Companies == Bad Results: Remove inactive companies      
- change `FULL_SUMMARY_DESCRIPTION` to have `<A 500 tokens factual summary of what the company does>`

```text
BEFORE:
EdHat International is a leading UK-based academic organisation that provides quality educational services to international students. 
The company offers various programs and services, including curriculum endorsement, research conferences, study abroad programs, test engines, 
learning management systems, and institute management systems, catering to the needs of students and institutions worldwide.

AFTER:
EdHat International is a leading UK-based academic organization that provides quality academic qualifications and educational services to international students. 
The company offers a range of programs, including Curriculum Endorsement Programmes, EdHat Test Engine, 
Institute Management System, and Learning Management System, designed to meet the needs of institutions and organizations worldwide. 
With a focus on research conferences, study abroad programs, and digital education solutions, 
EdHat International aims to help students achieve their academic goals and stay ahead in an ever-changing world.
```
