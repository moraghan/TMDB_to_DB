import json

import requests
from sqlalchemy import Column, Integer, String, Index, func
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from colorama import Fore, Back, Style

# if sys.argv[1]:
#     lower_request_id = int(sys.argv[1])
# else:
#     lower_request_id = 1
#
# if sys.argv[2]:
#     upper_request_id = int(sys.argv[2])
# else:
#     upper_request_id = 100000


request_types_limits = {"movie": 1000000,
                        "person": 1000000,
                        "collection": 20000,
                        "company": 10000,
                        "credit": 1000000,
                        "keyword": 10000,
                        "people": 1000000
                        }

API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'
BASE_URL = 'https://api.themoviedb.org/3/'
BASE_URL_END = '?api_key=' + API_KEY

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class TMDBRequest(Base):
    __tablename__ = 'tmdb_request'

    request_id = Column(Integer(), primary_key=True, autoincrement=True)
    request_type = Column(String(20))
    request_key = Column(Integer())
    json_response = Column(JSONB)
    __table_args__ = (Index('request_unique_idx', request_key, request_type),)


Base.metadata.create_all(engine)

session.commit()


def process_requests_for_type(request_type):
    request_type_upper_limit = request_types_limits.get(request_type, None)

    if not request_type_upper_limit:
        print('unknown category')
        return -1

    _last_key = session.query(func.max(TMDBRequest.request_key).filter(TMDBRequest.request_type == request_type)).one()

    if _last_key[0]:
        current_key = _last_key[0]
    else:
        current_key = 0

    while current_key < request_type_upper_limit:

        current_key += 1

        print(f'Retrieving details for Type {request_type} and Request Id {current_key}')

        if session.query(TMDBRequest).filter(TMDBRequest.request_key == current_key,
                                             TMDBRequest.request_type == request_type).first() is None:

            if request_type == 'credit':
                url = BASE_URL + 'movie' + '/' + str(current_key) + '/credits' + BASE_URL_END
            else:
                url = BASE_URL + str(request_type) + '/' + str(current_key) + BASE_URL_END

            _response_data = requests.get(url)

            if _response_data.status_code == 200:
                response_data = json.loads(_response_data.text)

                response_to_add = TMDBRequest(
                    request_type=request_type,
                    request_key=current_key,
                    json_response=response_data)

                session.add(response_to_add)
                session.commit()

            else:
                print(Fore.RED + f'Request Type {request_type} does not retrieve anything for Request Id {current_key}')
                print(Style.RESET_ALL)

        else:

            print('Record already exists so skipping Request')


process_requests_for_type('movie')

# for _request_id in range(int(lower_request_id), int(upper_request_id)):
for _request_id in range(1, 1000000):

    for request_type in range(len(request_types_limits)):

        for key in request_types_limits[request_type]:

            upper_limit = request_types_limits[request_type][key]

            if upper_limit > _request_id:

                print(f'Retrieving details for Type {key} and Request Id {_request_id}')

                try:

                    if session.query(TMDBRequest).filter(TMDBRequest.request_key == _request_id,
                                                         TMDBRequest.request_type == key).first() is None:

                        if key == 'credit':
                            url = BASE_URL + 'movie' + '/' + str(_request_id) + '/credits' + BASE_URL_END
                        else:
                            url = BASE_URL + str(key) + '/' + str(_request_id) + BASE_URL_END

                        _response_data = requests.get(url)

                        if _response_data.status_code == 200:
                            response_data = json.loads(_response_data.text)

                            request_to_add = TMDBRequest(
                                request_type=key,
                                request_key=_request_id,
                                json_response=response_data)

                            session.add(request_to_add)
                            session.commit()

                    else:

                        print('Record already exists so skipping Request')

                except Exception as e:
                    print("Failed trying to return information for:", e)
                    raise e

                finally:

                    session.close()
