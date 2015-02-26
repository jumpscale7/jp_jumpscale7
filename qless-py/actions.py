from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def init(self,serviceobject):
        instance=serviceobject.hrd.get("param.redis.instance")
        
        jpredis=j.atyourservice.get(name="redis",instance=instance,node=serviceobject.node)
        serviceobject.hrd.set("param.redis.host","localhost")
        serviceobject.hrd.set("param.redis.port", jpredis.hrd.get("param.port"))
        return True

    def configure(self,serviceobject):
        j.system.fs.changeDir("$(system.paths.base)/apps/qless-core/")
        j.do.execute("make qless.lua")
