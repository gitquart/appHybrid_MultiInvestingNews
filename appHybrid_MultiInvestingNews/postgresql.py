import psycopg2

HOST='ec2-52-5-1-20.compute-1.amazonaws.com'
DBNAME='d60rbnvko1pi6s'
USER='bkhliiklxjjgce'
PORT='5432'
PASSWORD='e1ec6f00414a7843803c52e448137f9d8213bdb3ffe8cd9bc9517e6b89f2ad01'


def getQuery(query):
    
    conn = psycopg2.connect(host=HOST,dbname=DBNAME, user=USER, password=PASSWORD,sslmode='require')
    cursor = conn.cursor()
    cursor.execute(query)
    lsResult = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    return lsResult

def executeNonQuery(query):
    conn = psycopg2.connect(host=HOST,dbname=DBNAME, user=USER, password=PASSWORD,sslmode='require')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
   





