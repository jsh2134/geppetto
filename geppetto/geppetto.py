import time
import os
import traceback

from fabric.api import env
from fabric.api import sudo, put, cd
from fabric.exceptions import NetworkError

import ec2
import settings


env.key_filename = settings.AWS['secrets']['aws_key_path']

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
				print "Failed to connect: used attempt %s of %s" % \
												(connect_attempts, self.MAX_ATTEMPTS)
				time.sleep(10)
			except:
				print "Failed to connect with error: %s" % (traceback.format_exc())
				return False
		

class EC2Puppet(Puppet):

	def __init__(self):
		self.cloud_type = Puppet.EC2

	def create(self):
		ec2conn = ec2.EC2Conn()
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
	def create_puppet(cls):

		puppet = EC2Puppet()
		puppet.create()

		# Install
		if puppet.connect():
			cls.install_puppet()

		return puppet

	@classmethod
	def install_puppet(cls):

		print "Doing Installation on %s" % env.host_string

		# Create User
		user = settings.PROJECT_NAME
		remote_home_dir = os.path.join('home',user)
		with settings(warn_only=True):
			sudo('useradd -U -m %s' % user)
		
		remote_code_dir = os.path.join(remote_home_dir, 'app')
		with settings(warn_only=True):
			sudo('mkdir %s' % remote_code_dir)

		# Install packages with yum
		sudo('yum install -y %s' % (" ".join(settings.YUM_PACKAGES)))

		# Install Python requirements with pip
		put(settings.PIP_REQS, remote_home_dir, use_sudo=True)

