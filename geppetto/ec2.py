import time
from boto.ec2.connection import EC2Connection


class EC2Conn:

	def __init__(self, config):
		self.conn = None
		self.config = config


	def connect(self):
		self.conn = EC2Connection(self.config['aws']['aws_key'],
								  self.config['aws']['aws_secret'])

	def create_instance(self):
		server_config = {
				'image_id' : self.config['aws']['image_id'],
				'instance_type' : self.config['aws']['instance_type'],
				'security_groups' : self.config['aws']['security_groups'],
				'key_name' : self.config['aws']['key_name'],
		}

		reservation = self.conn.run_instances(**server_config)
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


