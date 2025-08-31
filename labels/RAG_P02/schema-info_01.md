# Component 1 - DB schema extraction

The purpose of this step is to extract db structure and create json objects:

```text
- 1. Input/Output
- 2. Columns
- 3. SQL
- 4. Memory Strategy
```

## 1. Output

```json
{
  "ClassifiedCompaniesRelational_Jul2025__ClassifiedCompaniesRelational__CompanyName": {
    "column_name": "CompanyName",
    "data_type": "VARCHAR",
    "database_name": "ClassifiedCompaniesRelational_Jul2025",
    "null_percentage": 0.0,
    "sample_data": [
      "HOUSE OF MIAHS LIMITED",
      "KONSTNAR LIMITED",
      "B-SPOKE AUTOMOTIVE LIMITED",
      "CLARITY ULTRASOUND LIMITED",
      "FUNLINX UK LTD"
    ],
    "table_name": "ClassifiedCompaniesRelational",
    "total_rows": 10204100,
    "unique_count": 10026123
  }
}
```

```text
ClassifiedCompaniesRelational_Jul2025__ClassifiedCompaniesRelational__CompanyCategory
ClassifiedCompaniesRelational_Jul2025__ClassifiedCompaniesRelational__CompanyName
```

Why:

- use keys to loop
- use object to quick access data

## 2. Columns

The goal is to make sure the next step can have description, so we prepare whatever useful to create a good description.

| columns                                            | purpose                                                                     |
|----------------------------------------------------|-----------------------------------------------------------------------------|
| table_name + column_name + sample data + data_type | generate description                                                        |
| database_name                                      | to be used to generate an identifier - useful when multiple schema are used |
| unique_count                                       | for normalization - likely to be enum when it's low                         |
| other columns                                      | useful information                                                          |

## 3. Sample SQL

### 3.1. Sample Data

```sql
  SELECT {column_name}
    FROM {table_name}
   WHERE {column_name} IS NOT NULL -- NOT NULL is important
GROUP BY {column_name}             -- 1) Unique Values; 2) Performance? - worth it
   LIMIT {limit}                   -- 5 sample values - enough
   
-- ORDER BY??                      -- Avoid - 1) Performance Cost, 2) Don't want "A~" data for everything
```

### 3.2. Counts

| SQL                                                                                    | purpose         |
|----------------------------------------------------------------------------------------|-----------------|
| SELECT COUNT(*) FROM {table_name}                                                      | total row count |
| SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL                          | null count      |
| SELECT COUNT(DISTINCT {column_name}) FROM {table_name} WHERE {column_name} IS NOT NULL | unique count    |

## 4. Memory Strategy

- Small Count (e.g. < 1000 columns) - in memory processing -> dump into a file
- IO once - file handling, synchronization
