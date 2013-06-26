import time
import os
import sys
import traceback
import ConfigParser

from fabric.api import env
from fabric.api import settings, sudo, put, cd
from fabric.exceptions import NetworkError

import ec2
from modules import pip, supervisor
from modules.redis import redis
import logging


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


class Puppet(object):

	# Puppet Types
	EC2 = 1

	# Connection attempts
	MAX_ATTEMPTS = 3

	def __init__(self):
		self.instance = None
	
	def create(self):
		pass

	def ssh(self):
		try:
			env.host_string = "%s@%s" % (self.user, self.host)
		except Exception as e:
			logging.error("Failed to ssh to puppet with error: %s" % e)
			raise

	def connect(self):
		connect_attempts = 0
		while connect_attempts < self.MAX_ATTEMPTS:
			try:
				self.ssh()
				return True
			except NetworkError:
				connect_attempts += 1
				logging.warn("Failed to connect: used attempt %s of %s" % \
												(connect_attempts, self.MAX_ATTEMPTS))
				time.sleep(10)
			except:
				logging.error("Failed to connect with error: %s" % (traceback.format_exc()))
				return False
		

class EC2Puppet(Puppet):

	def __init__(self, config):
		self.cloud_type = Puppet.EC2
		self.config = config
		self.user = self.config['aws']['login_user']

	def create(self):
		env.key_filename = self.config['aws']['aws_key_path']
		ec2conn = ec2.EC2Conn(self.config)
		ec2conn.connect()
		self.instance = ec2conn.create_instance()

	def ssh(self):
		self.host = self.instance.public_dns_name
		return Puppet.ssh(self)
		


class PuppetMaster(object):
	"""A Singleton Object"""

	@classmethod
	def create_puppet(cls, config_name):
		puppets = load_puppet_configs()

		try:
			config = puppets[config_name]
		except KeyError:
			logging.error("Could not find config '%s'" % config_name)
			sys.exit(1)

		
		if 'aws' in config:
			puppet = EC2Puppet(config)
		else:
			puppet = Puppet(config)

		puppet.create()

		# Install
		if puppet.connect():
			cls.install_puppet(puppet)

		return puppet

	@classmethod
	def install_puppet(cls, puppet):

		print "Doing Installation on %s" % env.host_string

		# Create User
		user = puppet.config['main']['name']
		remote_home_dir = os.path.join(os.sep, 'home', user)
		with settings(warn_only=True):
			sudo('useradd -m --shell=/bin/bash %s' % user, pty=True)
		
		remote_code_dir = os.path.join(remote_home_dir, 'app')
		with settings(warn_only=True):
			sudo('mkdir %s' % remote_code_dir)

		# Install packages with yum
		if 'yum' in puppet.config:
			sudo('yum install -y %s' % (" ".join(puppet.config['yum'].keys())))

		# Install Python requirements with pip
		if 'pip_file' in puppet.config:

			if not pip.is_pip_installed():
				pip.install_pip()

			if len(puppet.config['pip_file'].keys()) > 0:
				file_name = puppet.config['pip_file'].keys()[0]
				put(file_name, remote_home_dir, use_sudo=True)
				sudo('pip install -r %s ' % file_name)
			else:
				logging.error("Config Error: You must include a file name if using the 'pip_file' parameter. Ignoring")

		if 'pip_packages' in puppet.config:

			if not pip.is_pip_installed():
				pip.install_pip()

			sudo('pip install %s ' % " ".join(puppet.config['pip_packages'].keys()))

		# Install Redis
		if 'redis' in puppet.config:
			redis.install_redis(puppet.config['redis'])

			if not pip.is_pip_installed():
				pip.install_pip()
		
			sudo('pip install redis')

		# Install Supervisor
		# TODO test
		"""if 'supervisor' in puppet.config:
			supervisor.install_supervisor()
		"""


