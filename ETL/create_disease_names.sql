CREATE TABLE disease_names AS
SELECT disease_name FROM human_disease_experiments_full
UNION DISTINCT
SELECT disease_name FROM human_disease_knowledge_full;


CREATE TABLE gene_disease AS
SELECT disease_name, gene_name FROM human_disease_knowledge_full
UNION DISTINCT
SELECT disease_name, gene_name FROM human_disease_experiments_full;