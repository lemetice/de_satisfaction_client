CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    town VARCHAR(255),
    country VARCHAR(255),
    institution_type VARCHAR(255),
    company_name VARCHAR(255),
    trust_score NUMERIC,
    review INTEGER,
    five_star_percentage NUMERIC
);

-- Charger les données dans la table avec les colonnes modifiées
COPY companies (town, country, institution_type, company_name, trust_score, review, five_star_percentage)
    FROM '/docker-entrypoint-initdb.d/data.csv'
    DELIMITER ','
    CSV HEADER;
