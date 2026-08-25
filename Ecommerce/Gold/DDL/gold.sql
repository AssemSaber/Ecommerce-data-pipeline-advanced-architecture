USE Atos;
GO

-- CREATE SCHEMA gold;



-- Customers


IF OBJECT_ID('metadata', 'U') IS NULL
BEGIN
    CREATE TABLE metadata (
        table_name         VARCHAR(100),
        last_load          DATETIME2
    );
END;
GO

delete from metadata;

update metadata set last_load='1990-1-1' where table_name='products'

insert into metadata 
values('customers','1990-1-1'),
('order_items','1990-1-1'),
('orders','1990-1-1'),
('payments','1990-1-1'),
('products','1990-1-1'),
('reviews','1990-1-1'),
('sellers','1990-1-1');

select * from metadata


IF OBJECT_ID('gold.dim_customers', 'U') IS NULL
BEGIN
    CREATE TABLE gold.dim_customers (
        customer_sk             BIGINT IDENTITY(1,1) PRIMARY KEY,
        customer_id             VARCHAR(100),
        customer_unique_id      VARCHAR(100),
        customer_zip_code_prefix VARCHAR(20),
        customer_city           VARCHAR(100),
        customer_state          VARCHAR(10)
    );
END;
GO



IF OBJECT_ID('gold.dim_products', 'U') IS NULL
BEGIN
    CREATE TABLE gold.dim_products (
        product_sk                  BIGINT IDENTITY(1,1) PRIMARY KEY,
        product_id                  VARCHAR(100),
        product_category_name       VARCHAR(100),
        product_name_lenght         INT,
        product_description_lenght  INT,
        product_photos_qty          BIGINT,
        product_weight_g             FLOAT,
        product_length_cm            FLOAT,
        product_height_cm            FLOAT,
        product_width_cm             FLOAT,
        is_delete               INT DEFAULT 0,
        is_current              INT DEFAULT 1,
        start_date              DATETIME2,
        end_date                DATETIME2
    );
END;
GO


IF OBJECT_ID('gold.dim_sellers', 'U') IS NULL
BEGIN
    CREATE TABLE gold.dim_sellers (
        seller_sk               BIGINT IDENTITY(1,1) PRIMARY KEY,
        seller_id               VARCHAR(100),
        seller_zip_code_prefix  VARCHAR(20),
        seller_city             VARCHAR(100),
        seller_state            VARCHAR(10),
        is_delete               INT DEFAULT 0
    );
END;
GO


IF OBJECT_ID('gold.status_payments', 'U') IS NULL
BEGIN
    create TABLE gold.status_payments (
        payment_sk            BIGINT IDENTITY(1,1) PRIMARY KEY,
        payment_type          VARCHAR(50),
        order_status          VARCHAR(50)
    );
END;
GO




IF OBJECT_ID('gold.dim_date', 'U') IS NULL
BEGIN
    CREATE TABLE gold.dim_date (
        date_sk       BIGINT IDENTITY(1,1) PRIMARY KEY,
        full_date     DATE,
        year          INT,
        month         INT,
        day           INT,
        quarter       INT
    );
END;
GO


delete from gold.fact_orders;
select * from metadata;
select * from gold.fact_orders;
IF OBJECT_ID('gold.fact_orders', 'U') IS NULL
BEGIN
    CREATE TABLE gold.fact_orders (
        order_id                         VARCHAR(100) NOT NULL,
        customer_sk                      BIGINT,
        product_sk                       BIGINT,
        seller_sk                        BIGINT,
        payment_sk                       BIGINT,
        order_purchase_date_sk           BIGINT,
        order_approved_date_sk           BIGINT,
        order_delivered_carrier_date_sk  BIGINT,
        order_delivered_customer_date_sk BIGINT,
        order_estimated_delivery_date_sk BIGINT,
        price                             DECIMAL(18, 2),
        freight_value                     DECIMAL(18, 2),
        review_score                     INT,
    );
END;
GO