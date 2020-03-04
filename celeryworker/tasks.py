from celery import Celery
from google.cloud import storage
from configuration.app_config import GCPConfig, CeleryConfig

app = Celery('tasks', broker=CeleryConfig.BROKER)


@app.task
def initial_tweet_processing(user_id):
    storage_client = storage.Client.from_service_account_json(GCPConfig.GCP_JSON)
    bucket = storage_client.get_bucket(GCPConfig.GCP_STORAGE_BUCKET)
    resource_uri = GCPConfig.URI_PREFIX + user_id + '.json'
    storage_client.download_blob_to_file(resource_uri, CeleryConfig.TEMPSTORAGE + user_id + '.json')
    # grab the file from GCP cloud
    # edit file so we can successfully import as json
    # start iterating through the file so we can extract today and tomorrow off the file
    # on every occurence of valid tweets, write them to the tweet cache
    # update file status on user table
    # send signal to fire second job to complete processing of tweet archive
    pass


@app.task
def complete_tweet_processing():
    pass
