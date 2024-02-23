from django.core.management.base import BaseCommand

from .helpers import get_manifest
from api.models import Plug


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Get the manifest
        current_manifest = get_manifest()
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
