import os, sys

import yaml
import logging

__config = {}
__loaded = False

lib_path = '/usr/etc/scada'
config_path = '/usr/etc/scada/config'

#Harry: I ADDED THIS
#yaml_name = 'config2.yaml'
yaml_name = 'config.yaml'

sys.path.append(lib_path)
sys.path.append(config_path)

new_config_path = os.path.dirname(__file__)

# Loads the YAML config file in a config structure

#HARRY: MADE IMPORTANT EDIT HERE
def load(forceLoad = False):
	global __config, __loaded
	
	if __loaded and not forceLoad:
		return
	
	#Harry: I changed this from having the config path to not
	# with open(config_path + "/" + yaml_name, 'r') as stream:
	with open(new_config_path + '/'  + yaml_name, 'r') as stream:
	# with open(os.eniron[])
		try:
			__config = yaml.safe_load(stream)
			__loaded = True
			logging.info('Successfully loaded config file')
			print ('LOADED CONFIG FILE IN config.py') #debug
		except yaml.YAMLError as exc:
			print(exc)


# Returns the value associated with the given key in the config structure
def get(key, default=None):
	global __config, __loaded
	
	if not __loaded:
		load()
	
	return __config.get(key, default)


# Returns a string dump of the entire config structure
def string_dump():
	global __config, __loaded
	
	if not __loaded:
		load()
	
	return yaml.dump(__config)

#HARRY: I ADDED THIS WHOLE THING
def write(key, value):
	global __config, __loaded

	if not __loaded:
		load()

	with open('new_' + yaml_name, 'w') as stream:
	# with open(os.eniron[])
		try:
			__config[key] = value
			yaml.dump(__config, stream)
		except yaml.YAMLError as exc:
			print(exc)
	
