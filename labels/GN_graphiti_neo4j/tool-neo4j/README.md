## Conventions:

Community Edition only allows one database per instance, so we apply naming conventions to solve such a problem.

```text
docker-compose__x__topic.yml
|
|-- service: neo4j__x__topic
|-- container_name: neo4j__x__topic
|-- port: x7474, x7687
+-- docker-volumes/x__topic/*
```

## Start Container:

```bash
docker-compose -f docker-compose__1__laptops.yml up -d
```

## Key Configuration

| Setting                     | Purpose              | Info                                        |
|-----------------------------|----------------------|---------------------------------------------|
| `NEO4J_AUTH`                | Username/password    | `neo4j/test1234`                            |
| Port x7474                  | Web interface        | Browser access e.g.: http://localhost:17474 |
| Port x7687                  | Bolt protocol        | connections e.g.: `bolt://localhost:17687`  |
| `/1__laptops/data` volume   | Database storage     | Persistence                                 |
| `/1__laptops/import` volume | CSV import directory | Data loading                                |

## Import Data

Start the docker container, and then do e.g. the below:

1. copy x.cypher, *.csv into `docker-volumes/1__laptops/import`
2. `docker exec -it neo4j__1__laptops bash`
3. `cd import`
4. `cypher-shell -u neo4j -p test1234 -f laptop-data__neo4j_import.cypher`