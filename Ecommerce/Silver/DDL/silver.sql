USE Atos;
GO

--CREATE SCHEMA silver;
--CREATE SCHEMA rejectedRows;
-- CREATE SCHEMA stage;

GO

-- DROP TABLE IF EXISTS silver.customers;
-- DROP TABLE IF EXISTS silver.geolocation;
-- DROP TABLE IF EXISTS silver.order_items;
-- DROP TABLE IF EXISTS silver.orders;
-- DROP TABLE IF EXISTS silver.payments;
-- DROP TABLE IF EXISTS silver.reviews;
-- DROP TABLE IF EXISTS silver.products;
-- DROP TABLE IF EXISTS silver.sellers;
-- DROP TABLE IF EXISTS silver.product_category_name_translation;
GO


-- Customers

IF OBJECT_ID('silver.customers', 'U') IS NULL
BEGIN
    CREATE TABLE silver.customers (
        customer_id              VARCHAR(100),
        customer_unique_id          VARCHAR(100),
        customer_zip_code_prefix VARCHAR(20),
        customer_city            VARCHAR(100),
        customer_state           VARCHAR(10),
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.customers', 'U') IS NULL
BEGIN
    CREATE TABLE stage.customers (
        customer_id              VARCHAR(100),
        customer_unique_id          VARCHAR(100),
        customer_zip_code_prefix VARCHAR(20),
        customer_city            VARCHAR(100),
        customer_state           VARCHAR(10),
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('rejected_customers', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_customers (
        customer_id              VARCHAR(100),
        customer_unique_id          VARCHAR(100),
        customer_zip_code_prefix VARCHAR(20),
        customer_city            VARCHAR(100),
        customer_state           VARCHAR(10),
        reason                    VARCHAR(100)
    );
END;
GO

-- Geolocation
IF OBJECT_ID('silver.geolocation', 'U') IS NULL
BEGIN
    CREATE TABLE silver.geolocations (
        geolocation_zip_code_prefix VARCHAR(20),
        geolocation_lat             VARCHAR(50),
        geolocation_lng             VARCHAR(50),
        geolocation_city            VARCHAR(100),
        geolocation_state           VARCHAR(10),
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('rejected_geolocation', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_geolocations (
        geolocation_zip_code_prefix VARCHAR(20),
        geolocation_lat             VARCHAR(50),
        geolocation_lng             VARCHAR(50),
        geolocation_city            VARCHAR(100),
        geolocation_state           VARCHAR(10),
        reason                      VARCHAR(100)
    );
END;
GO

-- Order Items
IF OBJECT_ID('silver.order_items', 'U') IS NULL
BEGIN
    CREATE TABLE silver.order_items (
        order_item_id         VARCHAR(100),
        order_id              VARCHAR(100),
        product_id            VARCHAR(100),
        seller_id             VARCHAR(100),
        shipping_limit_date   DATETIME2,
        price                 FLOAT,
        freight_value         FLOAT,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.order_items', 'U') IS NULL
BEGIN
    CREATE TABLE stage.order_items (
        order_item_id         VARCHAR(100),
        order_id              VARCHAR(100),
        product_id            VARCHAR(100),
        seller_id             VARCHAR(100),
        shipping_limit_date   DATETIME2,
        price                 FLOAT,
        freight_value         FLOAT,
        load_timestamp            DATETIME2
    );
END;
GO


IF OBJECT_ID('rejected_order_items', 'U') IS NULL
BEGIN
    create TABLE rejected_order_items (
        order_item_id         VARCHAR(100),
        order_id              VARCHAR(100),
        product_id            VARCHAR(100),
        seller_id             VARCHAR(100),
        shipping_limit_date   DATETIME2,
        price                 FLOAT,
        freight_value         FLOAT,
        reason                VARCHAR(200)
    );
END;
GO


-- Orders
IF OBJECT_ID('silver.orders', 'U') IS NULL
BEGIN
    create TABLE silver.orders (
        order_id                     VARCHAR(100),
        customer_id                  VARCHAR(100),
        order_status                 VARCHAR(50),
        order_purchase_timestamp     DATETIME2,
        order_approved_at            DATETIME2,
        order_delivered_carrier_date DATETIME2,
        order_delivered_customer_date DATETIME2,
        order_estimated_delivery_date DATETIME2,
        is_updated               INT DEFAULT 0,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.orders', 'U') IS NULL
BEGIN
    CREATE TABLE stage.orders (
        order_id                     VARCHAR(100),
        customer_id                  VARCHAR(100),
        order_status                 VARCHAR(50),
        order_purchase_timestamp     DATETIME2,
        order_approved_at            DATETIME2,
        order_delivered_carrier_date DATETIME2,
        order_delivered_customer_date DATETIME2,
        order_estimated_delivery_date DATETIME2,
        load_timestamp            DATETIME2,
        
    );
END;
GO

IF OBJECT_ID('rejected_orders', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_orders (
        order_id                     VARCHAR(100),
        customer_id                  VARCHAR(100),
        order_status                 VARCHAR(50),
        order_purchase_timestamp     DATETIME2,
        order_approved_at            DATETIME2,
        order_delivered_carrier_date DATETIME2,
        order_delivered_customer_date DATETIME2,
        order_estimated_delivery_date DATETIME2,
        reason                       VARCHAR(100)
    );
END;
GO


-- Payments
IF OBJECT_ID('silver.payments', 'U') IS NULL
BEGIN
    CREATE TABLE silver.payments (
        order_id              VARCHAR(100),
        payment_sequential    BIGINT,
        payment_type          VARCHAR(50),
        payment_installments  VARCHAR(20),
        payment_value         FLOAT,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.payments', 'U') IS NULL
BEGIN
    CREATE TABLE stage.payments (
        order_id              VARCHAR(100),
        payment_sequential    BIGINT,
        payment_type          VARCHAR(50),
        payment_installments  VARCHAR(20),
        payment_value         FLOAT,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('rejected_payments', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_payments (
        order_id              VARCHAR(100),
        payment_sequential    BIGINT,
        payment_type          VARCHAR(50),
        payment_installments  VARCHAR(20),
        payment_value         FLOAT,
        reason                VARCHAR(100)
    );
END;
GO


-- Reviews
IF OBJECT_ID('silver.reviews', 'U') IS NULL
BEGIN
    CREATE TABLE silver.reviews (
        review_id               VARCHAR(100),
        order_id                VARCHAR(100),
        review_score            BIGINT,
        review_creation_date    DATETIME2,
        review_answer_timestamp DATETIME2,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.reviews', 'U') IS NULL
BEGIN
    CREATE TABLE stage.reviews (
        review_id               VARCHAR(100),
        order_id                VARCHAR(100),
        review_score            BIGINT,
        review_creation_date    DATETIME2,
        review_answer_timestamp DATETIME2,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('rejected_reviews', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_reviews (
        review_id               VARCHAR(100),
        order_id                VARCHAR(100),
        review_score            BIGINT,
        review_comment_title    VARCHAR(MAX),
        review_comment_message  VARCHAR(MAX),
        review_creation_date    DATETIME2,
        review_answer_timestamp DATETIME2,
        reason                  VARCHAR(100)
    );
END;
GO


-- Products
IF OBJECT_ID('silver.products', 'U') IS NULL
BEGIN
    create TABLE silver.products (
        product_id                   VARCHAR(100),
        product_category_name        VARCHAR(100),
        product_name_lenght          INT,
        product_description_lenght   VARCHAR(20),
        product_photos_qty           BIGINT,
        product_weight_g             FLOAT,
        product_length_cm            FLOAT,
        product_height_cm            FLOAT,
        product_width_cm             FLOAT,
        is_delete               INT DEFAULT 0,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.products', 'U') IS NULL
BEGIN
    CREATE TABLE stage.products (
        product_id                   VARCHAR(100),
        product_category_name        VARCHAR(100),
        product_name_lenght          INT,
        product_description_lenght   VARCHAR(20),
        product_photos_qty           BIGINT,
        product_weight_g             FLOAT,
        product_length_cm            FLOAT,
        product_height_cm            FLOAT,
        product_width_cm             FLOAT,
        is_delete            INT DEFAULT 0,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('rejected_products', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_products (
        product_id                   VARCHAR(100),
        product_category_name        VARCHAR(100),
        product_name_lenght          INT,
        product_description_lenght   VARCHAR(20),
        product_photos_qty           BIGINT,
        product_weight_g             FLOAT,
        product_length_cm            FLOAT,
        product_height_cm            FLOAT,
        product_width_cm             FLOAT,
        reason                       VARCHAR(100)
    );
END;
GO

-- Sellers
IF OBJECT_ID('silver.sellers', 'U') IS NULL
BEGIN
    create TABLE silver.sellers (
        seller_id               VARCHAR(100),
        seller_zip_code_prefix  VARCHAR(20),
        seller_city             VARCHAR(100),
        seller_state            VARCHAR(10),
        is_delete               INT DEFAULT 0,
        load_timestamp            DATETIME2
    );
END;
GO

IF OBJECT_ID('stage.sellers', 'U') IS NULL
BEGIN
    create TABLE stage.sellers (
        seller_id               VARCHAR(100),
        seller_zip_code_prefix  VARCHAR(20),
        seller_city             VARCHAR(100),
        seller_state            VARCHAR(10),
        is_delete            INT DEFAULT 0,
        load_timestamp            DATETIME2

    );
END;
GO

IF OBJECT_ID('rejected_sellers', 'U') IS NULL
BEGIN
    CREATE TABLE rejected_sellers (
        seller_id               VARCHAR(100),
        seller_zip_code_prefix  VARCHAR(20),
        seller_city             VARCHAR(100),
        seller_state            VARCHAR(10),
        reason                  VARCHAR(100)
    );
END;
GO

-- Product Category Translation
IF OBJECT_ID('silver.product_category_name_translation', 'U') IS NULL
BEGIN
    CREATE TABLE silver.product_category_name_translation (
        product_category_name         VARCHAR(100),
        product_category_name_english VARCHAR(100),
        load_timestamp            DATETIME2
    );
END;
GO
