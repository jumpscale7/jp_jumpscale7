from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,**args):
        """
        will install a node over ssh
        """
        def update():
            self.execute(cmd="apt-get update")
        j.action.start(retry=2, name="update",description='update', action=update, stdOutput=True, jp=self.jp_instance)

        def upgrade():
            self.execute(cmd="apt-get upgrade -y")
        j.action.start(retry=2, name="upgrade",description='upgrade', action=upgrade, stdOutput=True, jp=self.jp_instance)

        def jumpscale():
            self.execute(cmd="curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            self.execute(cmd="sh /tmp/installjs.sh")
        j.action.start(retry=1, name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, jp=self.jp_instance)

        def extra():
            self.execute(cmd="apt-get install byobu -y")
        j.action.start(retry=1, name="extra",description='extra', action=extra, stdOutput=True, jp=self.jp_instance)


        return True


    def removedata(self,**args):
        """
        delete vmachine
        """
        self.execute(cmd="killall tmux;killall python;echo")
        self.execute(cmd="rm -rf /opt")
        return True

    def execute(self,**args):
        """
        execute over ssh something onto the machine
        """
        ip = self.jp_instance.hrd.get("param.machine.ssh.ip")
        port = self.jp_instance.hrd.get("param.machine.ssh.port")

        keyhrd=j.application.getAppInstanceHRD("sshkey",'$(param.ssh.key.name)')
        keypath="/tmp/$(param.ssh.key.name).privkey"
        j.do.writeFile(keypath,keyhrd.get("param.ssh.key.priv"))

        j.remote.cuisine.fabric.env["key_filename"] = keypath
        cl=j.remote.cuisine.connect(ip,port)

        if "cmd" not in args:
            raise RuntimeError("cmd need to be in args, example usage:jpackage execute -n node.ssh.key -i ovh5 --data=\"cmd:'ls /'\"")

        if "shell" in args:
            #can pass something to lua or jumpscale
            pass
        else:
            cl.run(''.join(args['cmd']))

        #clean priv key from memory
        del j.remote.cuisine.fabric.env["key_filename"]
        j.do.delete(keypath)

        return True
        
