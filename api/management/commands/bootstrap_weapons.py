from django.core.management.base import BaseCommand

from .helpers import get_manifest, create_or_update_plugs, create_or_update_plugsets, create_or_update_static_weapons


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Get the manifest
        current_manifest = get_manifest()
        inventory_item_definitions = current_manifest.json()['DestinyInventoryItemDefinition']
        plug_set_definitions = current_manifest.json()['DestinyPlugSetDefinition']
        collectible_definitions = current_manifest.json()['DestinyCollectibleDefinition']

        create_or_update_plugs(inventory_item_definitions)
        create_or_update_plugsets(plug_set_definitions)
        create_or_update_static_weapons(inventory_item_definitions, collectible_definitions)
