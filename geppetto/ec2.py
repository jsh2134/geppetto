from boto.ec2.connection import EC2Connection
from settings import AWS

import time


SERVER = {
		'image_id' : AWS['defaults']['image_id'],
		'instance_type' : AWS['defaults']['instance_type'],
		'security_groups' : AWS['defaults']['security_groups'],
		'key_name' : AWS['defaults']['key_name'],
}


class EC2Conn:

	def __init__(self):
		self.conn = None


	def connect(self):
		self.conn = EC2Connection(AWS['secrets']['aws_key'],
								  AWS['secrets']['aws_secret'])

	def create_instance(self):
		reservation = self.conn.run_instances( **SERVER)
		instance = reservation.instances[0]

		while instance.state != 'running':
			time.sleep(5)
			instance.update()
			print "Instance state: %s" % (instance.state)
		
		# Sleep for a bit more before trying to connect
		time.sleep(60)

		print "instance %s done!" % (instance.id)

		return instance

	def link_instance_and_ip(self, instance_id, ip):
		success = self.conn.associate_address(instance_id=instance_id,
									public_ip=ip)
		if success: 
			print "Sleeing for 60 seconds to let IP attach"
			time.sleep(60)

		return success

	def unlink_instance_and_ip(self, instance_id, ip):
		return self.conn.disassociate_address(instance_id=instance_id,
									public_ip=ip)

	def get_instances(self):
		return self.conn.get_all_instances()


