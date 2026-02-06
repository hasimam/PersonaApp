-- Add Quran values + Prophet traits tables (PostgreSQL)

CREATE TABLE IF NOT EXISTS quran_values (
    quran_value_code VARCHAR(32) PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    desc_en TEXT NOT NULL,
    desc_ar TEXT,
    refs TEXT
);

CREATE TABLE IF NOT EXISTS prophet_traits (
    trait_code VARCHAR(32) PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    desc_en TEXT NOT NULL,
    desc_ar TEXT,
    refs TEXT
);

CREATE TABLE IF NOT EXISTS quran_value_gene_weights (
    id SERIAL PRIMARY KEY,
    version_id VARCHAR(50) NOT NULL,
    quran_value_code VARCHAR(32) NOT NULL,
    gene_weights_jsonb JSONB NOT NULL,
    CONSTRAINT fk_quran_value_gene_weights_version
        FOREIGN KEY (version_id) REFERENCES app_versions(version_id) ON DELETE CASCADE,
    CONSTRAINT fk_quran_value_gene_weights_value
        FOREIGN KEY (quran_value_code) REFERENCES quran_values(quran_value_code) ON DELETE CASCADE,
    CONSTRAINT uq_quran_value_gene_weights_version_value
        UNIQUE (version_id, quran_value_code)
);

CREATE TABLE IF NOT EXISTS prophet_trait_gene_weights (
    id SERIAL PRIMARY KEY,
    version_id VARCHAR(50) NOT NULL,
    trait_code VARCHAR(32) NOT NULL,
    gene_weights_jsonb JSONB NOT NULL,
    CONSTRAINT fk_prophet_trait_gene_weights_version
        FOREIGN KEY (version_id) REFERENCES app_versions(version_id) ON DELETE CASCADE,
    CONSTRAINT fk_prophet_trait_gene_weights_trait
        FOREIGN KEY (trait_code) REFERENCES prophet_traits(trait_code) ON DELETE CASCADE,
    CONSTRAINT uq_prophet_trait_gene_weights_version_trait
        UNIQUE (version_id, trait_code)
);

CREATE INDEX IF NOT EXISTS ix_quran_value_gene_weights_version_id
    ON quran_value_gene_weights (version_id);
CREATE INDEX IF NOT EXISTS ix_quran_value_gene_weights_quran_value_code
    ON quran_value_gene_weights (quran_value_code);

CREATE INDEX IF NOT EXISTS ix_prophet_trait_gene_weights_version_id
    ON prophet_trait_gene_weights (version_id);
CREATE INDEX IF NOT EXISTS ix_prophet_trait_gene_weights_trait_code
    ON prophet_trait_gene_weights (trait_code);
