import json

import requests
from colorama import Fore, Style
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from models.tmdb_request import TMDBRequest
from helpers import get_db_connection, get_api_key, get_request_types

# if sys.argv[1]:
#     lower_request_id = int(sys.argv[1])
# else:
#     lower_request_id = 1
#
# if sys.argv[2]:
#     upper_request_id = int(sys.argv[2])
# else:
#     upper_request_id = 100000

# yaml_config = my_app()
# print(yaml_config)

REQUEST_TYPE_INFO = get_request_types()
API_KEY = get_api_key()
DB_URL = get_db_connection()

engine = create_engine(DB_URL)
#Base = declarative_base()

# from sqlalchemy import Column, Integer, String, UniqueConstraint
# from sqlalchemy.dialects.postgresql import JSONB
#
#
# class TMDBRequest(Base):
#     __tablename__ = 'tmdb_requests'
#
#     request_id = Column(Integer(), primary_key=True, autoincrement=True)
#     request_type = Column(String(20), nullable=False)
#     request_key = Column(Integer(), nullable=False)
#     request_text = Column(String(100), nullable=False)
#     json_response = Column(JSONB)
#     __table_args__ = (UniqueConstraint('request_key', 'request_type', name='request_key_type_UK'),)
#
#
# Base.metadata.create_all(engine)
#
Session = sessionmaker(bind=engine)

session = Session()


def process_requests_for_type(request_type):

    if REQUEST_TYPE_INFO.get(request_type, None) is None:
        print(Fore.RED + f'Request Type {request_type} does not exist. Exiting app.')
        print(Style.RESET_ALL)
        exit(0)

    request_type_upper_limit = REQUEST_TYPE_INFO[request_type].MAX_REQUEST_KEY
    request_type_url = REQUEST_TYPE_INFO[request_type].URL

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

            enriched_url = request_type_url.replace('{api_key}', API_KEY).replace('{id}', str(current_key))

            _response_data = requests.get(enriched_url)

            if _response_data.status_code == 200:
                response_data = json.loads(_response_data.text)

                response_to_add = TMDBRequest(
                    request_type=request_type,
                    request_key=current_key,
                    request_text=enriched_url,
                    json_response=response_data)

                try:
                    session.add(response_to_add)
                    session.commit()
                except Exception as e:
                    print("Failed trying to creatw information for:", e)
                    raise e


            else:
                print(Fore.RED + f'Request Type {request_type} does not retrieve anything for Request Id {current_key}')
                print(Style.RESET_ALL)

        else:

            print('Record already exists so skipping Request')

        session.close()



if __name__ == "__main__":

    process_requests_for_type('credit')
