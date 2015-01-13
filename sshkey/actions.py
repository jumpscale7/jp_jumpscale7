from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    
    def configure(self,**args):
        """
        create key
        """
        
        if self.jp_instance.hrd.get("param.ssh.key.priv").strip()=="":

            keyloc="/tmp/id_dsa"

            j.system.process.executeWithoutPipe("ssh-keygen -t dsa -f %s"%keyloc)            

            if not j.system.fs.exists(path=keyloc):
                raise RuntimeError("cannot find path for key %s, was keygen well executed"%keyloc)            

            key=j.system.fs.fileGetContents(keyloc)
            keypub=j.system.fs.fileGetContents(keyloc+".pub")

            
            self.jp_instance.hrd.set("param.ssh.key.pub",keypub)
            self.jp_instance.hrd.set("param.ssh.key.priv",key)
            
        return True
        
    def removedata(self,**args):
        """
        remove key data
        """
        pass