import requests
from environ import Env

from api.models import Plug, PlugSet, StaticWeapon
from api.watermarks import watermark_list, relevant_watermark_list, seasons_dictionary, expansions_dictionary

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


def create_or_update_plugs(inventory_item_definitions):
	# Plug display names to help narrow down the plugs to keep
	item_display_names = [
		'Barrel', 'Sight', 'Magazine', 'Stock', 'Trait', 'Blade', 'Battery', 'Guard', 'Launcher Barrel', 'Bowstring',
		'Arrow', 'Scope', 'Haft', 'Grip', 'Enhanced Trait', 'Origin Trait'
	]

	# List comprehension returning only plug objects of plugs that weapon
	# plug sets can roll
	plugs_list = [inventory_item_definitions[item] for item in inventory_item_definitions if
	              inventory_item_definitions[item].get('itemTypeDisplayName', False) and
	              inventory_item_definitions[item]['itemTypeDisplayName'] in item_display_names and
	              inventory_item_definitions[item]['inventory']['bucketTypeHash'] == 1469714392 and
	              inventory_item_definitions[item]['displayProperties'].get('icon', False)]

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


def create_or_update_plugsets(plug_set_definitions):
	# TODO What was this for? Doesn't seem to be used anywhere. (MV 2/18/24)
	# single_plug_plugset_hashes = [405, 408, 411, 503, 1443, 1445, 1447]

	"""List comprehension returning only weapon objects of weapons that are randomly rollable"""
	plug_set_list = [plug_set_definitions[item] for
	                 item in
	                 plug_set_definitions if
	                 plug_set_definitions[item]['redacted'] is False]

	for plug_set in plug_set_list:
		plug_set_hash = plug_set['hash']
		plug_hashes = [item['plugItemHash'] for
		               item in
		               plug_set['reusablePlugItems'] if
		               item.get('currentlyCanRoll', False) is not False]

		if PlugSet.objects.filter(hash=plug_set_hash).exists():
			plug_set_to_get = PlugSet.objects.get(hash=plug_set_hash)
			for plug in plug_set_to_get.reusable_plug_items.all():
				if plug.hash not in plug_hashes:
					plug_to_get = Plug.objects.get(hash=plug.hash)
					print(f'Updating PlugSet {plug_set_hash} removing Plug hash {plug.hash}')
					plug_set_to_get.reusable_plug_items.remove(plug_to_get)

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


def create_or_update_static_weapons(inventory_item_definitions, collectible_definitions):
	"""List comprehension returning only weapon objects of weapons that are randomly roll-able"""
	weapons_list = [
		inventory_item_definitions[item] for item in inventory_item_definitions if
		inventory_item_definitions[item]['itemType'] == 3 and
		inventory_item_definitions[item]['inventory']['tierType'] > 4 and
		inventory_item_definitions[item].get('iconWatermark', False) and
		len(inventory_item_definitions[item]['sockets']['socketEntries']) >= 2 and
		inventory_item_definitions[item]['sockets']['socketEntries'][1]['reusablePlugItems'] != []
	]

	weapon_hash_list = [item['hash'] for item in weapons_list]

	collections_list = [
		collectible_definitions[item] for
		item in
		collectible_definitions if collectible_definitions[item]['itemHash'] in weapon_hash_list
	]

	collections_hash_list = [item['itemHash'] for item in collections_list]

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
		else:  # inventory['bucketTypeHash'] == 953998645
			slot_type = 'Power'

		# Determining the weapon's ammo type (Primary, Special or Heavy)
		if equipping_block['ammoType'] == 1:
			ammo_type = 'Primary'
		elif equipping_block['ammoType'] == 2:
			ammo_type = 'Special'
		else:  # equipping_block['ammoType'] == 3
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
		else:  # weapon['defaultDamageType'] == 6
			damage_type = 'Stasis'

		# Determining if the weapon has a non-sunset version
		if quality['versions'][-1]['powerCapHash'] > 1862490585:
			sunset = False
		else:
			sunset = True

		single_plug_plugset_hashes = [390, 393, 396, 405, 408, 411, 503, 1443, 1445, 1447]

		# Finding the PlugSet for column one
		if socket_entries[1].get('randomizedPlugSetHash') is not None and PlugSet.objects.filter(
				hash=socket_entries[1]['randomizedPlugSetHash']).exists():
			column_one_set = PlugSet.objects.get(hash=socket_entries[1]['randomizedPlugSetHash'])
		else:
			column_one_set = None

		# Finding the PlugSet for column two
		if socket_entries[2].get('randomizedPlugSetHash') is not None and PlugSet.objects.filter(
				hash=socket_entries[2]['randomizedPlugSetHash']).exists():
			column_two_set = PlugSet.objects.get(hash=socket_entries[2]['randomizedPlugSetHash'])
		elif socket_entries[2].get('reusablePlugSetHash') is not None and socket_entries[2].get(
				'reusablePlugSetHash', None) in single_plug_plugset_hashes:
			column_two_set = PlugSet.objects.get(hash=socket_entries[2]['reusablePlugSetHash'])
		else:
			column_two_set = None

		# Finding the PlugSet for column three
		if socket_entries[3].get('randomizedPlugSetHash') is not None and PlugSet.objects.filter(
				hash=socket_entries[3]['randomizedPlugSetHash']).exists():
			column_three_set = PlugSet.objects.get(hash=socket_entries[3]['randomizedPlugSetHash'])
		elif socket_entries[3].get('reusablePlugSetHash') is not None and socket_entries[3].get(
				'reusablePlugSetHash', None) in single_plug_plugset_hashes:
			column_three_set = PlugSet.objects.get(hash=socket_entries[3]['reusablePlugSetHash'])
		else:
			column_three_set = None

		# Finding the PlugSet for column four
		if socket_entries[4].get('randomizedPlugSetHash') is not None and PlugSet.objects.filter(
				hash=socket_entries[4]['randomizedPlugSetHash']).exists():
			column_four_set = PlugSet.objects.get(hash=socket_entries[4]['randomizedPlugSetHash'])
		else:
			column_four_set = None

		# Finding the PlugSet for potential Origin Trait
		if len(socket_entries) > 8:
			if socket_entries[8].get('randomizedPlugSetHash') is not None and PlugSet.objects.filter(
					hash=socket_entries[8]['randomizedPlugSetHash']).exists():
				origin_trait_set = PlugSet.objects.get(hash=socket_entries[8]['randomizedPlugSetHash'])
			elif socket_entries[8].get('reusablePlugSetHash') is not None and PlugSet.objects.filter(
					hash=socket_entries[8]['reusablePlugSetHash']).exists():
				origin_trait_set = PlugSet.objects.get(hash=socket_entries[8]['reusablePlugSetHash'])
			else:
				origin_trait_set = None
		else:
			origin_trait_set = None

		current_watermark = None
		for watermark in watermark_list:
			if watermark in quality['displayVersionWatermarkIcons']:
				current_watermark = watermark
				break

		original_watermark = None
		for watermark in reversed(watermark_list):
			if watermark in quality['displayVersionWatermarkIcons']:
				original_watermark = watermark
				break

		original_nonsunset_watermark = None
		for watermark in reversed(relevant_watermark_list):
			if watermark in quality['displayVersionWatermarkIcons']:
				original_nonsunset_watermark = watermark
				break

		current_season = None
		if current_watermark:
			current_season = seasons_dictionary[current_watermark]

		original_season = None
		if original_watermark:
			original_season = seasons_dictionary[original_watermark]

		original_nonsunset_season = None
		if original_nonsunset_watermark:
			original_nonsunset_season = seasons_dictionary[original_nonsunset_watermark]

		original_nonsunset_expansion = None
		original_expansion = None
		current_expansion = None
		for expansion in expansions_dictionary.keys():
			if current_season in expansions_dictionary[expansion]:
				current_expansion = expansion
			if original_season in expansions_dictionary[expansion]:
				original_expansion = expansion
			if original_nonsunset_season in expansions_dictionary[expansion]:
				original_nonsunset_expansion = expansion

		if weapon['hash'] in collections_hash_list:
			source_hash = [item['sourceHash'] for item in collections_list if item['itemHash'] == weapon['hash']][0]
			source_string = \
				[item['sourceString'] for item in collections_list if item['itemHash'] == weapon['hash']][
					0].replace("Source: ", "")
		else:
			source_hash = 1234567890
			source_string = ""

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
				hash=weapon['hash'],
				name=display_properties['name'],
				icon=display_properties['icon'],
				flavor_text=weapon['flavorText'],
				tier_type=inventory['tierTypeName'],
				weapon_type=weapon['itemTypeDisplayName'],
				slot_type=slot_type,
				ammo_type=ammo_type,
				damage_type=damage_type,
				watermark_icons=quality['displayVersionWatermarkIcons'],
				current_watermark=current_watermark,
				original_watermark=original_watermark,
				original_nonsunset_watermark=original_nonsunset_watermark,
				season_information={
					'original_season': original_season,
					'original_expansion': original_expansion,
					'current_season': current_season,
					'current_expansion': current_expansion,
					'original_nonsunset_season': original_nonsunset_season,
					'original_nonsunset_expansion': original_nonsunset_expansion
				},
				index=weapon['index'],
				is_sunset=sunset,
				source_hash=source_hash,
				source_string=source_string,
				column_one_hash=column_one_set,
				column_two_hash=column_two_set,
				column_three_hash=column_three_set,
				column_four_hash=column_four_set,
				origin_trait_hash=origin_trait_set
			)
			print(f'Created "{new_weapon.name}"')
