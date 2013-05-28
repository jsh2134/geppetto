import sys

try:
	from settings_local import aws_key, aws_secret, aws_key_path
	from settings_local import aws_key_pair, aws_security_group
except:
	print """Error: You need to create a settings_local.py file
				 with your amazon secret variables!"""
	sys.exit(1)

PROJECT_NAME = 'puppet'

# List of yum Packages to Install
YUM_PACKAGES = [ 
					#'make',
					#'nginx',
				]

# Pip Requirements file
PIP_REQS = 'requirements.txt'

# Here lie the Amazon secrets
AWS = {
			'secrets' : {
				'aws_key' : aws_key,
				'aws_secret': aws_secret,
				'aws_key_path': aws_key_path,
			},
			'defaults' : {
					'image_id' : 'ami-3d4ff254',       # Ubuntu Cloud 64-bit
					#'instance_type' : 'hi1.4xlarge',      # Big Boy
					'instance_type' : 't1.micro',      # Baby Boy
					'security_groups': [aws_security_group], 
					'key_name': aws_key_pair,
			}
}

