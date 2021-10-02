from django.core.management.base import BaseCommand, CommandError
from django.db.models.fields import NullBooleanField
from api.models import StaticWeapon
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
    inventory_item_definitions = current_manifest.json()['DestinyInventoryItemDefinition']

    '''List comprehension returning only weapon objects of weapons that are 
    randomly rollable'''
    weapons_list = [
                    inventory_item_definitions[item] for
                    item in 
                    inventory_item_definitions if
                    inventory_item_definitions[item]['itemType'] == 3 and
                    inventory_item_definitions[item].get('collectibleHash', False) and
                    inventory_item_definitions[item]['inventory']['tierType'] > 4 and
                    inventory_item_definitions[item].get('iconWatermark', False) and
                    inventory_item_definitions[item]['sockets']['socketEntries'][1]['reusablePlugItems'] != []
                    ]
    
    for weapon in weapons_list:
      # Direct paths to displayProperties, inventory, quality, socketEntries and equippingBlock
      display_properties = weapon['displayProperties']
      inventory = weapon['inventory']
      quality = weapon['quality']
      socket_entries = weapon['sockets']['socketEntries']
      equipping_block = weapon['equippingBlock']

      # Determining the weapon's equippable slot (Kinetic, Energy, Power)
      if inventory['bucketTypeHash'] == 1498876634:
        slot_type = 'Kinetic'
      elif inventory['bucketTypeHash'] == 2465295065:
        slot_type = 'Energy'
      else: # inventory['bucketTypeHash'] == 953998645
        slot_type = 'Power'

      # Determining the weapon's ammo type (Primary, Special or Heavy)
      if equipping_block['ammoType'] == 1:
        ammo_type = 'Primary'
      elif equipping_block['ammoType'] == 2:
        ammo_type = 'Special'
      else: # equipping_block['ammoType'] == 3
        ammo_type = 'Heavy'

      # Determining the weapon's damage type (Kinetic, Arc, Solar, Stasis, Void)
      if weapon['defaultDamageType'] == 1:
        damage_type = 'Kinetic'
      elif weapon['defaultDamageType'] == 2:
        damage_type = 'Arc'
      elif weapon['defaultDamageType'] == 3:
        damage_type = 'Solar'
      elif weapon['defaultDamageType'] == 4:
        damage_type = 'Void'
      else: # weapon['defaultDamageType'] == 6
        damage_type = 'Stasis'

      # Determining the plug set hashes for each column if they exist
      # Column one
      if socket_entries[1]['randomizedPlugSetHash']:
        column_one_hash = socket_entries[1]['randomizedPlugSetHash']
      else:
        column_one_hash = None
      # Column two
      if socket_entries[2]['randomizedPlugSetHash']:
        column_two_hash = socket_entries[2]['randomizedPlugSetHash']
      else:
        column_two_hash = None
      # Column three
      if socket_entries[3]['randomizedPlugSetHash']:
        column_three_hash = socket_entries[3]['randomizedPlugSetHash']
      else:
        column_three_hash = None
      # Column four
      if socket_entries[4]['randomizedPlugSetHash']:
        column_four_hash = socket_entries[4]['randomizedPlugSetHash']
      else:
        column_four_hash = None

      # Creates a StaticWeapon object for the current weapon
      StaticWeapon.objects.create(
        hash = weapon['hash'],
        name = display_properties['name'],
        icon = display_properties['icon'],
        flavor_text = weapon['flavorText'],
        tier_type = inventory['tierTypeName'],
        weapon_type = weapon['itemTypeDisplayName'],
        slot_type = slot_type,
        ammo_type = ammo_type,
        damage_type = damage_type,
        watermark_icons = quality['displayVersionWatermarkIcons'],
        column_one_hash = column_one_hash,
        column_two_hash = column_two_hash,
        column_three_hash = column_three_hash,
        column_four_hash = column_four_hash,
      )
