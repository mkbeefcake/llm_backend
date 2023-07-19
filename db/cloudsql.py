import os

import sqlalchemy
from google.cloud.sql.connector import Connector

connector = Connector()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


def create_pool():
    conn = connector.connect(
        "chat-automation-387710:us-central1:chat-automation",
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db="chat_histories",
    )
    pool = sqlalchemy.create_engine("mysql+pymysql://", creator=conn)

    with pool.connect() as db_conn:
        sqlalchemy.text(
            "CREATE TABLE IF NOT EXISTS chat_histories "
            "(id SERIAL NOT NULL, user VARCHAR(255) NOT NULL, "
            "provider VARCHAR(255) NOT NULL, identifier VARCHAR(255) NOT NULL, "
            "fromUser VARCHAR(255) NOT NULL, "
            "text BLOB NOT NULL, "
            "price FLOAT NOT NULL, "
            "isOpened BOOLEAN NOT NULL, "
            "mediaCount INT, "
            "createdAt DATETIME, "
            "PRIMARY KEY (id));"
        )
        db_conn.commit()

    return pool


pool = create_pool()


async def update_chathistories_on_sqldb(
    user_id, provider_name, identifier_name, new_content
):
    with pool.connect() as db_conn:
        insert_stmt = sqlalchemy.text(
            "INSERT INTO chat_histories (user, provider, identifier, "
            "fromUser, text, price, isOpened, mediaCount, createdAt) "
            "VALUES (:user, :provider, :identifier, "
            ":fromUser, :text, :price, :isOpened, :mediaCount, :createdAt)",
        )

        for element in new_content:
            db_conn.execute(
                insert_stmt,
                parameters={
                    "user": user_id,
                    "provider": provider_name,
                    "identifier": identifier_name,
                    "fromUser": element["fromUser"],
                    "text": element["text"],
                    "price": float(element["price"]),
                    "isOpened": bool(element["isOpened"]),
                    "mediaCount": int(element["mediaCount"]),
                    "createdAt": element["createdAt"],
                },
            )
            db_conn.commit()

    pass
