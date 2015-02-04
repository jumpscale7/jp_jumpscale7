from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    def _getHostClient(self):
        hostJP = j.packages.get(name="$(param.hostnode.type)",instance="$(param.hostnode.instance)")
        cl = j.packages.remote.sshPython(hostJP, '$(param.hostnode.instance)')
        return cl

    def configure(self,**args):
        """
        will create a new virtual machine
        """
        cl = self._getHostClient()
        C = """
import JumpScale.lib.kvm
j.system.platform.kvm.create("$(param.name)","$(param.baseimage)")
"""
        cl.executeCode(C)

        C="""
key = j.system.fs.fileGetContents("/root/.ssh/id_dsa")
print key
"""
        key = cl.executeCode(C)
        from ipdb import set_trace;set_trace()
        self.jp_instance.hrd.set("param.machine.ssh.key",key)
        C="""
config = j.system.platform.kvm.getConfig("$(param.name)")
print config
"""
        config = cl.executeCode(C)
        vmHRD = j.core.hrd.get(content=config)
        self.jp_instance.hrd.set("param.machine.ssh.ip",vmHRD.get("bootstrap.ip"))
        self.jp_instance.hrd.set("param.machine.ssh.port",vmHRD.get("bootstrap.port"))
        return True


    def removedata(self,**args):
        """
        delete vmachine
        """
        cl = self._getHostClient()
        C = """
import JumpScale.lib.kvm
j.system.platform.kvm.destroy("$(param.name)")
"""
        cl.executeCode(C)
        return True

    def execute(self,**args):
        """
        execute over ssh something onto the machine
        """
        cl = self._getHostClient()

        if "cmd" not in args:
            raise RuntimeError("cmd need to be in args, example usage:jpackage execute -n node.ssh.key -i ovh5 --data=\"cmd:'ls /'\"")

        if "shell" in args:
            #can pass something to lua or jumpscale
            pass
        else:
            cmd = ''.join(args['cmd'])
            C = """
from JumpScale import j
import JumpScale.lib.kvm
j.system.platform.kvm.execute(name='$(param.name)', cmd='%s')
            """ % cmd
            cl.executeCode(C)

        #clean priv key from memory
        del j.remote.cuisine.fabric.env["key"]

        return True
