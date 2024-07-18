
import os
import asyncio
import logging
from dotenv import load_dotenv

from llms import QueryGenerator, ComplexQueryGenerator, TableToNaturalGenerator
from interfaces import QueryTemplate, ComplexQueryTemplate, TableToNaturalTemplate
from database import PostgresDatabase, get_schema
from prompts import QUERY_SYSTEM_MESSAGE, ANALYSIS_SYSTEM_MESSAGE


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

CURRENT_DIR = os.path.dirname(__file__)
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)


class ChatWithSQLHook:

    @staticmethod
    async def test_query_generator():
        url: str = os.environ.get("GPT4V_URL", "")
        key: str = os.environ.get("GPT4V_KEY", "")
        az_monitor: str = os.environ.get("AZ_CONNECTION_LOG", "")

        query_generator = QueryGenerator(aistudio_url=url, aistudio_key=key)
        complex_query_generator = ComplexQueryGenerator(aistudio_url=url, aistudio_key=key)
        table_to_natural_generator = TableToNaturalGenerator(aistudio_url=url, aistudio_key=key)
        database_engine = PostgresDatabase(
            host="localhost",
            port=5432,
            database="postgres",
            user="admin",
            password="admin",
        )
        await database_engine.connect()
        database_schema = await get_schema(database_engine)

        query_generator.system_message = QUERY_SYSTEM_MESSAGE
        complex_query_generator.system_message = QUERY_SYSTEM_MESSAGE
        table_to_natural_generator.system_message = ANALYSIS_SYSTEM_MESSAGE
        # query_generator = QueryGenerator(aoai_url=url, aoai_key=key, az_monitor=az_monitor) // If want to enable azure monitor logs

        query_schema = QueryTemplate(
            prompt = "Retrieve the information from all products that contains the name 'student' but are not 'student loans'.",
            query_type = "Postgres",
            programming_language = "SQL",
            db_params = {
                "database_name": "postgres",
                "table_name": "products",
                "fields": ["product_name", "product_description"],
            }
        )

        complex_schema = ComplexQueryTemplate(
            prompt = "Retrieve the name from all categories which had products where sold for students on classroom 2.",
            query_type = "Postgres",
            programming_language = "SQL",
            db_params = {
                "database_name": "postgres",
                "table_name": "categories",
                "fields": ["category_name"],
            },
            db_mapping = database_schema,
        )

        parameters = {
            "temperature": 0.0,
            "top_p": 0.95,
            "max_tokens": 2000,
        }

        query_response = await query_generator.send_request(query_schema, parameters)  # type: ignore
        assert isinstance(query_response, str)
        print(query_response)

        database_response = await database_engine.fetch(query_response)
        print([dict(record) for record in database_response])

        simple_table_schema = TableToNaturalTemplate(
            prompt = "Explain the data in the following data, considering the original question provided.",
            data = str([dict(record) for record in database_response]),
            original_prompt=query_schema.prompt,
        )
        simple_analysis = await table_to_natural_generator.send_request(simple_table_schema, parameters)

        complex_query_response = await complex_query_generator.send_request(complex_schema, parameters)  # type: ignore
        assert isinstance(complex_query_response, str)
        print(complex_query_response)
    
        complex_response = await database_engine.fetch(complex_query_response)
        print([dict(record) for record in complex_response])

        complex_table_schema = TableToNaturalTemplate(
            prompt = "Evaluate if the dasta provided is sufficient to answer the user original question.",
            data = str([dict(record) for record in complex_response]),
            original_prompt=complex_schema.prompt
        )
        complex_analysis = await table_to_natural_generator.send_request(complex_table_schema, parameters)
        
        return f"\n\n**SIMPLE ANALYSIS**:\n{simple_analysis},\n\n**COMPLEX ANALYSIS**:\n{complex_analysis}"


if __name__ == "__main__":
    hook = ChatWithSQLHook()
    analysis = asyncio.run(hook.test_query_generator())
    print(analysis)
