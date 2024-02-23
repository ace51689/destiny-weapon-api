import requests
from environ import Env

env = Env()
Env.read_env()
API_KEY = env('API_KEY', default='temp')


def get_manifest():
	# Define the base url:
	base_url = 'https://www.bungie.net'
	# Define the headers:
	headers = {'x-api-key': API_KEY}
	# Request the manifest:
	# TODO add a try/except here
	manifest = requests.get(f"{base_url}/Platform/Destiny2/Manifest", headers=headers)
	# Define the current location:
	current_location = manifest.json()['Response']['jsonWorldContentPaths']['en']
	# Return the current manifest:
	return requests.get(base_url + current_location)
