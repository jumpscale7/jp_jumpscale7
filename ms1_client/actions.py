from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    """
    """


    def configure(self,serviceobject):
        """
        configure ms1
        """
        import JumpScale.lib.ms1

        secret=j.tools.ms1.getCloudspaceSecret("$(param.login)","$(param.passwd)","$(param.cloudspace)","$(param.location)")

        #this remembers the secret required to use ms1
        serviceobject.hrd.set("param.secret",secret)

        return True

