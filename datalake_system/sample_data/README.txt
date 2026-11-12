SAMPLE DATA FILES FOR DATA LAKE PROJECT

Files included:
1. sales_data.csv - 100 sales transactions
2. customers.json - 50 customer records
3. website_logs.csv - 200 website logs
4. products.json - 30 product records

HOW TO USE IN THE DATA LAKE PROJECT:
1. Login to the Data Lake System
2. Create an S3 bucket
3. Upload these files
4. Run Glue Crawler
5. Execute Athena queries

Sample Queries:
----------------
1. Total sales by region:
   SELECT region, SUM(total_amount) as total_sales 
   FROM sales_data 
   GROUP BY region

2. Top customers:
   SELECT customer_id, SUM(total_amount) as total_spent
   FROM sales_data 
   GROUP BY customer_id 
   ORDER BY total_spent DESC 
   LIMIT 10

3. Website traffic analysis:
   SELECT browser, COUNT(*) as visits
   FROM website_logs 
   GROUP BY browser

4. Product analysis:
   SELECT category, AVG(price) as avg_price
   FROM products 
   GROUP BY category
