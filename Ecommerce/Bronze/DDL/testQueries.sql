    use Atos;
    GO

delete from bronze.customers;
delete from silver.customers;
delete from stage.customers;
select count(*) from bronze.customers;
select count(*) from silver.customers;
select * from bronze.customers;
select * from stage.customers;
select * from silver.customers;
    
delete from bronze.orders;
delete from silver.orders;
DELETE from rejected_orders;
select count(*) from bronze.orders;
select count(*) from silver.orders;
select * from bronze.orders;
select * from silver.orders;
select * from stage.orders;

DELETE from rejected_customers;
DELETE from rejected_orders;

select * from rejected_customers;
select * from rejected_orders;


delete from bronze.payments;
delete from silver.payments;
delete from rejected_payments;

select count(*) from bronze.payments;
select count(*) from silver.payments;
select * from bronze.payments;
select * from silver.payments;
select * from rejected_payments;


delete from bronze.reviews;
delete from silver.reviews;
delete from rejected_reviews;

select count(*) from bronze.reviews;
select count(*) from silver.reviews;
select * from bronze.reviews;
select * from silver.reviews;
select * from rejected_reviews;

delete from bronze.sellers;
delete from silver.sellers;
delete from rejected_sellers;

select count(*) from bronze.sellers;
select count(*) from silver.sellers;
select * from bronze.sellers;
select * from silver.sellers;
select * from rejected_sellers;

delete from stage.products;
delete from bronze.products;
delete from silver.products;
delete from rejected_products;

select count(*) from bronze.products;
select count(*) from silver.products;
select * from bronze.products;
select * from silver.products;
select * from rejected_products;

delete from bronze.order_items;
delete from silver.order_items;
delete from rejected_order_items;

select count(*) from bronze.order_items;
select count(*) from silver.order_items;
select * from bronze.order_items;
select * from silver.order_items;
select * from rejected_order_items;

---




delete from metadata;
update metadata set last_load='1990-1-1' where table_name='products'
update metadata set last_load='1990-1-1' where table_name='sellers'
update metadata set last_load='1990-1-1' where table_name='customers'
update metadata set last_load='2026-01-01' where table_name='date'

select * from gold.dim_date where date_sk=491

select * from silver.orders where order_id='136cce7faa42fdb2cefd53fdc79a6098'
select * from gold.fact_orders where order_id='136cce7faa42fdb2cefd53fdc79a6098'
select count(*) from silver.order_items
select * from gold.fact_orders
select count(*) from gold.fact_orders
delete from silver.orders;

delete from gold.fact_orders;
update metadata set last_load='1990-1-1' where table_name='payments'
update metadata set last_load='1990-1-1' where table_name='orders'
update metadata set last_load='1990-1-1' where table_name='order_items'
update metadata set last_load='1990-1-1' where table_name='reviews'

select * from metadata
select max(full_date) from gold.dim_date;

delete from gold.dim_customers;


select count(*) from gold.dim_customers;
select * from gold.dim_customers;
select * from gold.dim_customers where customer_id='06b8999e2fba1a1fbc88172c00ba8bc7'

select * from gold.dim_customers;

delete from gold.dim_sellers;
select * from silver.sellers;
select count(*) from gold.dim_sellers;

delete from gold.dim_sellers;
select count(*) from gold.dim_sellers;
select * from gold.dim_sellers;
select * from gold.dim_sellers where seller_id='116ccb1a1604bc88e4d234a8c23f33de'
select * from gold.dim_sellers where is_delete=1;

delete from gold.dim_products;
delete from silver.products;
delete from stage.products;
select * from gold.dim_products where product_id='3aa071139cb16b67ca9e5dea641aaa2f';
select * from gold.dim_products where is_delete=1;
select * from gold.dim_products where end_date is not null;
select max(load_timestamp) from silver.products where load_timestamp>'2026-08-17 02:11:50.290000';
select max(load_timestamp) from silver.products;
select max(last_load) from metadata;
select * from silver.products where load_timestamp>'2026-08-17 14:28:00.0000000'
select max(load_timestamp) from stage.products;
select * from stage.products where load_timestamp>'2026-08-17 02:30:57.7333333';

select product_id,count(*) from silver.products 
GROUP by product_id 
having count(*)>1

--- status_payments
select * from gold.status_payments;

select min(order_purchase_timestamp) from silver.orders;
select max(order_purchase_timestamp) from silver.orders;
------------ payments
select review_id, order_id, review_score from silver.payments 
        where load_timestamp > '1990-01-01 00:00:00'





-- customers bronze
    SELECT
        b.customer_id,
        b.customer_unique_id,
        b.customer_zip_code_prefix,
        b.customer_city,
        b.customer_state
    FROM bronze.customers AS b
    LEFT JOIN silver.customers AS s
        ON b.customer_id = s.customer_id
    WHERE
        s.customer_id IS NULL
        OR ISNULL(b.customer_unique_id, '') <> ISNULL(s.customer_unique_id, '')
        OR ISNULL(b.customer_zip_code_prefix, -1) <> ISNULL(s.customer_zip_code_prefix, -1)
        OR ISNULL(b.customer_city, '') <> ISNULL(s.customer_city, '')
        OR ISNULL(b.customer_state, '') <> ISNULL(s.customer_state, '');

-- orders bronze
select * from bronze.products
select * from stage.products
select * from silver.products

select product_category_name from silver.products

SELECT
b.product_id,
s.product_id,
b.product_category_name,
s.product_category_name,
b.product_name_lenght,
s.product_name_lenght,
b.product_description_lenght,
s.product_description_lenght,
b.product_photos_qty,
s.product_photos_qty,
b.product_weight_g,
s.product_weight_g,
b.product_length_cm,
s.product_length_cm,
b.product_height_cm,
s.product_height_cm,
b.product_width_cm,
s.product_width_cm
FROM bronze.products AS b
LEFT JOIN silver.products AS s
    ON b.product_id = s.product_id
WHERE
    s.product_id IS NULL

    OR ISNULL(b.product_category_name, '') <> ISNULL(s.product_category_name, '')

    OR ISNULL(b.product_name_lenght, -1) <> ISNULL(s.product_name_lenght, -1)

    OR ISNULL(b.product_description_lenght, '') <> ISNULL(s.product_description_lenght, '')

    OR ISNULL(b.product_photos_qty, -1) <> ISNULL(s.product_photos_qty, -1)

    OR ISNULL(b.product_weight_g, -1)  <> ISNULL(s.product_weight_g, -1)

    OR ISNULL(b.product_length_cm, -1)  <> ISNULL(s.product_length_cm, -1)

    OR ISNULL(b.product_height_cm, -1)  <> ISNULL(s.product_height_cm, -1)

    OR ISNULL(b.product_width_cm, -1) <> ISNULL(s.product_width_cm, -1);
---

SELECT
    b.order_id,
    b.payment_sequential,
    b.payment_type,
    b.payment_installments,
    b.payment_value

FROM bronze.payments AS b
LEFT JOIN silver.payments AS s
    ON b.order_id = s.order_id
WHERE
    s.order_id IS NULL

SELECT
count(*)
FROM bronze.payments AS b
LEFT JOIN silver.payments AS s
    ON b.order_id = s.order_id
WHERE
    s.order_id IS NULL


-- reviews --
SELECT
        b.review_id,
        b.order_id,
        b.review_score,
        b.review_creation_date,
        b.review_answer_timestamp
    FROM bronze.reviews AS b
    LEFT JOIN silver.reviews AS s
        ON b.review_id = s.review_id
    WHERE
        s.review_id IS NULL;

-- sellers
    SELECT
        b.seller_id,
        b.seller_zip_code_prefix,
        b.seller_city,
        b.seller_state
    FROM bronze.sellers AS b
    LEFT JOIN silver.sellers AS s
        ON b.seller_id = s.seller_id
    WHERE
        s.seller_id IS NULL;



SELECT
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state
FROM silver.sellers AS s
LEFT JOIN bronze.sellers AS b
    ON s.seller_id = b.seller_id
WHERE b.seller_id IS NULL
  AND s.is_delete = 0;


UPDATE s
SET
    s.is_delete = 1,
    s.load_timestamp = SYSDATETIME()
FROM silver.sellers AS s
LEFT JOIN bronze.sellers AS b
    ON s.seller_id = b.seller_id
WHERE b.seller_id IS NULL
  AND s.is_delete = 0;



--- order items ------

    SELECT
        b.order_id,
        b.order_item_id ,
        b.product_id,
        b.seller_id,
        b.shipping_limit_date,
        b.price,
        b.freight_value
    FROM bronze.order_items AS b
    LEFT JOIN silver.order_items AS s
        ON b.order_id = s.order_id
        AND b.order_item_id = s.order_item_id
    WHERE
        s.order_id IS NULL


SELECT *
    FROM silver.order_items AS oi
    LEFT JOIN silver.orders AS s
        ON oi.order_id = s.order_id
    WHERE
        s.order_id IS NULL


SELECT *
    FROM silver.order_items AS oi
    LEFT JOIN silver.sellers AS s
        ON oi.seller_id = s.seller_id
    WHERE
        s.seller_id IS NULL

select distinct seller_id from silver.sellers
select distinct seller_id from silver.orders

delete from bronze.reviews;
delete from bronze.reviews;
select * from bronze.reviews;
select * from silver.reviews;
select * from bronze.sellers;
select * from silver.sellers;

SELECT
        b.review_id,
        b.order_id,
        b.review_score,
        b.review_creation_date,
        b.review_answer_timestamp
    FROM bronze.reviews AS b
    LEFT JOIN silver.reviews AS s
        ON b.review_id = s.review_id
    WHERE
        s.review_id IS NULL;

select * from
gold.fact_orders o left join gold.dim_products p
on p.product_sk=o.product_sk
where p.product_sk is null

select
order_id,
dd.full_date as carrier_date,
dd.full_date as delivered_date,
product_category_name
from gold.dim_date dd join gold.fact_orders fo
on dd.date_sk=fo.order_delivered_carrier_date_sk
join gold.dim_products dp 
on fo.product_sk=dp.product_sk
join gold.dim_date dd2
on dd2.date_sk=fo.order_delivered_customer_date_sk
where product_category_name='beleza_saude'

select * from gold.dim_products
select * from gold.fact_orders

select * from metadata;
update metadata set last_load='1990-1-1' where table_name='customers'
update metadata set last_load='1990-1-1' where table_name='order_items'
update metadata set last_load='1990-1-1' where table_name='orders'
update metadata set last_load='1990-1-1' where table_name='payments'
update metadata set last_load='1990-1-1' where table_name='products'
update metadata set last_load='1990-1-1' where table_name='reviews'
update metadata set last_load='1990-1-1' where table_name='sellers'
-- update metadata set last_load='2026-01-01' where table_name='date'

delete from silver.customers;
delete from silver.order_items;
delete from silver.orders;
delete from silver.payments;
delete from silver.products;
delete from silver.reviews;
delete from silver.sellers;

delete from gold.dim_customers;
delete from gold.fact_orders;
delete from gold.dim_products;
delete from gold.dim_sellers;
delete from gold.status_payments;

delete from rejected_customers;
delete from rejected_order_items;
delete from rejected_orders;
delete from rejected_payments;
delete from rejected_products;
delete from rejected_reviews;
delete from rejected_sellers;



select * from gold.dim_sellers where seller_id='3442f8959a84dea7ee197c632cb2df15'
select * from gold.dim_products where product_id='1e9e8ef04dbcff4541ed26657ea517e5'
select * from gold.dim_products where is_delete=1
select * from gold.dim_sellers where is_delete=1
select * from gold.dim_products where end_date is not null
