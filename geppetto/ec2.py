import time
import socket
import logging

from boto.ec2.connection import EC2Connection


class EC2Conn:

	def __init__(self, config):
		self.conn = None
		self.config = config


	def connect(self):
		self.conn = EC2Connection(self.config['aws']['aws_key'],
								  self.config['aws']['aws_secret'])

	
	def verify_ssh(self, host):
		"""Confirm ability to SSH before returning"""
		attempts = 0

		while attempts < 25:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((host,22))
				s.shutdown(2)
				return True
			except:
				print "Launching Instance... Current Status: Attempting to SSH" 
				time.sleep(5)
				attempts+=1
		
		logging.error("Failed to SSH into %s:22 after 25 tries." % host)
		return False

	def create_instance(self):
		server_config = {
				'image_id' : self.config['aws']['image_id'],
				'instance_type' : self.config['aws']['instance_type'],
				'security_groups' : self.config['aws']['security_groups'].split(","),
				'key_name' : self.config['aws']['key_name'],
		}

		reservation = self.conn.run_instances(**server_config)
		instance = reservation.instances[0]

		while instance.state != 'running':
			time.sleep(15)
			instance.update()
			print "Launching Instance... Amazon Status: %s" % (instance.state)

		# Connect via SSH
		self.verify_ssh(instance.public_dns_name)

		# Add config details to Puppet
		instance.config = self.config

		print "instance %s done!" % (instance.id)

		return instance

	def link_instance_and_ip(self, instance_id, ip):
		success = self.conn.associate_address(instance_id=instance_id,
									public_ip=ip)
		if success: 
			print "Sleeping for 60 seconds to let IP attach"
			time.sleep(60)

		return success

	def unlink_instance_and_ip(self, instance_id, ip):
		return self.conn.disassociate_address(instance_id=instance_id,
									public_ip=ip)

	def get_instances(self):
		return self.conn.get_all_instances()


