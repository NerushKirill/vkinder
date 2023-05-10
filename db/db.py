import psycopg2 as pg

from config import CONN_DB


def with_connection(f):
    def with_connection_(*args, **kwargs):
        with pg.connect(CONN_DB) as conn:
            cur = conn.cursor()
            try:
                f(cur, *args, **kwargs)
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.commit()
                try:
                    if f.__name__ == 'my_favorite':
                        return cur.fetchall()
                    else:
                        return cur.fetchone()[0]
                except Exception as e:
                    if f.__name__ not in ['create_db', 'clear_db',  'check_candidate',
                                          'like_candidate', 'link_my_favorite']:
                        print(f'Function "{f.__name__}" - {e}')
    return with_connection_


@with_connection
def create_db(cur):
    cur.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id int NOT NULL,
                first_name varchar(50) NOT NULL,
                last_name varchar(50) NOT NULL,
                age int NOT NULL,
                user_id int NOT NULL,
                u_flag bool,
                link text);""")


@with_connection
def clear_db(cur):
    try:
        cur.execute("""DROP TABLE IF EXISTS candidates""")
        print('reset db')
    except Exception as e:
        print(e)


def reset():
    clear_db()
    create_db()


@with_connection
def add_candidate(cur, candidate, flag=False):
    try:
        cur.execute("""
           INSERT into candidates (id, first_name, last_name, age, user_id, u_flag, link) 
           values (%s, %s, %s, %s, %s, %s, %s) 
           returning id  
           """, (candidate['id'], candidate['first_name'],
                 candidate['last_name'], candidate['age'], candidate['user_id'], flag, candidate['link']))
    except Exception as e:
        print(e)


@with_connection
def check_candidate(cur, candidate):
    try:
        cur.execute("""
            SELECT COUNT(*) 
            FROM candidates
            WHERE id = %s
           """, (candidate['id'], ))
    except Exception as e:
        print(e)


@with_connection
def like_candidate(cur, candidate):
    try:
        cur.execute("""
            UPDATE candidates
            SET u_flag = true
            WHERE id = %s
           """, (candidate['id'], ))
    except Exception as e:
        print(e)


@with_connection
def my_favorite(cur):
    try:
        list_link = cur.execute("""
                        SELECT first_name, last_name, age, link
                        FROM candidates
                        WHERE u_flag = true
                        """)
        return list_link
    except Exception as e:
        print(e)
