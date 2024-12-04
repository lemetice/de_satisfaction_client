DO $$ BEGIN   RAISE NOTICE 'Executing init_postgres.sql...'; END $$;


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






