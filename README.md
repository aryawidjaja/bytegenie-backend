# ByteGenie Test - Backend API 🤖

## Overview

This API uses OpenAI's GPT-3.5-turbo-1106 to turn natural language questions into SQL queries, run those queries on a SQLite database, and then translate the results back into plain English. The goal is to let you ask questions about your data in a super easy way.

## Main Functionalities of the API

1. **Natural Language Query Processing**:
   - Takes your questions in plain English and turns them into SQL queries with the help of OpenAI's GPT-3.5-turbo-1106.
   - Runs those SQL queries on my SQLite database.
   - Turns the results back into natural language so you can understand them.

2. **Sample Data Provision**:
   - To make sure the SQL queries are accurate, I give the model some sample data and schema info.
   - This helps the model understand the structure of the database and generate better queries.

## Why GPT-3.5-turbo-1106?

I chose to use GPT-3.5-turbo-1106 because it's low cost and fast enough for my needs. It provides a good balance between performance and cost, making it ideal for processing and generating SQL queries quickly and accurately. Plus, I'm familiar with it and know how to get the best out of its capabilities for my task.

## Handling User Queries

1. **Extract SQL Query**:
   - I use OpenAI to convert what you ask into a SQL query.
   - The model gets some sample data and schema info to help it generate a more accurate SQL query.

2. **Execute SQL Query**:
   - The SQL query gets run on my SQLite database.
   - If it doesn't work the first time, the API tweaks the query and tries again.

3. **Convert to Natural Language Response**:
   - I take the results of the SQL query and turn them back into plain English using OpenAI.
   - If there are a lot of results, I just show you the first few so you don't get overwhelmed.

## Key Challenges

1. **Accuracy of SQL Queries**:
   - Making sure the generated SQL queries work with SQLite and give the right results.
   - Handling cases where the initial query doesn't work and tweaking it to get better results.

2. **Data Understanding**:
   - Giving the model enough context and sample data so it understands the database schema and can generate accurate queries.

3. **Scalability**:
   - Managing complex SQL queries within the limits of a lightweight SQLite database.

## Potential Improvements

1. **Enhanced Data Validation**:
   - Adding better validation and error-handling for user queries and SQL execution.

2. **Advanced Query Optimization**:
   - Using smarter techniques to optimize SQL queries based on past data and patterns.

3. **Scalability and Performance**:
   - Maybe looking at more scalable database options if the data gets bigger or the query volume increases.

4. **Learning the Data**:
   - Right now, sometimes the model doesn't quite get the data and generates incorrect SQL queries. If I had more time, I could develop an algorithm for the model to learn the data first, which would make the SQL generation more accurate.

## How to Get Started

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/aryawidjaja/bytegenie-backend.git
   cd bytegenie-backend
   ```

2. **Setup Virtual Environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Create a `.env` File**:
   Create a .env file in the root of the project and add your OpenAI API key:
   ```makefile
   OPENAI_API_KEY="your-openai-api-key"
   ```

4. **Initialize the Database**:
Ensure your SQLite database is set up. If you don't have a database yet, initialize it using your database setup script from another repo.

5. **Run the Application**:
   ```sh
   flask run
   ```
6. **Send Queries to the API**:
   - Use tools like Postman or curl to send POST requests to http://127.0.0.1:5000/query with a JSON body containing your natural language query.

## Example Query

To find salespeople for companies attending events in Singapore over the next 5 months, you can use the following curl command:

```sh
curl -X POST -H "Content-Type: application/json" -d '{"query": "Who are the salespeople for companies that are attending events in Singapore for the next 5 months"}' http://127.0.0.1:5000/query
```
