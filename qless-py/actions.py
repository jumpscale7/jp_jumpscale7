from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    def init(self,**args):
        instance=self.jp_instance.hrd.get("param.redis.instance")
        
        jpredis=j.packages.get(name="redis",instance=instance,node=self.jp_instance.node)
        self.jp_instance.hrd.set("param.redis.host","localhost")
        self.jp_instance.hrd.set("param.redis.port", jpredis.hrd.get("param.port"))
        return True

    def configure(self,**args):
        j.system.fs.changeDir("$(system.paths.base)/apps/qless-core/")
        j.do.execute("make qless.lua")
