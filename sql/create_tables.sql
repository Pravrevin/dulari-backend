-- ============================================================
-- Dulari Medical Store — Database Schema
-- Drop existing tables (in reverse FK order) then recreate
-- ============================================================

DROP TABLE IF EXISTS products_genericmedicine CASCADE;
DROP TABLE IF EXISTS products_productimage    CASCADE;
DROP TABLE IF EXISTS products_product         CASCADE;
DROP TABLE IF EXISTS products_category        CASCADE;

-- ============================================================
-- Category table (must be created before products)
-- ============================================================
CREATE TABLE products_category (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL UNIQUE,
    description TEXT            NOT NULL DEFAULT ''
);

-- ============================================================
-- Products table
-- ============================================================
CREATE TABLE products_product (
    product_id          INTEGER PRIMARY KEY,
    product_name        VARCHAR(255)    NOT NULL,
    mrp                 NUMERIC(10, 2)  NOT NULL,
    is_discontinued     BOOLEAN         NOT NULL DEFAULT FALSE,
    manufacturer_name   VARCHAR(255)    NOT NULL,
    pack_size_label     VARCHAR(255)    NOT NULL,
    short_composition1  VARCHAR(500)    NOT NULL DEFAULT '',
    short_composition2  VARCHAR(500)    NOT NULL DEFAULT '',

    category_id         INTEGER REFERENCES products_category(id) ON DELETE SET NULL,

    -- Flag attributes for frontend filtering
    is_new_launch           BOOLEAN     NOT NULL DEFAULT FALSE,
    is_trending_near_you    BOOLEAN     NOT NULL DEFAULT FALSE,
    is_in_spotlight         BOOLEAN     NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_product_category      ON products_product (category_id);
CREATE INDEX idx_product_new_launch    ON products_product (is_new_launch);
CREATE INDEX idx_product_trending      ON products_product (is_trending_near_you);
CREATE INDEX idx_product_spotlight     ON products_product (is_in_spotlight);
CREATE INDEX idx_product_discontinued  ON products_product (is_discontinued);

-- ============================================================
-- Product images table
-- ============================================================
CREATE TABLE products_productimage (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products_product(product_id) ON DELETE CASCADE,
    image       VARCHAR(255) NOT NULL,
    alt_text    VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE INDEX idx_productimage_product ON products_productimage (product_id);

-- ============================================================
-- Generic medicine table
-- ============================================================
CREATE TABLE products_genericmedicine (
    generic_product_id  SERIAL PRIMARY KEY,
    name                VARCHAR(255)    NOT NULL,
    brand               VARCHAR(255)    NOT NULL,
    mrp                 NUMERIC(10, 2)  NOT NULL,
    discount_percentage NUMERIC(5, 2)   NOT NULL DEFAULT 0,
    image               VARCHAR(255)    NOT NULL DEFAULT '',
    product_id          INTEGER         NOT NULL REFERENCES products_product(product_id) ON DELETE CASCADE
);

CREATE INDEX idx_genericmedicine_product ON products_genericmedicine (product_id);
