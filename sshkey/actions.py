from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def prepare(self, serviceObj):
        if serviceObj.hrd.get("instance.ssh.key.priv").strip() == "":
            self._generateKeys(serviceObj)
        elif serviceObj.hrd.get("instance.ssh.key.pub"):
            privkey = serviceObj.hrd.get("instance.ssh.key.priv")
            j.do.writeFile("/tmp/privkey", privkey)
            j.do.chmod('/tmp/privkey', 0o600)
            cmd = 'ssh-keygen -f /tmp/privkey -y -N \'\'> \'/tmp/pubkey\''
            j.do.execute(cmd)
            j.do.chmod('/tmp/pubkey', 0o600)
            pubkey = j.do.readFile('/tmp/pubkey')
            serviceObj.hrd.set("instance.ssh.key.pub", pubkey)


    def _generateKeys(self,serviceObj):
        keyloc = "/tmp/id_dsa"
        j.system.process.executeWithoutPipe("ssh-keygen -t dsa -f %s" % keyloc)
        if not j.system.fs.exists(path=keyloc):
            raise RuntimeError("cannot find path for key %s, was keygen well executed" % keyloc)

        key = j.system.fs.fileGetContents(keyloc)
        keypub = j.system.fs.fileGetContents(keyloc + ".pub")

        serviceObj.hrd.set("instance.ssh.key.pub", keypub)
        serviceObj.hrd.set("instance.ssh.key.priv", key)

    def configure(self, serviceObj):
        """
        create key
        """

        if serviceObj.hrd.get("instance.ssh.key.priv").strip() == "":
            self._generateKeys(serviceObj)

        return True

    def removedata(self, serviceObj):
        """
        remove key data
        """
        pass