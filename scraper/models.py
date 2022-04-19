import pymysql
from pymysql.err import OperationalError
if __name__ == "__main__":
    from utils import traceback
else:
    from .utils import traceback

DATABASE_NAME = "linkedin_webscraper"


def create_db(database_name):
    conn = pymysql.connect(
        host= 'localhost',
        user= 'root',
        password= '1234',
        db= 'mysql'
    )
    cur = conn.cursor()

    cur.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")
    cur.execute(f"USE {database_name};")

    return


def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS job_types1(
        cat_id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(255)
    );""")

    cur.execute("""CREATE TABLE IF NOT EXISTS job_types2(
        subcat_id INT AUTO_INCREMENT PRIMARY KEY,
        subcategory VARCHAR(255)
    );""")

    cur.execute("""CREATE TABLE IF NOT EXISTS states(
        state_id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(255)
    );""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS company_details(
        company_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        description VARCHAR(2048),
        state VARCHAR(255),
        subcategory VARCHAR(255)
    );""")

    cur.execute("""CREATE TABLE IF NOT EXISTS jobs(
        job_id INT AUTO_INCREMENT PRIMARY KEY,
        company VARCHAR(255),
        position VARCHAR(255),
        location VARCHAR(255)
    );""")


    return "Successfully Created"


def connect_db():
    try:
        conn = pymysql.connect(
            host= 'localhost',
            user= 'root',
            password= '1234',
            db= DATABASE_NAME
        )
        print(f"Database {DATABASE_NAME} connected")
    except OperationalError:
        # Database is not created yet, or has been dropped
        create_db(DATABASE_NAME)
        conn = connect_db()
        # Also creating the tables that were lost with the database
        create_tables(conn)

    return conn


def check_version(conn):
    cur = conn.cursor()
    cur.execute("select @@version")
    output = cur.fetchall()
    print(output)

    return output


def close_conn(conn):
    conn.close()
    print("Connection Closed")

    return "Connection closed"


def add_job_type1(conn, category):
    cur = conn.cursor()

    query = 'INSERT INTO job_types1(category) VALUES (%s);'
    val = (category)
    cur.execute(query, val)
    conn.commit()

    return f"Added {category} into {conn.db} database."


def add_job_type2(conn, subcategory):
    cur = conn.cursor()

    query = 'INSERT INTO job_types2(subcategory) VALUES (%s);'
    val = (subcategory)
    cur.execute(query, val)
    conn.commit()

    return f"Added {subcategory} into {conn.db} database."


def add_state(conn, state):
    cur = conn.cursor()

    query = 'INSERT INTO states(state) VALUES (%s);'
    val = (state)
    cur.execute(query, val)
    conn.commit()

    return f"Added {state} into {conn.db} database."


def add_company_detail(conn, name, desc, state, subcategory):
    cur = conn.cursor()
    query = f'INSERT INTO company_details(name, description, state, subcategory) VALUES (%s, %s, %s, %s);'
    val = (name, desc, state, subcategory)
    cur.execute(query, val)
    conn.commit()

    return f"Added {name} and it's details into {conn.db} database."


def add_job(conn, company, position, location):
    cur = conn.cursor()
    
    query = f'INSERT INTO jobs(company, position, location) VALUES(%s, %s, %s);'
    val = (company, position, location)
    cur.execute(query, val)
    conn.commit()

    return f"Added {position} Job for {company}"


if __name__ == "__main__":
    conn = connect_db()
    cur = conn.cursor()

    check_version(conn)
    create_tables(conn)

    cur.execute("SHOW TABLES;")
    print("All tables:", *cur.fetchall())
    close_conn(conn)