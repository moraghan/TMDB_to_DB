
import requests
import sys
import json

from sqlalchemy import Column, Integer, String, select
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

if sys.argv[1]:
    lower_request_id = int(sys.argv[1])
else:
    lower_request_id = 1

if sys.argv[2]:
    upper_request_id = int(sys.argv[2])
else:
    upper_request_id = 100000



#request_types = {['collection', 'person', 'movie', 'company', 'credit']}

API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'
BASE_URL = 'https://api.themoviedb.org/3/'
BASE_URL_END = '?api_key=' + API_KEY

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class MovieRequest(Base):
    __tablename__ = 'movie_request'

    request_id = Column(Integer(), primary_key=True, autoincrement=True)
    request_type = Column(String(20))
    request_key = Column(Integer())
    json_request = Column(JSONB)

class RequestType(Base):
    __tablename__ = 'request_type'

    request_type_id = Column(Integer(), primary_key=True, autoincrement=True)
    request_type = Column(String(20))
    lower_request_key = Column(Integer())
    upper_request_key = Column(Integer())

Base.metadata.create_all(engine)

movie_request_type = RequestType(request_type = 'movie', lower_request_key = 1, upper_request_key = 200 )
session.add(movie_request_type)

session.commit()

#for _request_id in range(int(lower_request_id), int(upper_request_id)):
for _request_id in range(605, 606):

    rows = session.execute(select(RequestType.request_type)).all()

    for request_type in rows :

        print(f'Retrieving details for Type {request_type} and Request Id {_request_id}')

        try:

            url = BASE_URL + str(request_type) + '/' + str(_request_id) + BASE_URL_END
            _response_data = requests.get(url)

            if _response_data.status_code == 200:

                response_data = json.loads(_response_data.text)
                print(response_data['request_key'])

                if session.query(MovieRequest).filter(MovieRequest.request_key == _request_id,
                                                                MovieRequest.request_type == request_type).first() is None:

                    request_to_add = MovieRequest(
                        request_type=request_type,
                        request_key=_request_id,
                        json_request=response_data)

                    session.add(request_to_add)
                    session.commit()

        except Exception as e:
            print("Failed trying to return information for:", e)
            raise e

        finally:

            session.close()
