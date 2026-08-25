-- reviews
use Atos;
Go

                    --- reveiws table ----
-- pk
select * from bronze.reviews
where review_id is null

-- may be two tables have same review_id
select review_id, count(*) as cnt
from bronze.reviews
group by review_id
having count(*)>1

select * from bronze.reviews
where review_id='d23bba9a2f1d16e5505a02e5968c1e68'

select * from bronze.orders
where order_id='360b84029c125bb8d4ede52585f058f2'


select review_id, count(*) as cnt
from bronze.reviews
where len(review_id) <>32
group by review_id

---reference
select * from bronze.reviews r left join bronze.orders o 
on r.order_id = o.order_id 
where o.order_id is null
-- review_score
select * from bronze.reviews
where review_score <0
-- 
select * from bronze.reviews
where review_score is null

-- creation_date
select * from bronze.reviews
where review_creation_date is null

-- review_answer_timestamp && review_creation_date >> month/day/year 
-- convert to day/month/year
-- taken time to respond=review_answer_timestamp-review_creation_date

                        --- customers table ----

select * from bronze.customers
where customer_id is null

select customer_id,count(*) from bronze.customers
group by customer_id
having count(*)>1


            -- drop customer unique id column as we use customer_id as pk
select customer_id,customer_unique_id,count(*) from bronze.customers
group by customer_id, customer_unique_id
having count(*)>1

select * from bronze.customers
where len(customer_id) <>32  

select * from bronze.customers
where customer_id like '%[^a-z0-9]%'

-- bad reference in customers table for geolocation table
select * from bronze.customers c left join bronze.geolocation g
on c.customer_zip_code_prefix = g.geolocation_zip_code_prefix
where g.geolocation_zip_code_prefix is null

-- customer_state??

                                  --- orders table ----
select * from bronze.orders
where order_id is null


select * from bronze.orders
where order_id like '%[^a-z0-9]%'

select * from bronze.orders
where customer_id is null

select * from bronze.orders o left join bronze.customers c
on o.customer_id = c.customer_id
where c.customer_id is null

select * from bronze.orders
where len(customer_id) <>32  

select * from bronze.orders
where len(order_id) <>32  

--- order status column ----
select order_status, count(*) from bronze.orders
group by order_status
-- approved
-- delivered
-- created
-- invoiced
-- processing
-- unavailable
-- canceled
-- shipped

select order_status from bronze.orders
where order_status is null

select 
    order_purchase_timestamp,
    order_approved_at, 
    order_delivered_carrier_date, 
    order_delivered_customer_date, 
    order_estimated_delivery_date from bronze.orders
where order_purchase_timestamp is null or order_approved_at is null or order_delivered_carrier_date is null or order_delivered_customer_date is null or order_estimated_delivery_date is null

-- order_estimated_delivery_date > order_delivered_customer_date --->> late expectaions
-- taken time to deliver=order_delivered_customer_date - order_purchase_timestamp
-- taken time to approve=order_approved_at - order_purchase_timestamp
-- taken time to carrier=order_delivered_carrier_date - order_approved_at

SELECT
    SUM(CASE WHEN order_purchase_timestamp IS NULL THEN 1 ELSE 0 END) AS purchase_timestamp_nulls,
    SUM(CASE WHEN order_approved_at IS NULL THEN 1 ELSE 0 END) AS approved_at_nulls,
    SUM(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 ELSE 0 END) AS delivered_carrier_nulls,
    SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS delivered_customer_nulls,
    SUM(CASE WHEN order_estimated_delivery_date IS NULL THEN 1 ELSE 0 END) AS estimated_delivery_nulls
FROM bronze.orders;

            --- normal nulls ---

--- 146  order_approved_at-->order_delivered_carrier_date-->order_delivered_customer_date
SELECT
    count(*) AS total_orders
FROM bronze.orders
where order_approved_at is null and order_delivered_carrier_date is null and order_delivered_customer_date is null 

-- 1636
SELECT
    count(*) AS total_orders
FROM bronze.orders
where order_approved_at is not null and order_delivered_carrier_date is null and order_delivered_customer_date is null 

-- 1183
SELECT
   *
FROM bronze.orders
where order_approved_at is not null and order_delivered_carrier_date is not null and order_delivered_customer_date is null

        -- unexpected nulls ---

SELECT
    count(*) AS total_orders
FROM bronze.orders
where order_purchase_timestamp is null and  order_approved_at is not null and order_delivered_carrier_date is not null and order_delivered_customer_date is not null 

        -- 14 orders are missing order_approved_at but have order_delivered_carrier_date and order_delivered_customer_date

SELECT
    *
FROM bronze.orders
where order_approved_at is null and order_delivered_carrier_date is not null and order_delivered_customer_date is not null 
        --- I noticed that approved_at at the same day but different hours from order_purchase_timestamp
        --- we handle missing values by using the same day of purchase_timestamp + avg(order_approved_at - order_purchase_timestamp as minutes) 


SELECT
    *  
FROM bronze.orders
where order_approved_at is not null and order_delivered_carrier_date is null and order_delivered_customer_date is not null 

    
        -- 1 order is missing order_delivered_carrier_date but has order_approved_at and order_delivered_customer_date
        -- we handle missing values by using the same day of purchase_timestamp + avg(order_delivered_carrier_date - order_approved_at as days)


                        --- payments table ----
select order_id,count(*) from bronze.payments
group by order_id
having count(*)>1

select * from bronze.payments
where order_id='9b75fa68354ea9cd02695d002b82b109'

select * from  bronze.order_items 
where order_items.order_id ='9b75fa68354ea9cd02695d002b82b109'

--- for each order_id, the sum of payment_value(payment table) should be equal to the sum of price+freight_value in order_items

select payment_type ,count(*) from bronze.payments
group by payment_type

select * from bronze.payments p left join silver.orders o
on  p.order_id=o.order_id
where o.order_id is null

select * from bronze.payments
    where payment_type='not_defined'
-- drop not_defined rows as payment_value is zero and they don't have any order

select * from  bronze.orders 
where orders.order_id ='00b1cb0320190ca0daa2c88b35206009'

select * from  bronze.order_items 
where order_items.order_id ='4637ca194b6387e2d538dc89b124b0ee'

-- run above three queries and to remember to drop any row of orders contains order_id, order_delivered_customer_date, and order_delivered_carrier_date is null

                        --- order_items table ----
select * from bronze.order_items
where order_id is null

select * from bronze.order_items
where order_item_id is null

select order_id,count(*) from bronze.order_items
GROUP by  order_id
having count(*)>1


select order_id,count(*) from bronze.order_items
GROUP by order_id
having count(*)>1

select * from bronze.order_items where order_id='00143d0f86d6fbd9f9b38ab440ac16f5'


select * from bronze.order_items i left join bronze.orders o
on i.order_id = o.order_id
where o.order_id is null

select * from bronze.order_items i left join bronze.products p
on i.product_id = p.product_id
where p.product_id is null

--- bad reference here ----
select * from bronze.order_items i left join bronze.sellers s
on i.seller_id = s.seller_id
where s.seller_id is null

select * from bronze.order_items
where price <0 or freight_value <0

select * from bronze.order_items
where shipping_limit_date is null


                        -- sellers table ----
select * from bronze.sellers
where seller_id is null

select seller_id,count(*) from bronze.sellers
group by seller_id
having count(*)>1

-- invalid references in sellers table
select * from bronze.sellers s left join bronze.geolocation g
on s.seller_zip_code_prefix = g.geolocation_zip_code_prefix
where g.geolocation_zip_code_prefix is null

-- seller_state?? convert??

                    --- geolocation table ----
select * from bronze.geolocation
where geolocation_zip_code_prefix is null


select geolocation_zip_code_prefix,count(*)
from bronze.geolocations
group by geolocation_zip_code_prefix

select COUNT(*) from bronze.geolocation
where geolocation_lng is null

select COUNT(*) from bronze.geolocation
where geolocation_lat is null

-- geolocation_state?? convert??

                    -- products table ----
                    
select * from bronze.products
where product_id is null

-- mapping product_category_name_translation table with products table to get product_category_name_english
-- check product_weight_g, product_length_cm, product_height_cm, product_width_cm are positive values