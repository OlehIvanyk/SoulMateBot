from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, inspect, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from config import databaseurl

# Check if DATABASE_URL is correct
DATABASE_URL = databaseurl.replace("postgres://", "postgresql://")  # Ensure dialect is postgresql not postgres
engine = create_engine(DATABASE_URL, client_encoding='utf8')
metadata = MetaData()

# Defining the 'users' table schema using SQLAlchemy
users = Table('users', metadata,
              Column('user_id', Integer, primary_key=True),
              Column('date', DateTime),
              Column('name', String),
              Column('phone_number', String),
              Column('score', Integer),
              Column('percentage', Float),
              Column('question', Integer),
              Column('state', String),
              Column('answered_questions_count', Integer),
              Column('v_percent', Float),
              Column('a_percent', Float),
              Column('r_percent', Float),
              Column('k_percent', Float)
              )

# Creating a sessionmaker to interact with the database
Session = sessionmaker(bind=engine)


class DatabaseManager:
    def __init__(self):
        self.session = Session()
        inspector = inspect(engine)
        if not inspector.has_table("users"):
            self.create_table()

    def create_table(self):
        metadata.create_all(engine)

    def save_user_data(self, user_id, date, name, phone_number, score, percentage, question, state,
                       answered_questions_count=0, v_percent=0.0, a_percent=0.0, r_percent=0.0, k_percent=0.0):
        # Construct the insert statement
        stmt = insert(users).values(
            user_id=user_id, date=date, name=name, phone_number=phone_number,
            score=score, percentage=percentage, question=question, state=state,
            answered_questions_count=answered_questions_count,
            v_percent=v_percent, a_percent=a_percent, r_percent=r_percent, k_percent=k_percent
        )

        # On conflict (i.e., if the record with the specified user_id already exists), update the record
        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=['user_id'],
            set_=dict(
                date=date, name=name, phone_number=phone_number,
                score=score, percentage=percentage, question=question, state=state,
                answered_questions_count=answered_questions_count,
                v_percent=v_percent, a_percent=a_percent, r_percent=r_percent, k_percent=k_percent
            )
        )

        try:
            # Execute the statement and commit
            self.session.execute(do_update_stmt)
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def get_user_data(self, user_id):
        return self.session.query(users).filter_by(user_id=user_id).first()

    def close_db(self):
        self.session.close()

    def __del__(self):
        self.close_db()

    def alter_user_id_column(self):
        connection = engine.raw_connection()
        try:
            cursor = connection.cursor()
            cursor.execute('ALTER TABLE users ALTER COLUMN user_id TYPE BIGINT;')
            connection.commit()
        finally:
            connection.close()


