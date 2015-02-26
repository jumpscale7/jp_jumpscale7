from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def build(self,serviceobject):
        """
        instructions how to build the package
        build to /opt/lua
        """
        #BUILDLUA
        cmd="""
set -e
cd /opt/build/github.com/LuaDist/lua/
cp src/luaconf.h.orig src/luaconf.h
make linux
mkdir -p /opt/lua/
cp src/lua /opt/lua/
cp src/luac /opt/lua/
cp src/liblua.a /opt/lua/
# rm -rf /opt/build/github.com/LuaDist/lua/
"""
        j.action.start(retry=1, name="luabuild",description='compile lua', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=serviceobject)

    def package(self,serviceobject):
        """
        copy files to binary repo
        """
        j.do.copyTree("/opt/lua","/opt/code/git/binary/lua/lua")

