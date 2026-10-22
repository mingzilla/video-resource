# Data Normalization Decisions Framework: Where to Start

## 1. Abstraction Level <--> Processing Strategy

| Level       | Typical Processing | Example Use Case                                                           |
|-------------|--------------------|----------------------------------------------------------------------------|
| D_Document  | Runtime            | Full-text search                                                           |
| E_Entity    | Either             | Core business objects                                                      |
| A_Attribute | Creation-time      | Domain-scoped attributes (evolve to V_ when cross-domain needs emerge)     |
| V_Value     | Creation-time      | Universal values (promoted from A_ when cross-domain relationships needed) |

---

## 2. Key Differentiators Between Node Levels

### 2.1. DEAV Node Levels

Be aware that DEAV are different types of nodes. They are not properties of an entity. The property e.g. {ram: "32gb"} is abstracted out as a node `32gb: A_Ram`

| Criteria                 | D_ Documents              | E_ Entities       | A_ Attributes (Scoped)                            | V_ Values (Universal)                                   |
|--------------------------|---------------------------|-------------------|---------------------------------------------------|---------------------------------------------------------|
| **Frequency of Changes** | High (raw changes)        | Low               | Very Low                                          | Very Low                                                |
| **Query Use**            | Full-text/search          | Traversal anchors | Filtering + Relationship traversal (domain joins) | Filtering + Relationship traversal (cross-domain joins) |
| **Example**              | hp_gaming, hp_gamer: Spec | hp_530: Laptop    | intel_i9: CPU                                     | black: Color                                            |

Differentiation:

- Attributes: similar to a (scoped) Enum - It's context related - e.g. You want 32gb_ram to join different laptops
- Values: similar to a (universal) Enum - It's generic - The Values Level Nodes creates the ability to join different concepts - e.g. You want color to join car and laptop

Abilities:

- A_ and V_ nodes provide both traditional filtering capabilities (on node properties) AND relationship traversal capabilities (for discovering connections between entities).
- This dual functionality is a key advantage of the node-based approach over property-based modeling.

### 2.2. Does A_ need a `scope` property?

The scope isn't an enforced property - it's a conceptual distinction that emerges from usage patterns:

```text
A_ (Attributes) - Naturally scoped:
- intel_i9: CPU - naturally only applies to computing devices
- 32gb: RAM - naturally only applies to devices with memory
- No need to explicitly store scope, it's implicit in the domain
- 32gb: RAM - can be applied to phone or laptop, if there is a need to build phone and laptop relationship, then a V_ is needed, otherwise create scoped A_

V_ (Values) - Naturally universal:
- red: Color - naturally applies to anything that can have color
- large: Size - naturally applies across domains
```

## 3. A_ → V_ Evolution Pattern

The Evolution Pattern:

1. Start with A_ attributes for domain-specific needs
2. When cross-domain requirements emerge ("same color as my laptop" for phones)
3. Then promote/refactor to V_ values

So the distinction is more about:

- A_: allows building relationship between same type of entities - e.g. hp laptop and lenovo laptop - both relate to `32gb: LaptopRam`
- V_: allows building relationship between different types of entities - e.g. car color and laptop color - both relate to `red: Color`

The system can evolve from A_ → V_ when business requirements demand cross-domain relationships, rather than trying to predict universality upfront.

- **Trigger**: Business requirement like "find phones with same color as my laptop"


## 4. Summary - Simple Guide

- Always starts with Entity and Attribute
- When you need multiple specs to refer to the same entity -> Create D level: *D -- 1E
- When cross-domain requirements emerge ("same color as my laptop" for phones) -> Create V level: *E -- 1V
