import time
import os
import traceback

from fabric.api import env
from fabric.api import sudo, put, cd
from fabric.exceptions import NetworkError

import ec2
import modules
import settings
import logging


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
		pass

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

	def create(self):
		env.key_filename = os.path.join(self.config['aws']['aws_key_path'], self.config['aws']['key_name'])
		ec2conn = ec2.EC2Conn(self.config)
		ec2conn.connect()
		self.instance = ec2conn.create_instance()

	def ssh(self):

		# Set Fabric Env Host String
		env.host_string = "ec2-user@%s" % (self.instance.ip_address) 

		print "Implement Connect function"
		return False


class PuppetMaster(object):
	"""A Singleton Object"""

	@classmethod
	def create_puppet(cls, config_name):
		
		try:
			config = settings.PUPPETS[config_name]
		except KeyError as e:
			logging.error("Could not find config '%s'" % config_name)
		print config

		puppet = EC2Puppet(config)
		puppet.create()

		# Install
		if puppet.connect():
			cls.install_puppet()

		return puppet

	@classmethod
	def install_puppet(cls):

		print "Doing Installation on %s" % env.host_string

		# Create User
		user = cls.config['name']
		remote_home_dir = os.path.join('home',user)
		with settings(warn_only=True):
			sudo('useradd -U -m %s' % user)
		
		remote_code_dir = os.path.join(remote_home_dir, 'app')
		with settings(warn_only=True):
			sudo('mkdir %s' % remote_code_dir)

		# Install packages with yum
		if 'yum' in cls.config:
			sudo('yum install -y %s' % (" ".join(cls.config['yum'].keys())))

		# Install Python requirements with pip
		if 'pip_file' in cls.config:

			if not modules.pip.is_pip_installed():
				modules.pip.install_pip()

			if len(cls.config['pip_file'].keys()) > 0:
				file_name = cls.config['pip_file'].keys()[0]
				put(file_name, remote_home_dir, use_sudo=True)
				sudo('pip install -r %s ' % file_name)
			else:
				logging.error("Config Error: You must include a file name if using the 'pip_file' parameter. Ignoring")

		if 'pip_packages' in cls.config:

			if not modules.pip.is_pip_installed():
				modules.pip.install_pip()

			sudo('pip install %s ' % " ".join(cls.config['packages'].keys()))

		# Install Redis
		# TODO test
		if 'redis' in cls.config:
			modules.redis.install_redis()

			if not modules.pip.is_pip_installed():
				modules.pip.install_pip()
		
			sudo('pip install redis')

		# Install Supervisor
		# TODO test
		if 'supervisor' in cls.config:
			modules.supervisor.install_supervisor()



