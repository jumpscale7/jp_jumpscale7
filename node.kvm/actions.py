from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def _getHostClient(self):
        hostJP = j.atyourservice.get(name="$(param.hostnode.type)",instance="$(param.hostnode.instance)")
        cl = j.atyourservice.remote.sshPython(hostJP, '$(param.hostnode.instance)')
        return cl

    def configure(self,serviceobject):
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
        serviceobject.hrd.set("param.machine.ssh.key",key)
        C="""
import JumpScale.lib.kvm
config = j.system.platform.kvm.getConfig("$(param.name)")
print config
"""
        config = cl.executeCode(C)
        vmHRD = j.core.hrd.get(content=config)
        serviceobject.hrd.set("param.machine.ssh.ip",vmHRD.get("bootstrap.ip"))
        serviceobject.hrd.set("param.machine.ssh.login",vmHRD.get("bootstrap.login"))
        serviceobject.hrd.set("param.machine.ssh.passwd",vmHRD.get("bootstrap.passwd"))
        return True


    def removedata(self,serviceobject):
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
