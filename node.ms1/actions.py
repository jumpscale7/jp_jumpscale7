from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import JumpScale.lib.ms1
import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,**args):
        """
        will install a node
        """
        
        ms1client_hrd=j.application.getAppInstanceHRD("ms1_client","$(param.ms1.connection)")

        spacesecret=ms1client_hrd.get("param.secret")

        def createmachine():

            machineid,ip,port=j.tools.ms1.createMachine(spacesecret, "$(param.name)", memsize="$(param.memsize)", \
                ssdsize=$(param.ssdsize), vsansize=0, description='',imagename="$(param.imagename)",delete=False)

            self.jp_instance.hrd.set("param.machine.id",machineid)
            self.jp_instance.hrd.set("param.machine.ssh.ip",ip)
            self.jp_instance.hrd.set("param.machine.ssh.port",port)


        j.action.start(retry=1, name="createmachine",description='createmachine', cmds='', action=createmachine, \
            actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)    


        def update():
            self.execute(cmd="apt-get update")
        j.action.start(retry=1, name="update",description='update', action=update, stdOutput=True, jp=self.jp_instance) 

        def upgrade():
            self.execute(cmd="apt-get upgrade -y")
        j.action.start(retry=1, name="upgrade",description='upgrade', action=upgrade, stdOutput=True, jp=self.jp_instance) 

        def jumpscale():
            self.execute(cmd="curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh | bash")
        j.action.start(retry=1, name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, jp=self.jp_instance) 

        return True
    

    def removedata(self,**args):
        """
        delete vmachine
        """
        ms1client_hrd=j.application.getAppInstanceHRD("ms1_client","$(param.ms1.connection)")
        spacesecret=ms1client_hrd.get("param.secret")
        j.tools.ms1.deleteMachine(spacesecret, "$(param.name)")

        return True
    
    def execute(self,**args):
        """
        execute over ssh something onto the machine
        """
        # self.jp_instance.hrd.set("param.machine.id",machineid)
        ip=self.jp_instance.hrd.get("param.machine.ssh.ip")
        port=self.jp_instance.hrd.get("param.machine.ssh.port")
        cl=j.remote.cuisine.connect(ip,port)

        if "cmd" not in args:
            raise RuntimeError("cmd need to be in args")

        if "shell" in args:
            #can pass something to lua or jumpscale
            pass
        else:
            cl.run(args["cmd"])

        return True
        