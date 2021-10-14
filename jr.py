import json
from omegaconf import DictConfig, OmegaConf

import requests
from colorama import Fore, Style
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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

conf = OmegaConf.load('config/config.yaml')

REQUEST_TYPE_INFO = conf.TMDB_REQUEST_TYPES

API_KEY = (conf.APP.API_KEY)
DB_URL = (conf.DATABASE.DATABASE_URL)

engine = create_engine(DB_URL)
Base = declarative_base()
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
from models.tmdb_request import TMDBRequest
session = Session()


def process_requests_for_type(request_type):

    if REQUEST_TYPE_INFO.get(request_type, None) is None :
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
                    print("Failed trying to return information for:", e)
                    raise e


            else:
                print(Fore.RED + f'Request Type {request_type} does not retrieve anything for Request Id {current_key}')
                print(Style.RESET_ALL)

        else:

            print('Record already exists so skipping Request')

        session.close()


process_requests_for_type('credit')

