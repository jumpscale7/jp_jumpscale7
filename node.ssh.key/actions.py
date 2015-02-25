from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will install a node over ssh
        """
        def update():
            j.do.execute("apt-get update")
        j.actions.start(name="update",description='update', action=update, stdOutput=True, serviceObj=serviceObj)

        def upgrade():
            j.do.execute("apt-get upgrade -y")
        j.actions.start( name="upgrade",description='upgrade', action=upgrade, stdOutput=True, serviceObj=serviceObj)
        def extra():
            j.do.execute("apt-get install byobu curl -y")
        j.actions.start(name="extra",description='extra', action=extra, stdOutput=True, serviceObj=serviceObj)

        def jumpscale():
            j.do.execute("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            j.do.execute("sh /tmp/installjs.sh")
        j.actions.start(name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, serviceObj=serviceObj)

        return True


    def removedata(self,serviceObj):
        """
        delete vmachine
        """
        j.do.execute("killall tmux;killall python;echo")
        j.do.execute("rm -rf /opt")
        return True

    def execute(self,serviceObj):
        """
        execute over ssh something onto the machine
        """
        # if "cmd" not in serviceObj.args:
        #     raise RuntimeError("cmd need to be in args, example usage:jpackage execute -n node.ssh.key -i ovh5 --data=\"cmd:'ls /'\"")

        # cl = j.atyourservice.remote.sshPython(serviceObj=serviceObj,node=serviceObj.instance)
        # cmd = serviceObj.args['cmd']
        # cl.connection.run(cmd)

        return True

