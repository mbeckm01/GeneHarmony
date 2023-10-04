-- Create table of distinct disease names for multiselect input
CREATE TABLE disease_names AS
SELECT disease_name FROM human_disease_experiments_full
UNION DISTINCT
SELECT disease_name FROM human_disease_knowledge_full
UNION DISTINCT
SELECT disease_name FROM human_disease_textmining_full;

-- Create table of distinct disease and gene names for returning relevant search results
CREATE TABLE gene_disease AS
SELECT disease_name, gene_name FROM human_disease_knowledge_full
UNION DISTINCT
SELECT disease_name, gene_name FROM human_disease_experiments_full
UNION DISTINCT
SELECT disease_name, gene_name FROM human_disease_textmining_full;

-- Create table of distinct disease names, gene names, confidence scores, and source data
CREATE TABLE diseases_full AS
    SELECT disease_name, gene_name, confidence_score, source_database AS source
    FROM human_disease_knowledge_full
UNION DISTINCT
    SELECT disease_name, gene_name, confidence_score, source_database AS source
    FROM human_disease_experiments_full
UNION DISTINCT
    SELECT disease_name, gene_name, confidence_score, abstract_url AS source
    FROM human_disease_textmining_full;