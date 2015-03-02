from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    # def _getHostClient(self):
    #     hostJP = j.atyourservice.get(name="$(instance.hostnode.type)",instance="$(instance.hostnode.instance)")
    #     cl = j.atyourservice.remote.sshPython(hostJP, '$(instance.hostnode.instance)')
    #     return cl

    def configure(self,serviceobject):
        """
        will create a new virtual machine
        """
        import JumpScale.lib.kvm
        j.system.platform.kvm.create("$(instance.name)","$(instance.baseimage)")

        key = j.system.fs.fileGetContents("/root/.ssh/id_dsa")
        serviceobject.hrd.set("instance.machine.ssh.key",key)
        config = j.system.platform.kvm.getConfig("$(instance.name)")
        serviceobject.hrd.set("instance.machine.ssh.ip",config.get("bootstrap.ip"))
        serviceobject.hrd.set("instance.machine.ssh.login",config.get("bootstrap.login"))
        serviceobject.hrd.set("instance.machine.ssh.passwd",config.get("bootstrap.passwd"))
        return True


    def removedata(self,serviceobject):
        """
        delete vmachine
        """
        import JumpScale.lib.kvm
        j.system.platform.kvm.destroy("$(instance.name)")
        return True

    def execute(self,serviceobject, cmd):
        ip = serviceobject.hrd.get("instance.machine.ssh.ip")
        login = serviceobject.hrd.get("instance.machine.ssh.login")
        passwd = serviceobject.hrd.get("instance.machine.ssh.passwd")

        c = j.remote.cuisine
        if serviceobject.hrd.get("instance.baseimage") == "openwrt":
            c.fabric.env['shell'] = "/bin/ash -l -c"
        cl = c.connect(ip,22,passwd)
        cl.run(cmd)