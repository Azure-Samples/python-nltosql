import logging

from string import Template
from aistudio_requests.generate import PromptGenerator
from interfaces import QueryTemplate, ComplexQueryTemplate, TableToNaturalTemplate


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class QueryGenerator(PromptGenerator):

    async def retrieve_context(self) -> str:
        return ""

    async def retrieve_history(self) -> str:
        return ""

    async def prepare_request(
        self,
        prompt_template: QueryTemplate
    ):
        """
        Asynchronously prepares a database query request using the provided parameters. This method
        formats a query string that is tailored to interact with Azure OpenAI Service by substituting
        placeholders in a template with the actual values from the arguments. It handles various
        database-related parameters to generate a meaningful and contextually relevant query based on
        the prompt and type of query requested.

        Args:
            prompt (str): The base prompt text that forms the foundation of the query.
            query_type (str): Specifies the type of query to generate, influencing the structure of the query.
            db_params (Dict[str, Union[str, List[str]]]): A dictionary containing parameters related to the
                database query, such as database name, table name, and fields. These parameters are used to
                dynamically construct the query based on database-specific requirements.
            programming_language (Optional[str]): An optional parameter that specifies the programming language
                context for the query. This can be used to tailor the query for specific programming environments
                or syntaxes.

        Returns:
            str: A fully constructed query string ready to be sent to the Azure OpenAI Service. This string is
                formatted based on the provided prompt, query type, database parameters, and optional programming
                language.

        Raises:
            ValueError: If essential database parameters like database name or table name are missing
                in `db_params`.
        """

        query_request = "$prompt using $query_type."

        if not all(key in prompt_template.db_params for key in ["database_name", "table_name"]):
            logger.error(
                "Could not find database_name and table_name in db_params. Found: %s",
                set(prompt_template.db_params.keys()),
            )
            raise ValueError("The database name and table name are required to generate a query.")

        query_request += " The database name is $database_name, the table is $table_name"

        match prompt_template.db_params.get("fields", None):
            case str():
                query_request += " and the field is $field."
            case list():
                query_request += " and the fields are $fields."
            case _:
                logger.error(
                    "Could not find fields. Found: %s",
                    type(prompt_template.db_params.get("fields", None)),
                )

        if prompt_template.programming_language:
            query_request += " The programming language is $programming_language."

        query_request = Template(query_request).safe_substitute(
            prompt=prompt_template.prompt,
            query_type=prompt_template.query_type,
            programming_language=prompt_template.programming_language,
            **prompt_template.db_params,
        )
        return query_request


class ComplexQueryGenerator(PromptGenerator):

    async def retrieve_context(self) -> str:
        return ""

    async def retrieve_history(self) -> str:
        return ""

    async def prepare_request(
        self,
        prompt_template: ComplexQueryTemplate
    ):
        """
        Asynchronously prepares a database query request using the provided parameters. This method
        formats a query string that is tailored to interact with Azure OpenAI Service by substituting
        placeholders in a template with the actual values from the arguments. It handles various
        database-related parameters to generate a meaningful and contextually relevant query based on
        the prompt and type of query requested.

        Args:
            prompt (str): The base prompt text that forms the foundation of the query.
            query_type (str): Specifies the type of query to generate, influencing the structure of the query.
            db_params (Dict[str, Union[str, List[str]]]): A dictionary containing parameters related to the
                database query, such as database name, table name, and fields. These parameters are used to
                dynamically construct the query based on database-specific requirements.
            programming_language (Optional[str]): An optional parameter that specifies the programming language
                context for the query. This can be used to tailor the query for specific programming environments
                or syntaxes.

        Returns:
            str: A fully constructed query string ready to be sent to the Azure OpenAI Service. This string is
                formatted based on the provided prompt, query type, database parameters, and optional programming
                language.

        Raises:
            ValueError: If essential database parameters like database name or table name are missing
                in `db_params`.
        """

        query_request = "$prompt using $query_type."

        if not all(key in prompt_template.db_params for key in ["database_name", "table_name"]):
            logger.error(
                "Could not find database_name and table_name in db_params. Found: %s",
                set(prompt_template.db_params.keys()),
            )
            raise ValueError("The database name, schema and table name are required to generate a query.")

        query_request += " The database name is $database_name, the table is $table_name"

        match prompt_template.db_params.get("fields", None):
            case str():
                query_request += " and the field is $field."
            case list():
                query_request += " and the fields are $fields."
            case _:
                logger.error(
                    "Could not find fields. Found: %s",
                    type(prompt_template.db_params.get("fields", None)),
                )
        if not prompt_template.db_mapping:
            logger.error("Could not find db_mapping in db_params. Found: %s", prompt_template.db_mapping)
            raise ValueError("The database mapping is required to generate a query.")

        query_request += " The database schema is $db_mapping."

        if prompt_template.programming_language:
            query_request += " The programming language is $programming_language."

        query_request = Template(query_request).safe_substitute(
            prompt=prompt_template.prompt,
            query_type=prompt_template.query_type,
            programming_language=prompt_template.programming_language,
            db_mapping=prompt_template.db_mapping,
            **prompt_template.db_params,
        )
        return query_request


class TableToNaturalGenerator(PromptGenerator):

    async def retrieve_context(self) -> str:
        return ""

    async def retrieve_history(self) -> str:
        return ""

    async def prepare_request(
        self,
        prompt_template: TableToNaturalTemplate
    ):
        """
        Asynchronously prepares a database query request using the provided parameters. This method
        formats a query string that is tailored to interact with Azure OpenAI Service by substituting
        placeholders in a template with the actual values from the arguments. It handles various
        database-related parameters to generate a meaningful and contextually relevant query based on
        the prompt and type of query requested.

        Args:
            prompt (str): The base prompt text that forms the foundation of the query.
            query_type (str): Specifies the type of query to generate, influencing the structure of the query.
            db_params (Dict[str, Union[str, List[str]]]): A dictionary containing parameters related to the
                database query, such as database name, table name, and fields. These parameters are used to
                dynamically construct the query based on database-specific requirements.
            programming_language (Optional[str]): An optional parameter that specifies the programming language
                context for the query. This can be used to tailor the query for specific programming environments
                or syntaxes.

        Returns:
            str: A fully constructed query string ready to be sent to the Azure OpenAI Service. This string is
                formatted based on the provided prompt, query type, database parameters, and optional programming
                language.

        Raises:
            ValueError: If essential database parameters like database name or table name are missing
                in `db_params`.
        """

        query_request = """
            Considering the data
            DATA:\n$data\n
            and the original question
            ORIGINAL QUESTION:\n$original_prompt\n
            DO:\n$prompt
        """

        query_request = Template(query_request).safe_substitute(
            prompt=prompt_template.prompt,
            data=prompt_template.data,
            original_prompt=prompt_template.original_prompt
        )

        return query_request
