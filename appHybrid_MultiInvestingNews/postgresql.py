import psycopg2

HOST='ec2-52-5-1-20.compute-1.amazonaws.com'
DBNAME='d2518vjck351pf'
USER='fhgcymlgcyitvo'
PORT='5432'
PASSWORD='8a60be146a4ad13d922c6a4a70dd29781c57ae7bfe09b70af3465fac06db391f'


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
   





