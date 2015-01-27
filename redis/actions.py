from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):


    def prepare(self,**args):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        import JumpScale.baselib.redis
        j.clients.redis.deleteInstance(self.jp_instance.instance)
        return True
        
    def configure(self,**args):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        import JumpScale.baselib.redis
        appendonly=False
        if "$(param.disk)".lower().strip()=="true" or "$(param.disk)".strip()=="1":
            appendonly=True
        passwd = "$(param.passwd)".strip() or None
        j.clients.redis.configureInstance(self.jp_instance.instance,port=$(param.port),maxram=$(param.mem),appendonly=appendonly, passwd=passwd)
        return True
