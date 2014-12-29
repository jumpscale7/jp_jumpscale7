from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()


class Actions(ActionsBase):

    def removedata(self,**args):
        j.do.delete("/opt/code/luajit/",force=True)
        j.do.delete("/opt/luajit/",force=True)
        j.do.delete("/opt/code/github/torch/",force=True)

    def build(self,**args):

        #to reset the state use jpackage reset -n ...
        
        j.system.platform.ubuntu.check()
        def deps():

            j.system.platform.ubuntu.checkInstall(["cmake"], "cmake")
            j.system.platform.ubuntu.checkInstall(["gcc"], "gcc")


            for item in ["libreadline-dev","libzmq-dev","libsnappy1","libssl-dev","libzzip-dev","liblz-dev","zlib1g-dev"]:
                j.system.platform.ubuntu.install(item)

            try:
                j.do.copyFile("/usr/lib/libsnappy.so.1.2.1","$(param.base)/bin/libsnappy.so")
            except:
                pass
            j.do.delete("/usr/lib/libsnappy.so.1.2.1")

        j.action.start(retry=1, name="deps",description='install deps', cmds='', action=deps, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)    

    #NOT NEEDED ANYMORE IS PART OF LUAROCKS
    #     def luajitbuild():
    #         cmdstr="""
    # # set -ex
    # cd $(param.basebuild.luajit)
    # make
    # make install PREFIX=$(param.base)
    # """
    #         j.do.execute(cmdstr, outputStdout=True, outputStderr=True, timeout=240, errors=[], ok=[], captureout=True, dieOnNonZeroExitCode=True)

    #     j.action.start(retry=2, name="luajitbuild",description='', cmds='', action=luajitbuild, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)
            
        def buildluarocks():
            #build luarocks
            cmdstr="""
    #set -ex
    cd /opt/build/github.com/torch/luajit-rocks/
    mkdir -p build
    cd build
    cmake .. -DCMAKE_INSTALL_PREFIX=$(param.base)
    make install
    """
            j.do.execute(cmdstr, outputStdout=True, outputStderr=True, timeout=240, errors=[], ok=[], captureout=True, dieOnNonZeroExitCode=True)
            j.do.symlinkFilesInDir("$(param.base)/bin/", "/usr/local/bin/", delete=True)

        j.action.start(retry=2, name="buildluarocks",description='', cmds='', action=buildluarocks, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)
            

        toinstall=["penlight","fs","buffer","async","redis-async","parallel","trepl","readline","persist","sys","xlua","paths","pprint",\
            "redis-queue","redis-status","rq-monitor","thmap","sundown","strict","threads","utf8","util","lua-resty-snappy","lua-resty-libcjson",\
            "lua-resty-fileinfo","lua-resty-template","json","turbo","lustache","pgmoon","luazip","lanes","etlua","luaposix","lua-cjson",\
            "redis-lua","env","luasocket","lpeg","serpent","i18n","hdf5","md5","curl"]#,"lzlib"]

        for item in toinstall:
            cmd="luarocks install %s"%item
            j.action.start(retry=3, name="%s"%cmd,description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)

        cmd="luarocks build https://raw.github.com/leafo/sitegen/master/sitegen-dev-1.rockspec"
        j.action.start(retry=2, name="build sitegen",description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)

        j.do.symlinkFilesInDir("$(param.base)/bin/", "/usr/local/bin/", delete=True)

        cmd="curl https://raw.githubusercontent.com/uleelx/lupy/master/lupy.lua > $(param.base)/share/lua/5.1/lupy.lua"
        j.action.start(retry=2, name="install lupy",description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)


        # def cleanup():
        #     todelete=["$(param.base)/lib/pkgconfig/","$(param.base)/share/cmake/","$(param.base)/share/man/"]#,"$(param.base)/lib/luarocks/","$(param.base)/include/"
        #     for item in todelete:
        #         j.do.delete(item)
        # j.action.start(retry=1, name="cleanup",description='', cmds="", action=cleanup, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)

    def package(self,**args):
        j.do.delete("/opt/code/git/binary/luajit/luajit/",force=True)
        j.do.copyTree("/opt/luajit/","/opt/code/git/binary/luajit/luajit/")
