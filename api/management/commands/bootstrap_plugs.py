import requests

from django.core.management.base import BaseCommand
from environ import Env

from api.models import Plug

env = Env()
Env.read_env()

API_KEY = env('API_KEY', default='temp')


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Defining the url and headers for our request
        url = 'https://www.bungie.net/Platform/Destiny2/Manifest'
        headers = {'x-api-key': API_KEY}

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
                              'Bowstring', 'Arrow', 'Scope', 'Haft', 'Grip',
                              'Enhanced Trait', 'Origin Trait']

        # List comprehension returning only plug objects of plugs that weapon
        # plug sets can roll
        plugs_list = [plugs[item] for item in plugs if
                      plugs[item].get('itemTypeDisplayName', False) and
                      plugs[item]['itemTypeDisplayName'] in item_display_names and
                      plugs[item]['inventory']['bucketTypeHash'] == 1469714392 and
                      plugs[item]['displayProperties'].get('icon', False)]

        for plug in plugs_list:
            display_properties = plug['displayProperties']

            if plug['itemTypeDisplayName'] == 'Enhanced Trait':
                plug_name = f"Enhanced {display_properties['name']}"
            else:
                plug_name = display_properties['name']

            # Updates Plug objects if they already exist
            if Plug.objects.filter(hash=plug['hash']).exists():
                plug_to_update = Plug.objects.get(hash=plug['hash'])

                if plug_to_update.name != plug_name:
                    plug_to_update.name = plug_name

                if plug_to_update.icon != display_properties['icon']:
                    plug_to_update.icon = display_properties['icon']

                if plug_to_update.description != display_properties['description']:
                    plug_to_update.description = display_properties['description']

                plug_to_update.save()
                print(f'Updated "{plug_to_update.name}" Plug object')

            else:
                # Creates Plug object if one doesn't already exist
                plug = Plug.objects.create(
                    hash=plug['hash'],
                    name=plug_name,
                    icon=display_properties['icon'],
                    description=display_properties['description']
                    )
                print(f'Created "{plug.name}" Plug object')

