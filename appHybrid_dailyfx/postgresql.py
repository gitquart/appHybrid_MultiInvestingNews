import psycopg2

HOST='ec2-23-23-164-251.compute-1.amazonaws.com'
DBNAME='d7vvujncq3os5s'
USER='acanhvmrdorzis'
PASSWORD='e4a2d5e50f22dd51728eff619d70c9b172317f7e89d767c34f3b2aba91c0f339'
PORT='5432'


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

    return True
   





