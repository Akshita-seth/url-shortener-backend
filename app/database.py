from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker #sessionmaker creates a factory for database sessions.

from app.models import Base

DATABASE_URL = "postgresql+psycopg://postgres:postgres@postgres:5432/urlshortener"
#"Use PostgreSQL through psycopg, connect as user postgres, using this password, to PostgreSQL running on docker container postgres at port 5432, and use the urlshortener database."

engine = create_engine(DATABASE_URL) #Knows how to connect to PostgreSQL.

#Creates database-session objects.
SessionLocal = sessionmaker(
    bind=engine,  #Sessions created by this factory should use our PostgreSQL engine defined above
    autoflush=False, #Don't automatically push pending changes to the database before certain queries
    autocommit=False  #database changes are not automatically committed
)
#doesn't create an actual session yet. It creates something that can create sessions when our API needs them.

Base.metadata.create_all(engine)
#Using this database engine, create all the tables that have been defined under Base if they don't already exist.
#SQLAlchemy looks at Base. Finds all classes that inherit from it (URL, User, etc.). Creates the corresponding tables in PostgreSQL.

#Creates a session for a request and closes it afterward
def get_db(): #Every API request that needs the database can get its own session
    db = SessionLocal() #create Session

    try:
        yield db #Give this database session to the code that needs it.
    finally: #finally is important because even if something goes wrong, we still want to close the session
        db.close()  #When that API operation is finished, close the session.
