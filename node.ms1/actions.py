from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.lib.ms1
import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,serviceobject):
        """
        will install a node
        """

        ms1client_hrd=j.application.getAppInstanceHRD("ms1_client","$(param.ms1.connection)")

        spacesecret=ms1client_hrd.get("param.secret")

        def createmachine():

            machineid,ip,port=j.tools.ms1.createMachine(spacesecret, "$(param.name)", memsize="$(param.memsize)", \
                ssdsize=$(param.ssdsize), vsansize=0, description='',imagename="$(param.imagename)",delete=False)

            serviceobject.hrd.set("param.machine.id",machineid)
            serviceobject.hrd.set("param.machine.ssh.ip",ip)
            serviceobject.hrd.set("param.machine.ssh.port",port)


        j.action.start(retry=1, name="createmachine",description='createmachine', cmds='', action=createmachine, \
            actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=serviceobject)


        def update():
            serviceobject.args['cmd'] = "apt-get update"
            self.execute()
        j.action.start(retry=1, name="update",description='update', action=update, stdOutput=True, jp=serviceobject)

        def upgrade():
            serviceobject.args['cmd'] = "apt-get upgrade -y"
            self.execute()
        j.action.start(retry=1, name="upgrade",description='upgrade', action=upgrade, stdOutput=True, jp=serviceobject)

        def jumpscale():
            serviceobject.args['cmd'] = "curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh; sh /tmp/installjs.sh"
            self.execute(cmd="")
        j.action.start(retry=1, name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, jp=serviceobject)

        return True


    def removedata(self,serviceobject):
        """
        delete vmachine
        """
        ms1client_hrd=j.application.getAppInstanceHRD("ms1_client","$(param.ms1.connection)")
        spacesecret=ms1client_hrd.get("param.secret")
        j.tools.ms1.deleteMachine(spacesecret, "$(param.name)")

        return True

    def execute(self,serviceobject):
        """
        execute over ssh something onto the machine
        """

        if "cmd" not in serviceobject.args:
            raise RuntimeError("cmd need to be in args, example usage:jpackage execute -n node.ssh.key -i ovh5 --data=\"cmd:'ls /'\"")

        cl = j.atyourservice.remote.sshPython(jp=serviceobject,node=serviceobject.instance)
        cmd = serviceobject.args['cmd']
        cl.connection.run(cmd)

        return True
