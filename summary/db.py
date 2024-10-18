import mysql.connector
import sshtunnel
import logging

from .config import Config
from datetime import datetime
import numpy as np
import mysql.connector
import sshtunnel
import logging
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

def group_in_db(data, apq_id,version):
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
        processed_ids = []
        for i in data['Match']:
            selected_ids = data.loc[data['Match'] == i, 'Number'].str.split(', ')
            logging.info(f"selected_ids: {selected_ids}")
            description = ""
            now = datetime.now()
            created = now.strftime("%Y/%m/%d %H:%M:%S")
            title = i.encode('utf-8').decode('windows-1252')
            logging.info(f"title: {title}")
            migrated_from = 0
            answer_id = 0
            creation="AI"
            group_order = None
            sqlInsert = "INSERT INTO group_ideas VALUES (DEFAULT,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            valInsert = (title,description,apq_id,created,created, migrated_from,answer_id,creation,0,group_order,int(version),0)
            mycursor.execute(sqlInsert, valInsert)
            mydb.commit()
            id = mycursor.lastrowid
            
              # Array to keep track of processed IDs

            for value in selected_ids:
                for key in value:
                    logging.info(f"key: {key}")

                    # Check if the ID is in the processed_ids array
                    if key in processed_ids:
                        logging.info(f"ID {key} already processed, skipping insertion.")
                    else:
                        # ID not in array, process it
                        logging.info(f"Processing ID {key}")
                        sqlGroupVersion = "INSERT INTO group_idea_version VALUES (DEFAULT, %s, %s)"
                        valGroupUpdate = (key, id)
                        mycursor.execute(sqlGroupVersion, valGroupUpdate)
                        mydb.commit()

                        # Add the ID to the processed_ids array
                        processed_ids.append(key)

def insert_or_update_progress(apq_id, version, progress):
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

        # Check if the row already exists
        select_query = "SELECT * FROM group_idea_progress WHERE apq_id = %s AND version = %s"
        mycursor.execute(select_query, (apq_id, version))
        result = mycursor.fetchone()

        if result:
            # Row exists, update it
            update_query = "UPDATE group_idea_progress SET progress = %s, created = %s WHERE apq_id = %s AND version = %s"
            mycursor.execute(update_query, (progress, created, apq_id, version))
        else:
            # Row does not exist, insert a new one
            insert_query = "INSERT INTO group_idea_progress VALUES (DEFAULT, %s, %s, %s, %s)"
            mycursor.execute(insert_query, (apq_id, created, version, progress))

        mydb.commit()


def delete_group_ideas(apq_id, version):
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
        delete_query = "DELETE group_ideas FROM group_ideas WHERE group_ideas.version=%s AND group_ideas.apq_id=%s"
        mycursor.execute(delete_query, (version, apq_id))

        delete_query_2 = "DELETE giv FROM group_idea_version giv INNER JOIN group_ideas ON giv.group_id = group_ideas.id WHERE group_ideas.version=%s AND group_ideas.apq_id=%s"
        mycursor.execute(delete_query_2, (version, apq_id))
        mydb.commit()

