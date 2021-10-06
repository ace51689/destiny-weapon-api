from django.core.management.base import BaseCommand, CommandError
from api.models import Plug
import requests

class Command(BaseCommand):

  def handle(self, *args, **options):
    # Defining the url and headers for our request
    url = 'https://www.bungie.net/Platform/Destiny2/Manifest'
    headers = {'x-api-key': 'f5268091535243949c8bb6ace14cc3c3'}
    
    # Requesting the manifest
    manifest = requests.get(url, headers=headers)
    current_location = manifest.json()['Response']['jsonWorldContentPaths']['en']
    base_url = 'https://www.bungie.net'
    
    # Requesting the current manifest
    current_manifest = requests.get(base_url + current_location)
    plugs = current_manifest.json()['DestinyInventoryItemDefinition']

    # Plug display names to help narrow down the plugs to keep
    item_display_names = ['Barrel', 'Sight', 'Magazine', 'Stock', 'Trait',
                          'Blade', 'Battery', 'Guard', 'Launcher Barrel',
                          'Bowstring', 'Arrow']

    # List comprehension returning only plug objects of plugs that weapon
    # plug sets can roll
    plugs_list = [plugs[item] for item in plugs if
                  plugs[item].get('itemTypeDisplayName', False) and
                  plugs[item]['itemTypeDisplayName'] in item_display_names and
                  plugs[item]['inventory']['bucketTypeHash'] == 1469714392 and
                  plugs[item]['displayProperties'].get('icon', False)]

    for plug in plugs_list:
      display_properties = plug['displayProperties']
      
      if Plug.objects.filter(hash=plug['hash']).exists():
        plug_to_update = Plug.objects.get(hash=plug['hash'])
        
        if plug_to_update.name != display_properties['name']:
          plug_to_update.name = display_properties['name']
        
        if plug_to_update.icon != display_properties['icon']:
          plug_to_update.icon = display_properties['icon']
        
        if plug_to_update.description != display_properties['description']:
          plug_to_update.description = display_properties['description']
        
        plug_to_update.save()
      
      else:
      
        Plug.objects.create(
          hash = plug['hash'],
          name = display_properties['name'],
          icon = display_properties['icon'],
          description = display_properties['description']
        )
