from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def prepare(self, **args):
        if self.jp_instance.hrd.get("param.ssh.key.priv").strip() == "":
            self._generateKeys()
        elif self.jp_instance.hrd.get("param.ssh.key.pub"):
            privkey = self.jp_instance.hrd.get("param.ssh.key.priv")
            j.do.writeFile("/tmp/privkey", privkey)
            j.do.chmod('/tmp/privkey', 0o600)
            cmd = 'ssh-keygen -f /tmp/privkey -y -N \'\'> \'/tmp/pubkey\''
            j.do.execute(cmd)
            j.do.chmod('/tmp/pubkey', 0o600)
            pubkey = j.do.readFile('/tmp/pubkey')
            self.jp_instance.hrd.set("param.ssh.key.pub", pubkey)


    def _generateKeys(self):
        keyloc = "/tmp/id_dsa"
        j.system.process.executeWithoutPipe("ssh-keygen -t dsa -f %s" % keyloc)
        if not j.system.fs.exists(path=keyloc):
            raise RuntimeError("cannot find path for key %s, was keygen well executed" % keyloc)

        key = j.system.fs.fileGetContents(keyloc)
        keypub = j.system.fs.fileGetContents(keyloc + ".pub")

        self.jp_instance.hrd.set("param.ssh.key.pub", keypub)
        self.jp_instance.hrd.set("param.ssh.key.priv", key)

    def configure(self, **args):
        """
        create key
        """

        if self.jp_instance.hrd.get("param.ssh.key.priv").strip() == "":
            self._generateKeys()

        return True

    def removedata(self, **args):
        """
        remove key data
        """
        pass