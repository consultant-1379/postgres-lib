import psycopg2
import psycopg2.extras

'''
Errors with psycopg
'''

# Wrong Host
"""
Error:  could not translate host name "wrong_host" to address: Name or service not known

error.pgcode:  None
error.pgerror:  None
"""

# try:
#     connection = psycopg2.connect(user="postgres",
#                                   password="P0stgreSQL11",
#                                   host="wrong_host",
#                                   port="5432",
#                                   database="flsdb")
# except psycopg2.Error as error:
#     print('Error: ', error)
#     print("error.pgcode: ", error.pgcode)
#     print("error.pgerror: ", error.pgerror)
'''Psycopg Dictionary Buzz - DictCursor'''
# print('#' * 50)
# print(' # DictCursor #')
'''Output:
 # DictCursor #
[['databasechangeloglock', 1, 0, 0, 0, 2, 0, None, None, 3, None], ['tblock', 0, 0, 0, 0, 1, 0, None, None, 3, None], ['databasechangelog', 13, 0, 0, 0, 0, 0, None, None, 3, None], ['pm_rop_info', 0, 0, 0, 0, 0, 0, None, None, 3, None], ['pm_rop_info_metadata', 0, 0, 0, 0, 0, 0, None, None, 3, None], ['ulsa_info', 0, 0, 0, 0, 0, 0, None, None, 3, None]]
'''
# try:
#     connection = psycopg2.connect(user="postgres",
#                                   password="P0stgreSQL11",
#                                   host="postgres",
#                                   port="5432",
#                                   database="flsdb")
#
#     qry = 'SELECT pg_stat_user_tables.relname AS table, ' \
#           'pg_stat_user_tables.n_live_tup AS rowcount, ' \
#           'pg_stat_user_tables.n_tup_ins AS inserts, ' \
#           'pg_stat_user_tables.n_tup_upd AS updates, ' \
#           'pg_stat_user_tables.n_tup_del AS deletes, ' \
#           'pg_stat_user_tables.n_dead_tup AS bloat, ' \
#           'pg_stat_user_tables.autovacuum_count, ' \
#           'pg_stat_user_tables.last_vacuum, ' \
#           'pg_stat_user_tables.last_autovacuum, ' \
#           'pg_stat_user_tables.analyze_count, ' \
#           'pg_stat_user_tables.last_autoanalyze ' \
#           'FROM pg_stat_user_tables ' \
#           'INNER JOIN pg_class ' \
#           'ON pg_stat_user_tables.relname = pg_class.relname ' \
#           'ORDER BY pg_stat_user_tables.n_dead_tup DESC;'
#     cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     cursor.execute(qry)
#     rows = cursor.fetchall()
#     print(rows)
#     print('$' * 50)
#     print(rows[2])
#     print('$' * 50)
#     for row in rows:
#         print(type(row))
#         print(row['table'])
#         print(row['rowcount'])
#         print(row['inserts'])
#         print(row['updates'])
#         print(row['deletes'])
#         print(row['bloat'])
# except psycopg2.Error as error:
#     print('Error: ', error)
#     print("error.pgcode: ", error.pgcode)
#     print("error.pgerror: ", error.pgerror)
#
# '''Psycopg Dictionary Buzz - RealDictCursor'''
# print('#' * 50)
# print(' # RealDictCursor #')
# '''Output:
#  # RealDictCursor #
# [RealDictRow([('table', 'databasechangeloglock'), ('rowcount', 1), ('inserts', 0), ('updates', 0), ('deletes', 0), ('bloat', 2), ('autovacuum_count', 0), ('last_vacuum', None), ('last_autovacuum', None), ('analyze_count', 3), ('last_autoanalyze', None)]), RealDictRow([('table', 'tblock'), ('rowcount', 0), ('inserts', 0), ('updates', 0), ('deletes', 0), ('bloat', 1), ('autovacuum_count', 0), ('last_vacuum', None), ('last_autovacuum', None), ('analyze_count', 3), ('last_autoanalyze', None)]), RealDictRow([('table', 'databasechangelog'), ('rowcount', 13), ('inserts', 0), ('updates', 0), ('deletes', 0), ('bloat', 0), ('autovacuum_count', 0), ('last_vacuum', None), ('last_autovacuum', None), ('analyze_count', 3), ('last_autoanalyze', None)]), RealDictRow([('table', 'pm_rop_info'), ('rowcount', 0), ('inserts', 0), ('updates', 0), ('deletes', 0), ('bloat', 0), ('autovacuum_count', 0), ('last_vacuum', None), ('last_autovacuum', None), ('analyze_count', 3), ('last_autoanalyze', None)]), RealDictRow([('table', 'pm_rop_info_metadata'), ('rowcount', 0), ('inserts', 0), ('updates', 0), ('deletes', 0), ('bloat', 0), ('autovacuum_count', 0), ('last_vacuum', None), ('last_autovacuum', None), ('analyze_count', 3), ('last_autoanalyze', None)]), RealDictRow([('table', 'ulsa_info'), ('rowcount', 0), ('inserts', 0), ('updates', 0), ('deletes', 0), ('bloat', 0), ('autovacuum_count', 0), ('last_vacuum', None), ('last_autovacuum', None), ('analyze_count', 3), ('last_autoanalyze', None)])]
# '''
# try:
#     connection = psycopg2.connect(user="postgres",
#                                   password="P0stgreSQL11",
#                                   host="postgres",
#                                   port="5432",
#                                   database="flsdb")
#     qry = 'SELECT pg_stat_user_tables.relname AS table, ' \
#           'pg_stat_user_tables.n_live_tup AS rowcount, ' \
#           'pg_stat_user_tables.n_tup_ins AS inserts, ' \
#           'pg_stat_user_tables.n_tup_upd AS updates, ' \
#           'pg_stat_user_tables.n_tup_del AS deletes, ' \
#           'pg_stat_user_tables.n_dead_tup AS bloat, ' \
#           'pg_stat_user_tables.autovacuum_count, ' \
#           'pg_stat_user_tables.last_vacuum, ' \
#           'pg_stat_user_tables.last_autovacuum, ' \
#           'pg_stat_user_tables.analyze_count, ' \
#           'pg_stat_user_tables.last_autoanalyze ' \
#           'FROM pg_stat_user_tables ' \
#           'INNER JOIN pg_class ' \
#           'ON pg_stat_user_tables.relname = pg_class.relname ' \
#           'ORDER BY pg_stat_user_tables.n_dead_tup DESC;'
#     cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     cursor.execute(qry)
#     rows = cursor.fetchall()
#     print(rows)
#     print('$' * 50)
#     print(rows[2])
#     print('$' * 50)
#     for row in rows:
#         print(row['table'])
#         print(row['rowcount'])
#         print(row['inserts'])
#         print(row['updates'])
#         print(row['deletes'])
#         print(row['bloat'])
# except psycopg2.Error as error:
#     print('Error: ', error)
#     print("error.pgcode: ", error.pgcode)
#     print("error.pgerror: ", error.pgerror)

try:
    connection = psycopg2.connect(user="postgres",
                                  password="P0stgreSQL11",
                                  host="postgres",
                                  port="5432",
                                  database="flsdb")
    qry = 'SELECT pg_stat_user_tables.relname AS table, ' \
          'pg_stat_user_tables.n_live_tup AS rowcount, ' \
          'pg_stat_user_tables.n_tup_ins AS inserts, ' \
          'pg_stat_user_tables.n_tup_upd AS updates, ' \
          'pg_stat_user_tables.n_tup_del AS deletes, ' \
          'pg_stat_user_tables.n_dead_tup AS bloat, ' \
          'pg_stat_user_tables.autovacuum_count, ' \
          'pg_stat_user_tables.last_vacuum, ' \
          'pg_stat_user_tables.last_autovacuum, ' \
          'pg_stat_user_tables.analyze_count, ' \
          'pg_stat_user_tables.last_autoanalyze ' \
          'FROM pg_stat_user_tables ' \
          'INNER JOIN pg_class ' \
          'ON pg_stat_user_tables.relname = pg_class.relname ' \
          'ORDER BY pg_stat_user_tables.n_dead_tup DESC;'
    cursor = connection.cursor()
    cursor.execute(qry)
    rows = cursor.fetchall()
    print(rows)
except psycopg2.Error as error:
    print('Error: ', error)
    print("error.pgcode: ", error.pgcode)
    print("error.pgerror: ", error.pgerror)

"""
Error:  relation "pmrop_info" does not exist
LINE 1: SELECT name FROM pmrop_info LIMIT 1;
                         ^

error.pgcode:  42P01
error.pgerror:  ERROR:  relation "pmrop_info" does not exist
LINE 1: SELECT name FROM pmrop_info LIMIT 1;
"""
# try:
#     connection = psycopg2.connect(user="postgres",
#                                   password="P0stgreSQL11",
#                                   host="postgres",
#                                   port="5432",
#                                   database="flsdb")
#     cursor = connection.cursor()
#     qry = 'SELECT name FROM pmrop_info LIMIT 1;'
#     cursor.execute(qry)
#     row = cursor.fetchone()
#     print(row)
# except psycopg2.Error as error:
#     print('Error: ', error)
#     print("error.pgcode: ", error.pgcode)
#     print("error.pgerror: ", error.pgerror)


# try:
#     connection = psycopg2.connect(user="postgres",
#                                   password="P0stgreSQL11",
#                                   host="postgres",
#                                   port="5432",
#                                   database="flsdb")
#     cursor = connection.cursor()
#     qry = 'SELECT * FROM databasechangelog LIMIT 1;'
#     cursor.execute(qry)
#     rows = cursor.fetchall()
#     cursor.close()
#     print(rows)
# except psycopg2.Error as error:
#     print('Error: ', error)
#     print("error.pgcode: ", error.pgcode)
#     print("error.pgerror: ", error.pgerror)

# try:
#     connection = psycopg2.connect(user="postgres",
#                                   password="wrong_password",
#                                   host="postgres",
#                                   port="5432",
#                                   database="flsdb")
#     cursor = connection.cursor()
#     qry = 'SELECT * FROM databasechangelog LIMIT 1;'
#     cursor.execute(qry)
#     rows = cursor.fetchall()
#     cursor.close()
#     print(rows)
# except psycopg2.Error as error:
#     print('Error: ', error)
#     print("error.pgcode: ", error.pgcode)
#     print("error.pgerror: ", error.pgerror)
