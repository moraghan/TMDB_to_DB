from omegaconf import OmegaConf

config_file = '/Users/moraghan/PycharmProjects/pythonTMDB/config/config.yaml'

def get_db_connection() :
    conf = OmegaConf.load(config_file)
    return conf.DATABASE.DATABASE_URL

def get_api_key() :
    conf = OmegaConf.load(config_file)
    return conf.APP.API_KEY

def get_request_types() :
    conf = OmegaConf.load(config_file)
    return conf.TMDB_REQUEST_TYPES
