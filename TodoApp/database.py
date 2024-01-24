from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# sqlite is only used to create a table. If we want to enhance our table we have \
# to use Alembic.

# For SEQLite Database
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
# the above line contains this -- connect_args={'check_same_thread': False}
# which is used only in sqlite3 so here we have commented this lines.


# For PostgreSQL Database
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:ap222@localhost/TodoApplicationDatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# For MySQL Database
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:ap222@127.0.0.1:3306/TodoApplicationDatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit= False, autoflush= False, bind= engine)
Base = declarative_base() # Object of a Database, which controls the database



