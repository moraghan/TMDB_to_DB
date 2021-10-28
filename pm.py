import json

import click
import requests
from colorama import Fore, Style
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from helpers import get_db_connection, get_api_key, get_request_types
from models.tmdb_request import TMDBRequest

REQUEST_TYPE_INFO = get_request_types()
API_KEY = get_api_key()
DB_URL = get_db_connection()

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()


@click.command()
@click.option('--request_type', default='movie', help='Type of TMdb API Request you wish to make')
@click.option('--start_request_key', default=0, help='Starting value for request key')
def process_requests_for_type(request_type: str, start_request_key: int) -> None:
    """Retrieve information from TMdb API and insert into database"""
    if REQUEST_TYPE_INFO.get(request_type, None) is None:
        print(Fore.RED + f'Request Type {request_type} does not exist. Exiting app.')
        print(Style.RESET_ALL)
        exit(0)

    request_type_upper_limit = REQUEST_TYPE_INFO[request_type].MAX_REQUEST_KEY

    request_type_url = REQUEST_TYPE_INFO[request_type].URL

    if start_request_key is None or start_request_key == 0:
        _last_key = session.query(
            func.max(TMDBRequest.request_key).filter(TMDBRequest.request_type == request_type)).one()
        if _last_key[0]:
            current_key = _last_key[0] + 1
    else:
        current_key = start_request_key

    while current_key < request_type_upper_limit:

        print(f'Retrieving details for Type {request_type} and Request Id {current_key}')

        if session.query(TMDBRequest).filter(TMDBRequest.request_key == current_key,
                                             TMDBRequest.request_type == request_type).first() is None:

            enriched_url = request_type_url.replace('{api_key}', API_KEY).replace('{id}', str(current_key))

            _response_data = requests.get(enriched_url)

            if _response_data.status_code == 200:
                response_data = json.loads(_response_data.text)
            else:
                print(Fore.RED + f'Request Type {request_type} does not retrieve anything for Request Id {current_key}')
                print(Style.RESET_ALL)
                response_data = None

            response_to_add = TMDBRequest(
                request_type=request_type,
                request_key=current_key,
                request_text=enriched_url,
                response_status_code=_response_data.status_code,
                response_json=response_data)

            try:
                session.add(response_to_add)
                session.commit()
            except Exception as e:
                print("Failed trying to create information for:", e)
                raise e

        else:

            print('Record already exists so skipping Request')

        current_key += 1

    session.close()


if __name__ == "__main__":
    process_requests_for_type()
