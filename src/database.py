import asyncpg


class PostgresDatabase:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    async def connect(self):
        self.connection = await asyncpg.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

    async def disconnect(self):
        if self.connection is None:
            raise ValueError("Database connection is closed")
        await self.connection.close()

    async def execute(self, query, *args):
        if self.connection is None:
            raise ValueError("Database connection is closed")
        return await self.connection.execute(query, *args)

    async def fetch(self, query, *args):
        if self.connection is None:
            raise ValueError("Database connection is closed")
        return await self.connection.fetch(query, *args)


async def get_schema(db):
    schema_dict = {}

    tables = await db.fetch('''
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ''')

    for table in tables:
        table_name = table['table_name']
        columns = await db.fetch('''
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = $1
        ''', table_name)
        
        foreign_keys = await db.fetch('''
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = $1
        ''', table_name)

        for col in columns:
            column_name = f"Column name: {col['column_name']}"
            data_type = f"Data Type: {col['data_type']}"
            fk_info = next((fk for fk in foreign_keys if fk['column_name'] == column_name), None)
            foreign_key_to = f"foreign key to {fk_info['foreign_table_name']} through {fk_info['foreign_column_name']}" if fk_info else None
            schema_dict[column_name] = str([f"Table Name: {table_name}", data_type, foreign_key_to])

    return schema_dict
