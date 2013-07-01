Geppetto
##################

Deploy, Install and Administrate your Amazon Infrastructure fast

Use geppetto to deploy servers (puppets) according to a pre-written config. Geppetto makes it easy to define server configs, yum packages, pip packages and other deployment and installation pieces. 


Sample Python Usage
--------------------
::

        from geppetto import PuppetMaster

        # makes and installs puppet
        puppet = PuppetMaster.create_puppet('example_puppet')
        
        # server is deployed and installed on based on config file
        print "Puppet details: %s" % (puppet.instance)

Sample Puppet Config 
--------------------

::

        [main]
        name=example_config
        [yum]
        nginx
        python-devel
        gcc
        make
        [pip_packages]
        pycrypto
        boto
        fabric
        [redis]
        port=6379
        # Amazon Web Services Details Here
        [aws]
        # Amazon Credentials here
        aws_key=YOUR-KEY
        aws_secret=YOUR-SECRET
        # Instance Specific Details here
        login_user=ec2-user
        # EBS-backed 64-bit Amazon Linux
        image_id=ami-05355a6c 
        instance_type=t1.micro


Status
-------
This is still a work in progress and most likely is broken right now. Moving towards a stable release.

Currently working on:

- installing everything under virtualenv
- verifying correct install of supervisor
- test suite
- stable release

Recently Completed:

- verifying correct install of redis
- defining multiple Puppet configs
- examples

