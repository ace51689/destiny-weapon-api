from django.core.management.base import BaseCommand, CommandError
from api.models import PlugSet, Plug
import requests

class Command(BaseCommand):

  def handle(self, *args, **options):
    url = 'https://www.bungie.net/Platform/Destiny2/Manifest'
    headers = {'x-api-key': 'f5268091535243949c8bb6ace14cc3c3'}
    
    # Requesting the manifest
    manifest = requests.get(url, headers=headers)
    current_location = manifest.json()['Response']['jsonWorldContentPaths']['en']
    base_url = 'https://www.bungie.net'
    
    # Requesting the current manifest
    current_manifest = requests.get(base_url + current_location)
    plug_set_definitions = current_manifest.json()['DestinyPlugSetDefinition']

    '''List comprehension returning only weapon objects of weapons that are 
    randomly rollable'''
    plug_set_list = [plug_set_definitions[item] for item in plug_set_definitions if plug_set_definitions[item]['isFakePlugSet'] == False]

    for plug_set in plug_set_list:
  
      plug_set_hash = plug_set['hash']

      plug_hashes = [item['plugItemHash'] for item in plug_set['reusablePlugItems'] if item['currentlyCanRoll']]
      
      for plug_hash in plug_hashes:
                  
        # Updates PlugSet object if it already exists
        if Plug.objects.filter(hash=plug_hash).exists() and PlugSet.objects.filter(hash=plug_set_hash).exists():
          print(f'Updating PlugSet {plug_set_hash} with Plug hash {plug_hash}')
          plug_set_to_get = PlugSet.objects.get(hash=plug_set_hash)
          plug_to_get = Plug.objects.get(hash=plug_hash)
          if plug_to_get not in plug_set_to_get.reusable_plug_items.all():
            plug_set_to_get.reusable_plug_items.add(plug_to_get)
        
        
        # Creates PlugSet object if it doesn't already exist
        if Plug.objects.filter(hash=plug_hash).exists() and not PlugSet.objects.filter(hash=plug_set_hash).exists():
          print(f'Creating PlugSet {plug_set_hash} with initial Plug hash {plug_hash}')
          new_plug_set = PlugSet(hash=plug_set_hash)
          new_plug_set.save()
          new_plug_set.reusable_plug_items.add(Plug.objects.get(hash=plug_hash))