from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):
    
    def execute(self,**args):
        """
        execute over ssh something onto the machine
        """
        ip = self.jp_instance.hrd.get("param.machine.ssh.ip")
        port = self.jp_instance.hrd.get("param.machine.ssh.port")

        from IPython import embed
        print "DEBUG NOW ooo99"
        embed()
        
        j.remote.cuisine.fabric.env["key_filename"] = privkey
        cl=j.remote.cuisine.connect(ip,port)

        if "cmd" not in args:
            raise RuntimeError("cmd need to be in args")

        if "shell" in args:
            #can pass something to lua or jumpscale
            pass
        else:
            cl.run(''.join(args['cmd']))

        #clean priv key from memory
        del j.remote.cuisine.fabric.env["key_filename"]

        return True
        