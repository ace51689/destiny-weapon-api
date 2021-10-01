from django.core.management.base import BaseCommand, CommandError
from api.models import StaticWeapon
import requests

class Command(BaseCommand):

  def handle(self, *args, **options):
    url = 'https://www.bungie.net/Platform/Destiny2/Manifest'
    headers = {'x-api-key': 'f5268091535243949c8bb6ace14cc3c3'}
    
    manifest = requests.get(url, headers=headers)
    current_location = manifest.json()['Response']['jsonWorldContentPaths']['en']
    base_url = 'https://www.bungie.net'
    
    current_manifest = requests.get(base_url + current_location)
    inventory_item_definitions = current_manifest.json()['DestinyInventoryItemDefinition']

    weapons_list = [
                    inventory_item_definitions[item] for
                    item in inventory_item_definitions if
                    inventory_item_definitions[item]['itemType'] == 3 and
                    inventory_item_definitions[item]
                    .get('collectibleHash', False) and
                    inventory_item_definitions[item]['inventory']['tierType'] 
                    > 4 and
                    inventory_item_definitions[item].get('iconWatermark', 
                    False) and
                    inventory_item_definitions[item]['sockets']
                    ['socketEntries'][1]['reusablePlugItems'] != []
                    ]
    
    for weapon in weapons_list:
      StaticWeapon.objects.create(
        hash = weapon['hash'],
        name = weapon['displayProperties']['name'],
        weapon_dict = weapon
      )
