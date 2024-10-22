import sshtunnel

from .config import Config
from datetime import datetime
import mysql.connector
import sshtunnel
import pandas as pd



def get_ideas(apq_id):
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_SERVER, Config.SSH_PORT),
        ssh_username = Config.SSH_USER,
        ssh_password = Config.SSH_PASS,
        remote_bind_address = ('127.0.0.1', 3306)
    ) as tunnel:
        mydb = mysql.connector.connect(
            user= Config.MYSQL_USER,
            password=  Config.MYSQL_PASS,
            host = Config.HOST,
            port = int(tunnel.local_bind_port),
            database= Config.DB,
            raise_on_warnings= True
        )
        mycursor = mydb.cursor()


        sql = "SELECT id, idea FROM ideas WHERE apq_id = %s"
        val = (apq_id,)

        mycursor.execute(sql, val)
        data = mycursor.fetchall()
        df = pd.DataFrame(data)
        df_ideas = df.rename(columns={0: 'id', 1: 'idea'})

        sql = "SELECT question FROM apqs WHERE id = %s"
        val = (apq_id,)
        mycursor.execute(sql, val)
        question = mycursor.fetchall()

        return df_ideas, question

def insert_in_db(summary, apq_id):
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_SERVER, Config.SSH_PORT),
        ssh_username = Config.SSH_USER,
        ssh_password = Config.SSH_PASS,
        remote_bind_address = ('127.0.0.1', 3306)
    ) as tunnel:
        mydb = mysql.connector.connect(
            user= Config.MYSQL_USER,
            password=  Config.MYSQL_PASS,
            host = Config.HOST,
            port = int(tunnel.local_bind_port),
            database= Config.DB,
            raise_on_warnings= True
        )

        mycursor = mydb.cursor()


        now = datetime.now()
        created = now.strftime("%Y/%m/%d %H:%M:%S")
        sqlInsert = f"INSERT INTO group_ideas_summary (apq_id, created, summary) VALUES ({apq_id}, {created}, {summary});"
        mycursor.execute(sqlInsert, sqlInsert)
        mydb.commit()
        mycursor.close()
        mydb.close()