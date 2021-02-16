from resources.io import ApiManager

# fetching data from Covid-tracking API
config_path = './.config/covid-tracking-api.yml'

api_man = ApiManager(config_path,
                    base_dir='./data/',
                    monitor_api=True)

api_man.fetch(force=False)

# retrieving states names dataframe
states_info_df = api_man.retrieve('states-info', as_dataframe=True)
us_historical_df = api_man.retrieve('us-historical', as_dataframe=True)

# dumping dataframes to pickle
states_info_df.to_pickle('./data/dataframes/states_info.pkl')
us_historical_df.to_pickle('./data/dataframes/us_historical.pkl')