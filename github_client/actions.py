from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    """
    """

    def configure(self,serviceobject):
        j.application.config.set("whoami.email","$(github.client.email)")
        j.application.config.set("whoami.fullname","$(github.client.login)")
        j.application.config.set("whoami.git.login","$(github.client.login)")
        j.application.config.set("whoami.git.passwd","$(github.client.passwd)")

