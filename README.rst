Geppetto
##################

Deploy, Install and Administrate your Amazon Infrastructure fast

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

Sample Python Usage
--------------------
::

        from geppetto import PuppetMaster

        # makes and installs puppet
        puppet = PuppetMaster.create_puppet('example_puppet')
        print "Puppet details: %s" % (puppet.instance)


