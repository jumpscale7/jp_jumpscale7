from JumpScale import j
import time

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):
    def prepare(self, **kwargs):
        print "Installing nodejs & npm"
        print "To run nodejs, run /opt/nodejs/bin/node"
        print "To run npm, run /opt/nodejs/bin/npm"

