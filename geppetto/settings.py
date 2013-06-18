import os
import logging
import ConfigParser


def load_puppet_configs(configs_dir=None):

	if not configs_dir:
		base = os.path.dirname(__file__)
		configs_path = os.path.abspath(os.path.join(base, 'puppets'))

	config = ConfigParser.RawConfigParser(allow_no_value=True)
	puppet_configs = [os.path.join(configs_path,f) for f in os.listdir(configs_path)]

	puppets = {}
	for puppet in puppet_configs:
		config.read(puppet)
		try:
			name = config.get('main', 'name')
		except:
			logging.error('Config %s does not contain Section "%s" with variable "%s" ' % (puppet, 'main', 'name') )
		puppets[name] = {}
		for section in config.sections():
			puppets[name][section] = dict(config.items(section))

	logging.info("Loaded Configs for %s" % puppets.keys())
	print("Loaded Configs for %s" % puppets.keys())
	return puppets

# Get Puppet Configs
PUPPETS = load_puppet_configs()
print PUPPETS
