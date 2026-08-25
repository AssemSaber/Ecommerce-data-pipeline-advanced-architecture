-- ctrl + shift + p
use Atos;
Go
CREATE Schema bronze;

GO
drop table if exists bronze.customers;
drop table if exists bronze.geolocation;    
drop table if exists bronze.order_items;    
drop table if exists bronze.orders ;    
drop table if exists bronze.payments;    
drop table if exists bronze.reviews;    
drop table if exists bronze.products;    
drop table if exists bronze.sellers;    
drop table if exists bronze.product_category_name_translation;    



-- Customers
    IF OBJECT_ID('bronze.customers', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.customers (
            customer_id              VARCHAR(100),
            customer_unique_id       VARCHAR(100),
            customer_zip_code_prefix VARCHAR(20),
            customer_city            VARCHAR(100),
            customer_state           VARCHAR(10)
        );
    END;
    GO

-- select * from Atos.bronze.customers;
-- Geolocation
    IF OBJECT_ID('bronze.geolocation', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.geolocations (
            geolocation_zip_code_prefix VARCHAR(20),
            geolocation_lat             VARCHAR(50),
            geolocation_lng             VARCHAR(50),
            geolocation_city            VARCHAR(100),
            geolocation_state           VARCHAR(10)
        );
    END;
    GO


-- select * from Atos.bronze.order_items;
-- Order Items
    IF OBJECT_ID('bronze.order_items', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.order_items (
            order_id            VARCHAR(100),
            order_item_id        int,
            product_id           VARCHAR(100),
            seller_id            VARCHAR(100),
            shipping_limit_date DATETIME2,
            price               FLOAT,
            freight_value       FLOAT
        );
    END;
    GO


-- Orders
    IF OBJECT_ID('bronze.orders', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.orders (
            order_id                       VARCHAR(100),
            customer_id                    VARCHAR(100),
            order_status                   VARCHAR(50),
            order_purchase_timestamp       DATETIME2,
            order_approved_at              DATETIME2,
            order_delivered_carrier_date   DATETIME2,
            order_delivered_customer_date  DATETIME2,
            order_estimated_delivery_date  DATETIME2
);
END;
GO


-- select count(*) from bronze.payments;
-- Payments
    IF OBJECT_ID('bronze.payments', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.payments (
            order_id              VARCHAR(100),
            payment_sequential    BIGINT,
            payment_type          VARCHAR(50),
            payment_installments  VARCHAR(20),
            payment_value         FLOAT
        );
    END;
    GO


-- select count(*) from bronze.reviews;
-- Reviews
    IF OBJECT_ID('bronze.reviews', 'U') IS NULL
    BEGIN
        create table bronze.reviews (
            review_id                VARCHAR(100),
            order_id                 VARCHAR(100),
            review_score             BIGINT,
            review_comment_title     VARCHAR(MAX),
            review_comment_message   VARCHAR(MAX),
            review_creation_date     DATETIME2,
    review_answer_timestamp  DATETIME2
);
END;
GO

-- select count(*) from bronze.products;
-- Products
    IF OBJECT_ID('bronze.products', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.products (
            product_id                  VARCHAR(100),
            product_category_name       VARCHAR(100),
            product_name_lenght         INT,
            product_description_lenght  VARCHAR(20),
    product_photos_qty          BIGINT,
    product_weight_g            FLOAT,
    product_length_cm           FLOAT,
    product_height_cm           FLOAT,
    product_width_cm            FLOAT
);
END;
GO

-- select count(*) from bronze.sellers;
-- Sellers
    IF OBJECT_ID('bronze.sellers', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.sellers (
    seller_id           VARCHAR(100),
    seller_zip_code_prefix VARCHAR(20),
    seller_city         VARCHAR(100),
    seller_state        VARCHAR(10)
);
END;
GO

-- select count(*) from bronze.product_category_name_translation;
-- Product Category Translation
    IF OBJECT_ID('bronze.product_category_name_translation', 'U') IS NULL
    BEGIN
        CREATE TABLE bronze.product_category_name_translation (
            product_category_name         VARCHAR(100),
            product_category_name_english VARCHAR(100)
        );
    END;
    GO