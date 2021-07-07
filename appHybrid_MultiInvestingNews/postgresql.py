import psycopg2

HOST='ec2-52-6-178-202.compute-1.amazonaws.com'
DBNAME='dfqghadp4uimcj'
USER='zuifbxljotyqju'
PASSWORD='145e55d54668fefb4180a3a143799e38f0270dada403009f88841268bd90ae8c'
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
   





