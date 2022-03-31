from django.core.management.base import BaseCommand, CommandError
from api.models import StaticWeapon, PlugSet, Plug
from api.watermarks import watermark_list, relevent_watermark_list, seasons_dictionary, expansions_dictionary
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
    collectible_definitions = current_manifest.json()['DestinyCollectibleDefinition']

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

    weapon_hash_list = [item['hash'] for item in weapons_list]

    collections_list = [
      collectible_definitions[item] for
      item in
      collectible_definitions if collectible_definitions[item]['itemHash']
      in weapon_hash_list
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

      # Determining if the weapon has a non-sunset version
      if quality['versions'][-1]['powerCapHash'] > 1862490585:
        sunset = False
      else:
        sunset = True
      
      single_plug_plugset_hashes = [390, 393, 396, 405, 408, 411, 503, 1443, 1445, 1447]

      # Finding the PlugSet for column one
      if socket_entries[1].get('randomizedPlugSetHash', None) != None and PlugSet.objects.filter(hash=socket_entries[1]['randomizedPlugSetHash']).exists():
        column_one_set = PlugSet.objects.get(hash=socket_entries[1]['randomizedPlugSetHash'])
      else:
        column_one_set = None
      
      # Finding the PlugSet for column two
      if socket_entries[2].get('randomizedPlugSetHash', None) != None and PlugSet.objects.filter(hash=socket_entries[2]['randomizedPlugSetHash']).exists():
        column_two_set = PlugSet.objects.get(hash=socket_entries[2]['randomizedPlugSetHash'])
      elif socket_entries[2].get('reusablePlugSetHash', None) != None and socket_entries[2].get('reusablePlugSetHash', None) in single_plug_plugset_hashes:
        column_two_set = PlugSet.objects.get(hash=socket_entries[2]['reusablePlugSetHash'])
      else:
        column_two_set = None
      
      # Finding the PlugSet for column three
      if socket_entries[3].get('randomizedPlugSetHash', None) != None and PlugSet.objects.filter(hash=socket_entries[3]['randomizedPlugSetHash']).exists():
        column_three_set = PlugSet.objects.get(hash=socket_entries[3]['randomizedPlugSetHash'])
      elif socket_entries[3].get('reusablePlugSetHash', None) != None and socket_entries[3].get('reusablePlugSetHash', None) in single_plug_plugset_hashes:
        column_three_set = PlugSet.objects.get(hash=socket_entries[3]['reusablePlugSetHash'])
      else:
        column_three_set = None
      
      # Finding the PlugSet for column four
      if socket_entries[4].get('randomizedPlugSetHash', None) != None and PlugSet.objects.filter(hash=socket_entries[4]['randomizedPlugSetHash']).exists():
        column_four_set = PlugSet.objects.get(hash=socket_entries[4]['randomizedPlugSetHash'])
      else:
        column_four_set = None

      # Finding the PlugSet for potential Origin Trait
      if socket_entries[8].get('randomizedPlugSetHash', None) != None and PlugSet.objects.filter(hash=socket_entries[8]['randomizedPlugSetHash']).exists():
        origin_trait_set = PlugSet.objects.get(hash=socket_entries[8]['randomizedPlugSetHash'])
      elif socket_entries[8].get('reusablePlugSetHash', None) != None and PlugSet.objects.filter(hash=socket_entries[8]['reusablePlugSetHash']).exists():
        origin_trait_set = PlugSet.objects.get(hash=socket_entries[8]['reusablePlugSetHash'])
      else:
        origin_trait_set = None

      for watermark in watermark_list:
        if watermark in quality['displayVersionWatermarkIcons']:
          current_watermark = watermark
          break
        # print('No watermark found!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

      for watermark in reversed(watermark_list):
        if watermark in quality['displayVersionWatermarkIcons']:
          original_watermark = watermark
          break
      
      original_nonsunset_watermark = None
      for watermark in reversed(relevent_watermark_list):
        if watermark in quality['displayVersionWatermarkIcons']:
          original_nonsunset_watermark = watermark
          break
        
      current_season = seasons_dictionary[current_watermark]
      original_season = seasons_dictionary[original_watermark]

      original_nonsunset_season = None
      if original_nonsunset_watermark:
        original_nonsunset_season = seasons_dictionary[original_nonsunset_watermark]

      original_nonsunset_expansion = None
      for expansion in expansions_dictionary.keys():
        if current_season in expansions_dictionary[expansion]:
          current_expansion = expansion
        if original_season in expansions_dictionary[expansion]:
          original_expansion = expansion
        if original_nonsunset_season in expansions_dictionary[expansion]:
          original_nonsunset_expansion = expansion

      source_hash = [item['sourceHash'] for item in collections_list if item['itemHash'] == weapon['hash']][0]
      source_string = [item['sourceString'] for item in collections_list if item['itemHash'] == weapon['hash']][0].replace("Source: ", "")

      if StaticWeapon.objects.filter(hash=weapon['hash']).exists():
        # Updates StaticWeapon if it already exists
        weapon_to_update = StaticWeapon.objects.get(hash=weapon['hash'])
        print(f'Updating "{weapon_to_update.name}"')
        
        weapon_to_update.name = display_properties['name']
        weapon_to_update.icon = display_properties['icon']
        weapon_to_update.flavor_text = weapon['flavorText']
        weapon_to_update.tier_type = inventory['tierTypeName']
        weapon_to_update.weapon_type = weapon['itemTypeDisplayName']
        weapon_to_update.slot_type = slot_type
        weapon_to_update.ammo_type = ammo_type
        weapon_to_update.damage_type = damage_type
        weapon_to_update.watermark_icons = quality['displayVersionWatermarkIcons']
        weapon_to_update.current_watermark = current_watermark
        weapon_to_update.original_watermark = original_watermark
        weapon_to_update.original_nonsunset_watermark = original_nonsunset_watermark
        weapon_to_update.season_information = {
          'original_season': original_season,
          'original_expansion': original_expansion,
          'current_season': current_season,
          'current_expansion': current_expansion,
          'original_nonsunset_season': original_nonsunset_season,
          'original_nonsunset_expansion': original_nonsunset_expansion
        }
        weapon_to_update.index = weapon['index']
        weapon_to_update.is_sunset = sunset
        weapon_to_update.source_hash = source_hash
        weapon_to_update.source_string = source_string
        weapon_to_update.column_one_hash = column_one_set
        weapon_to_update.column_two_hash = column_two_set
        weapon_to_update.column_three_hash = column_three_set
        weapon_to_update.column_four_hash = column_four_set
        weapon_to_update.origin_trait_hash = origin_trait_set

        weapon_to_update.save()
        print(f'Updated "{weapon_to_update.name}"')
      else:
      # Creates a StaticWeapon object if one doesn't already exist
        new_weapon = StaticWeapon.objects.create(
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
          current_watermark = current_watermark,
          original_watermark = original_watermark,
          original_nonsunset_watermark = original_nonsunset_watermark,
          season_information = {
            'original_season': original_season,
            'original_expansion': original_expansion,
            'current_season': current_season,
            'current_expansion': current_expansion,
            'original_nonsunset_season': original_nonsunset_season,
            'original_nonsunset_expansion': original_nonsunset_expansion
          },
          index = weapon['index'],
          is_sunset = sunset,
          source_hash = source_hash,
          source_string = source_string,
          column_one_hash = column_one_set,
          column_two_hash = column_two_set,
          column_three_hash = column_three_set,
          column_four_hash = column_four_set,
          origin_trait_hash = origin_trait_set
        )
        print(f'Created "{new_weapon.name}"')
