
import os
import asyncio
import logging
from dotenv import load_dotenv

from database import PostgresDatabase


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

CURRENT_DIR = os.path.dirname(__file__)
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)


async def create():
    db = PostgresDatabase(
        host="localhost",
        port=5432,
        database="postgres",
        user="admin",
        password="admin",
    )
    await db.connect()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR(100)
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        product_name VARCHAR(100),
        product_description TEXT,
        category_id INT,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS classroom (
        classroom_id SERIAL PRIMARY KEY,
        classroom_name VARCHAR(100) NOT NULL
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS student (
        student_id SERIAL PRIMARY KEY,
        student_name VARCHAR(100) NOT NULL,
        classroom_id INT,
        FOREIGN KEY (classroom_id) REFERENCES classroom(classroom_id)
    );
    """)

    await db.execute("""
    CREATE TABLE purchases (
        purchase_id SERIAL PRIMARY KEY,
        student_id INT,
        product_id INT,
        FOREIGN KEY (student_id) REFERENCES student(student_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    await db.disconnect()


async def insert():
    db = PostgresDatabase(
        host="localhost",
        port=5432,
        database="postgres",
        user="admin",
        password="admin",
    )
    await db.connect()

    await db.execute("""
    INSERT INTO categories (category_name) VALUES
        ('Books'),
        ('Electronics'),
        ('Furniture'),
        ('Stationery'),
        ('Apparel'),
        ('Accessories'),
        ('Loans');
    """)

    await db.execute("""
    INSERT INTO products (product_name, product_description, category_id) VALUES
        ('book', 'A book for students', 1),
        ('laptop', 'A laptop for students', 2),
        ('tablet', 'A tablet for students', 2),
        ('pen', 'A pen for students', 4),
        ('desk', 'A desk for students', 3),
        ('chair', 'A chair for students', 3),
        ('backpack', 'A backpack for students', 6),
        ('planner', 'A planner for students', 4),
        ('notebook', 'A notebook for students', 4),
        ('calculator', 'A calculator for students', 2),
        ('uniform', 'A uniform for students', 5),
        ('shoes', 'Shoes for students', 5),
        ('jacket', 'A jacket for students', 5),
        ('hat', 'A hat for students', 5),
        ('water bottle', 'A water bottle for students', 6),
        ('student ID holder', 'An ID holder for students', 6),
        ('lamp', 'A lamp for students', 3),
        ('art supplies', 'Art supplies for students', 4),
        ('student lunchbox', 'A lunchbox for students', 6),
        ('student loans', 'Loans for students', 7);
    """)

    await db.execute("""
    INSERT INTO classroom (classroom_name) VALUES
        ('Classroom A'),
        ('Classroom B'),
        ('Classroom C');
    """)

    await db.execute("""
    INSERT INTO student (student_name, classroom_id) VALUES
        ('John Doe', 1),
        ('Jane Smith', 2),
        ('Alice Johnson', 1),
        ('Bob Brown', 3),
        ('Charlie Davis', 2);
    """)

    await db.execute("""
    INSERT INTO purchases (student_id, product_id) VALUES
        (1, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (5, 6);
    """)


if __name__ == "__main__":
    #asyncio.run(create())
    asyncio.run(insert())