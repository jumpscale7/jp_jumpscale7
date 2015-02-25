from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

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
        def extra():
            self.execute(cmd="apt-get install byobu curl -y")
        j.action.start(retry=1, name="extra",description='extra', action=extra, stdOutput=True, jp=self.jp_instance)

        def jumpscale():
            self.execute(cmd="curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            self.execute(cmd="sh /tmp/installjs.sh")
        j.action.start(retry=1, name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, jp=self.jp_instance)

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
        if "cmd" not in self.jp_instance.args:
            raise RuntimeError("cmd need to be in args, example usage:jpackage execute -n node.ssh.key -i ovh5 --data=\"cmd:'ls /'\"")

        cl = j.atyourservice.remote.sshPython(jp=self.jp_instance,node=self.jp_instance.instance)
        cmd = self.jp_instance.args['cmd']
        cl.connection.run(cmd)

        return True

