from sqlalchemy import text
import re
from .openai_api import client

def extract_sql_query(user_query):
    """
    Uses OpenAI API to transform a natural language query into an SQL query.

    Args:
        user_query (str): The user's natural language query.

    Returns:
        str: The generated SQL query.
    """

    base_prompt = f"""Can you create a SQL query from this natural language: '{user_query}'?
    IMPORTANT: Ensure the SQL query is compatible with SQLite and ONLY provide the SQL command without any explanations.
    For more context, here is my SQL database schema:
    1. Table 'companies' contains columns:
        `id`|INTEGER|1||1,
        `company_logo_url`|VARCHAR|0||0,
        `company_logo_text`|VARCHAR|0||0,
        `company_name`|VARCHAR|0||0 (e.g. BBGC, HR Maritime, HR Maritime Consultants Ltd),
        `relation_to_event`|VARCHAR|0||0 (e.g. partner, sponsor, partner, exhibitor, associate),
        `event_url`|VARCHAR|0||0,
        `company_revenue`|VARCHAR|0||0 (e.g. $2 million, $6 million, $12 million, $355 million),
        `n_employees`|VARCHAR|0||0 (e.g. 11-50, 114.0),
        `company_phone`|VARCHAR|0||0 (e.g. +41 22 732 57 00, (656) 333-8530),
        `company_founding_year`|FLOAT|0||0 (e.g. 2008.0, 2005.0),
        `company_address`|VARCHAR|0||0 (e.g. 'Rue Adrien-Lachenal 20, Geneva, Geneva 1207, CH'),
        `company_industry`|VARCHAR|0||0 (e.g. Financial Services, IT Services and IT Consulting, Maritime Transportation),
        `company_overview`|VARCHAR|0||0,
        `homepage_url`|VARCHAR|0||0,
        `linkedin_company_url`|VARCHAR|0||0,
        `homepage_base_url`|VARCHAR|0||0,
        `company_logo_url_on_event_page`|VARCHAR|0||0,
        `company_logo_match_flag`|VARCHAR|0||0 (e.g. yes, no).

    2. Table 'events' contains columns:
        `id`|INTEGER|1||1,
        `event_logo_url`|VARCHAR|0||0,
        `event_name`|VARCHAR|0||0 (e.g. AHICE South East Asia, Commodity Trading Week APAC),
        `event_start_date`|DATE|0||0 (e.g. 2024-07-06, 2025-02-25, 2025-02-25)
        `event_end_date`|DATE|0||0 (e.g. 2024-07-06, 2025-02-26, 2025-02-26),
        `event_venue`|VARCHAR|0||0 (e.g. Pan Pacific Singapore, Marina Bay Sands, Canton Fair Complex Guangzhou),
        `event_country`|VARCHAR|0||0 (e.g. 'Singapore', 'Australia', 'Maryland, USA'),
        `event_description`|VARCHAR|0||0,
        `event_url`|VARCHAR|0||0 .
        Each `event_url` corresponds to a unique event.

    3. Table 'people' contains columns:
        `id`|INTEGER|1||1,
        `first_name`|VARCHAR|0||0 (e.g. 'Cynthia', 'Alexander', 'Nadir'),
        `middle_name`|VARCHAR|0||0
        `last_name`|VARCHAR|0||0 (e.g. 'Battini', 'McClure', 'Shaari'),
        `job_title`|VARCHAR|0||0 (e.g. Indirect Buyer, Public Relations, SEO Junior Account Manager),
        `person_city`|VARCHAR|0||0 (e.g. Rutland, Paris, Minneapolis),
        `person_state`|VARCHAR|0||0 (e.g. MN, TN, TX),
        `person_country`|VARCHAR|0||0 (e.g. France, US, GB),
        `email_address`|VARCHAR|0||0 (e.g. nkushwa@digitalrealty.com, lyssm@knowbe4.com),
        `homepage_base_url`|VARCHAR|0||0
        `duration_in_current_job`|VARCHAR|0||0 (e.g. '4 years 2 months in role 4 years 2 months in company'),
        `duration_in_current_company`|VARCHAR|0||0 (e.g. '4 years 2 months').
        Each `homepage_base_url` can be interpreted as a unique company.

    Table 'people' has a foreign key relationship with table 'companies' referencing column 'homepage_base_url'."""

    messages = [
        {"role": "system", "content": "You are an SQL expert. Generate precise SQLite-compatible queries based on natural language inputs."},
        {"role": "user", "content": base_prompt}
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    sql_query = completion.choices[0].message.content.strip().strip('```sql').strip('```')

    return sql_query

def convert_data_to_natural_language(data, user_query):
    """
    Uses OpenAI API to convert data into a natural language response.

    Args:
        data (list): The fetched data from the database.
        user_query (str): The user's natural language query.

    Returns:
        str: The natural language response.
    """
    if not data:
        return "I'm sorry, but there's no data available for the given query."
    
    max_results = 25  # Limit the number of rows to display
    limited_data = data[:max_results]
    data_str = "\n".join([str(row) for row in limited_data])
    additional_info = "" if len(data) <= max_results else f"\nAnd {len(data) - max_results} more rows not displayed."

    prompt = f"The user asked: '{user_query}'. Here is the data retrieved from the database: {data_str}.{additional_info} Please provide a natural language response summarizing this data."
    
    messages = [
        {"role": "system", "content": "Act as the user is asking to you, so answer the user directly what they asked."},
        {"role": "user", "content": prompt}
        ]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    natural_language_response = completion.choices[0].message.content.strip()

    return natural_language_response

def extract_tables_and_columns(sql_query):
    tables = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', sql_query, re.IGNORECASE)
    tables = [table[0] or table[1] for table in tables]
    columns = re.findall(r'WHERE\s+(\w+\.\w+)|ON\s+(\w+\.\w+)', sql_query, re.IGNORECASE)
    columns = [col[0] or col[1] for col in columns]
    return list(set(tables)), list(set(columns))

def get_column_data(db, table_name, column_name):
    query = f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL AND {column_name} != ''"
    result = db.execute(text(query))
    return [row[0] for row in result]

def get_table_columns(db, table_name):
    query = f"PRAGMA table_info({table_name})"
    result = db.execute(text(query))
    return [row[1] for row in result]

def refine_sql_query_with_data(user_query, original_sql, error_message, db, attempt):
    tables, columns = extract_tables_and_columns(original_sql)
    
    sample_data = {}
    if attempt == 1:
        for table in tables:
            for column in columns:
                if column.startswith(f"{table}."):
                    col_name = column.split('.')[1]
                    data = get_column_data(db, table, col_name)
                    if data:
                        sample_data[f"{table}.{col_name}"] = ", ".join(f"'{value}'" for value in data[:20])
    elif attempt == 2:
        for table in tables:
            table_columns = get_table_columns(db, table)
            for col in table_columns:
                data = get_column_data(db, table, col)
                if data:
                    sample_data[f"{table}.{col}"] = ", ".join(f"'{value}'" for value in data[:20])
    else:
        all_tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        for table in all_tables:
            table_name = table[0]
            table_columns = get_table_columns(db, table_name)
            for col in table_columns:
                data = get_column_data(db, table_name, col)
                if data:
                    sample_data[f"{table_name}.{col}"] = ", ".join(f"'{value}'" for value in data[:10])

    sample_data_str = "\n".join([f"{k}: {v}" for k, v in sample_data.items()])

    refine_prompt = f"""
    The original query "{user_query}" produced this SQL:
    {original_sql}
    
    This query returned no results or produced an error: {error_message}
    
    In my SQL Database, we have schema:
    1. Table 'companies' contains columns: id, company_logo_url, company_logo_text, company_name, relation_to_event (e.g. partner, sponsor, partner, exhibitor, associate), event_url, company_revenue (e.g. $2 million, $6 million, $12 million), n_employees (e.g. 11-50, 114.0), company_phone (e.g. +41 22 732 57 00, (656) 333-8530), company_founding_year (e.g. 2008.0, 2011.0), company_address (e.g. 'Rue Adrien-Lachenal 20, Geneva, Geneva 1207, CH'), company_industry (e.g. Financial Services, IT Services and IT Consulting, Maritime Transportation, Maritime), company_overview, homepage_url, linkedin_company_url, homepage_base_url, company_logo_url_on_event_page, company_logo_match_flag.
    2. Table 'events' contains columns: id, event_logo_url, event_name (e.g. World University Expo @ SUNTEC, AHICE South East Asia, Commodity Trading Week APAC), event_start_date (e.g. 2024-07-06, 2025-02-25, 2025-02-25), event_end_date (e.g. 2024-07-06, 2025-02-26, 2025-02-26), event_venue (e.g. SUNTEC Convention Centre, Pan Pacific Singapore, Marina Bay Sands), event_country (e.g. 'Singapore', 'Australia', 'Maryland, USA'), event_description, event_url.
    3. Table 'people' contains columns: id, first_name (e.g. 'Cynthia', 'Alexander', 'Nadir'), middle_name, last_name (e.g. 'Battini', 'McClure', 'Shaari'), job_title (e.g. Indirect Buyer, Public Relations, SEO Junior Account Manager), person_city (e.g. Rutland, Paris, Minneapolis), person_state (e.g. MN, TN, TX), person_country (e.g. France, US, GB), email_address (e.g. nkushwa@digitalrealty.com, lyssm@knowbe4.com), homepage_base_url, duration_in_current_job (e.g. '4 years 2 months in role 4 years 2 months in company'), duration_in_current_company (e.g. '4 years 2 months').

    Here is a sample of data from relevant columns:
    {sample_data_str}

    Please refine the SQL query to be more accurate based on this sample data.
    Ensure it's compatible with SQLite and only provide the SQL command, only provide the SQL command without any explanations.
    Consider all available tables and columns to best answer the user's query.
    """

    messages = [
        {"role": "system", "content": "You are an SQL expert. Refine and correct SQL queries to ensure they produce results."},
        {"role": "user", "content": refine_prompt}
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )
    refined_sql = completion.choices[0].message.content.strip().strip('```sql').strip('```')
    print(f"Refined SQL Query: {refined_sql}")

    return refined_sql