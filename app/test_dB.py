from app.database import SessionLocal
from app.models import URL


db = SessionLocal()

new_url = URL(
    original_url="https://www.google.com",
    short_code="abc123"
)

db.add(new_url) #insert this object into dB
db.commit()   # commit this transaction and permanently save the change
db.refresh(new_url)  #we didn't provide the id. PostgreSQL generated it.
# refresh() asks the database for the current state of that row and updates our Python object with the database-generated values.

print(new_url.id)

db.close()