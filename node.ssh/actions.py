from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    
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
        