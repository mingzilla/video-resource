## Prompt - Original Prompt and Result

```text
EXTRACT COMPANY INFORMATION FROM WEBSITE TEXT

RULES:
- Use ONLY information explicitly in the text below
- Do not add, infer, or guess anything
- If a category doesn't apply, skip it

TASK:
1. Extract 15-20 total labels across these categories:
 - industries: primary/secondary industries
 - activities: daily operations
 - products: specific products/services
 - markets: customer segments served
 - regions: geographic operations
 - model: B2B, B2C, SaaS, etc.
 - competencies: specialized skills/advantages

2. Write factual summary (max 500 tokens) from text only.

FORMAT:
industries: software, cybersecurity
activities: threat_monitoring, incident_response
products: firewall_system, intrusion_detection
markets: banks, government_agencies
regions: UK, Europe
model: B2B
competencies: real_time_analytics
SUMMARY: [factual summary here]

WEBSITE CONTENT:
{cleaned_webtext}

EXTRACT:
```

### What's Good

- Use ONLY information explicitly in the text below
- Labels then Summary
- Write factual summary (max 500 tokens) from text only

### Problems

- Always have prefix
- Labels not consistent
- Summary may not exist
- Data Contamination! - Every Company is `Cybersecurity`

### Examples

```text
Here are the extracted labels across the categories:

industries:
- Education
- Cybersecurity (implied by "firewall_system" and "intrusion_detection")

activities:
- Threat monitoring
- Incident response
- Digital education
- Online exams
- Research conferences

products:
- Firewall system
- Intrusion detection
- Test engine
- Learning management system (LMS)
- Institute management system (IMS)

markets:
- Banks
- Government agencies
- International students
- Educational institutions

regions:
- UK
- Europe

model:
- B2B

competencies:
- Real-time analytics
```

```text
Here are the extracted labels:

industries:
- software
- cybersecurity

activities:
- threat_monitoring
- incident_response

products:
- firewall_system
- intrusion_detection

markets:
- banks
- government_agencies

regions:
- UK
- Europe

model:
- B2B

competencies:
- real_time_analytics
```

```text
Here are the extracted labels:

1. industries:
 - software
2. activities:
 - threat_monitoring
 - incident_response
3. products:
 - firewall_system
 - intrusion_detection
4. markets:
 - banks
 - government_agencies
5. regions:
 - UK
 - Europe
6. model:
 - B2B
7. competencies:
 - real_time_analytics

Summary: Sherlock Games focuses on detailed analysis to solve complex cases, following them on Instagram and Facebook.
```