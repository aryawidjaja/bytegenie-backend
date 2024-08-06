from flask_restful import Resource, reqparse
from sqlalchemy import text
from ..database import get_db
from .utils import extract_sql_query, refine_sql_query_with_data, convert_data_to_natural_language
import time

class QueryResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True, help="Query cannot be blank!")
        args = parser.parse_args()

        user_query = args['query']
        print(f"Original Query: {user_query}")

        max_retries = 5
        delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    sql_query = extract_sql_query(user_query)
                else:
                    with get_db() as db:
                        sql_query = refine_sql_query_with_data(user_query, sql_query, "No valid results returned", db, attempt)
                print(f"Generated SQL Query: {sql_query}")
                
                if not sql_query:
                    return {"error": "Failed to generate a valid SQL query"}, 400
                
                with get_db() as db:
                    result = db.execute(text(sql_query))
                    data = result.fetchall()
                    columns = result.keys()
                    print(f"Retrieved data: {data}")

                if any(row != (None,) for row in data):
                    break
                else:
                    print(f"No valid data retrieved. Attempt {attempt + 1} of {max_retries}. Refining query...")
                    time.sleep(delay)
            except Exception as e:
                print(f"Error: {e}")
                if attempt < max_retries - 1:
                    print("Refining query...")
                    time.sleep(delay)
                else:
                    raise
        
        if not any(row != (None,) for row in data):
            return {"error": "Could not find any relevant data, please provide more detailed prompt."}, 500

        data = [{k: v for k, v in zip(columns, row) if v is not None} for row in data if row != (None,)]
        
        natural_language_response = convert_data_to_natural_language(data, user_query)
        
        return {"response": natural_language_response}
