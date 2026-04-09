-- ============================================================
-- Dulari Medical Store — Database Schema
-- ============================================================

-- Products table
CREATE TABLE IF NOT EXISTS products_product (
    product_id          INTEGER PRIMARY KEY,
    product_name        VARCHAR(255)    NOT NULL,
    mrp                 NUMERIC(10, 2)  NOT NULL,
    is_discontinued     BOOLEAN         NOT NULL DEFAULT FALSE,
    manufacturer_name   VARCHAR(255)    NOT NULL,
    pack_size_label     VARCHAR(255)    NOT NULL,
    short_composition1  VARCHAR(500)    NOT NULL DEFAULT '',
    short_composition2  VARCHAR(500)    NOT NULL DEFAULT '',

    -- Flag attributes for frontend filtering
    is_new_launch           BOOLEAN     NOT NULL DEFAULT FALSE,
    is_trending_near_you    BOOLEAN     NOT NULL DEFAULT FALSE,
    is_in_spotlight         BOOLEAN     NOT NULL DEFAULT FALSE
);

-- Indexes for flag-based filtering
CREATE INDEX IF NOT EXISTS idx_product_new_launch        ON products_product (is_new_launch);
CREATE INDEX IF NOT EXISTS idx_product_trending          ON products_product (is_trending_near_you);
CREATE INDEX IF NOT EXISTS idx_product_spotlight         ON products_product (is_in_spotlight);
CREATE INDEX IF NOT EXISTS idx_product_discontinued      ON products_product (is_discontinued);

-- Product images table
CREATE TABLE IF NOT EXISTS products_productimage (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products_product(product_id) ON DELETE CASCADE,
    image       VARCHAR(255) NOT NULL,
    alt_text    VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_productimage_product ON products_productimage (product_id);
