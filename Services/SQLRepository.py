from sqlalchemy import create_engine
import os
import os.path

path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
path = os.path.join(path, "mysite\db.sqlite3")
print(path)
engine = create_engine(f'sqlite:////D:\Projects\Web-platform\mysite\db.sqlite3')
engine.connect()

print(engine)