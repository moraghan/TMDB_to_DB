import json
import hydra
from omegaconf import DictConfig, OmegaConf

import requests
from colorama import Fore, Style
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.tmdb_request import TMDBRequest

@hydra.main(config_path="config", config_name="config")
def my_app(cfg: DictConfig) -> dict:
    _config = OmegaConf.to_yaml(cfg)
    print(_config)

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

#engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# class TMDBRequest(Base):
#     __tablename__ = 'tmdb_request'
#
#     request_id = Column(Integer(), primary_key=True, autoincrement=True)
#     request_type = Column(String(20), nullable=False)
#     request_key = Column(Integer(),nullable=False)
#     json_response = Column(JSONB)
#     __table_args__ = (UniqueConstraint('request_key', 'request_type', name = 'request_key_type_UK'),)

Base.metadata.create_all(engine)

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
            try:

                _response_data = requests.get(url)

            except Exception as e:

                print(Fore.RED + f'Error retrieving daat for url {url}')
                print(Style.RESET_ALL)


            if _response_data.status_code == 200:
                response_data = json.loads(_response_data.text)

                response_to_add = TMDBRequest(
                    request_type=request_type,
                    request_key=current_key,
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


process_requests_for_type('movie')

