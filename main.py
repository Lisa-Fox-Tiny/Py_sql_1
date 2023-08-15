import psycopg2


def drop_db(cur):
    cur.execute("""
        DROP TABLE phone_numbers;
        DROP TABLE clients;
    """)


def create_db(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(20),
            last_name VARCHAR(35),
            email VARCHAR(260)
        );
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phone_numbers(
            phone_id SERIAL PRIMARY KEY,
            phone VARCHAR(12),
            client_id INTEGER REFERENCES clients(id)
        );
        """)
    return


def add_phone(cur, client_id, phones):
    cur.execute("""
    INSERT INTO phone_numbers(phone, client_id)
    VALUES (%s, %s);
    """, (phones, client_id))
    return client_id


def add_client(cur, first_name, last_name, email, phones=None):
    cur.execute("""
        INSERT INTO clients(first_name, last_name, email)
        VALUES (%s, %s, %s);
        """, (first_name, last_name, email))
    cur.execute("""
        SELECT id from clients
        ORDER BY id DESC
        LIMIT 1;
        """)
    id = cur.fetchone()[0]
    if phones is None:
        return id
    else:
        add_phone(cur, id, phones)
        return id


def change_client(cur, client_id, first_name=None, last_name=None, email=None):
    cur.execute("""
        SELECT * FROM clients
        """)
    index = cur.fetchone()
    if first_name is None:
        first_name = index[1]
    if last_name is None:
        last_name = index[2]
    if email is None:
        email = index[3]
    cur.execute("""
            UPDATE clients
            SET first_name = %s, last_name = %s, email = %s
            where id = %s;
            """, (first_name, last_name, email, client_id))
    return client_id


def delete_phone(cur, phone):
    cur.execute("""
        DELETE FROM phone_numbers
        WHERE client_id=%s;
    """, (phone, ))
    return phone


def delete_client(cur, id):
    cur.execute("""
        DELETE FROM phone_numbers
        WHERE client_id = %s;
    """, (id, ))
    cur.execute("""
        DELETE FROM clients
        WHERE id = %s;
    """, (id, ))
    return id


def find_client(cur, first_name=None, last_name=None, email=None, phones=None):
    if first_name is None:
        first_name = '%'
    else:
        first_name = '%' + first_name + '%'
    if last_name is None:
        last_name = '%'
    else:
        last_name = '%' + last_name + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phones is None:
        cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                LEFT JOIN phone_numbers p ON c.id = p.client_id
                WHERE c.first_name LIKE %s AND c.last_name LIKE %s AND c.email LIKE %s
                """, (first_name, last_name, email))
    else:
        cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                LEFT JOIN phone_numbers p ON c.id = p.client_id
                WHERE c.first_name LIKE %s AND c.last_name LIKE %s AND c.email LIKE %s AND p.phone LIKE %s
                """, (first_name, last_name, email, phones))
    return cur.fetchall()


if __name__ == "__main__":
    with psycopg2.connect(database='base', user='postgres', password='123456912') as conn:
        with conn.cursor() as curs:
            drop_db(curs)
            create_db(curs)
            add_client(curs, "Михаил", "Шабалин", "712qfd@gmail.com")
            add_client(curs, "Кирилл", "Лебедев", "009aaf@gmail.com")
            curs.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                LEFT JOIN phone_numbers p ON c.id = p.client_id
                ORDER BY c.id
            """)
            print(curs.fetchall())
            add_phone(curs, 1, 79163452130)
            curs.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                        LEFT JOIN phone_numbers p ON c.id = p.client_id
                        ORDER BY c.id
                    """)
            print(curs.fetchall())
            print(find_client(curs, None, None, None, '79163452130'))
            change_client(curs, 1, "Иван", None, "klijh54@gmail.com")
            curs.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                        LEFT JOIN phone_numbers p ON c.id = p.client_id
                        ORDER BY c.id
                        """)
            print(curs.fetchone())
            delete_phone(curs, 1)
            curs.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                        LEFT JOIN phone_numbers p ON c.id = p.client_id
                        ORDER BY c.id
                        """)
            print(curs.fetchone())
            delete_client(curs, 1)
            curs.execute("""
                        SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM clients c
                        LEFT JOIN phone_numbers p ON c.id = p.client_id
                        ORDER BY c.id
                        """)
            print(curs.fetchall())
            print(find_client(curs, None, None, '009aaf@gmail.com'))
            print(find_client(curs, 'Кирилл'))
    conn.close()