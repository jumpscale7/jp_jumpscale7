from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def prepare(self,**args):

        reset=True
        if reset:
            j.do.delete("/opt/code/luajit/",force=True)
            j.do.delete("/opt/code/github/torch/",force=True)

        j.system.platform.ubuntu.checkInstall(["cmake"], "cmake")
        j.system.platform.ubuntu.checkInstall(["gcc"], "gcc")

        def deps():
            for item in ["libreadline-dev","libzmq-dev","libsnappy1","libssl-dev","libzzip-dev","liblz-dev","zlib1g-dev"]:
                j.system.platform.ubuntu.install(item)

            try:
                j.do.copyFile("/usr/lib/libsnappy.so.1.2.1","$(param.base.luajit)/bin/libsnappy.so")
            except:
                pass
            j.do.delete("/usr/lib/libsnappy.so.1.2.1")

        j.action.start(retry=1, name="deps",description='install deps', cmds='', action=deps, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)



    def configure(self,**args):
        """
        """
        #build luajit
        self.build()

    def build(self,**args):

        def luajitbuild():
            cmdstr="""
    # set -ex
    cd $(param.basebuild.luajit)
    make
    make install PREFIX=$(param.base.luajit)
    """
            j.do.execute(cmdstr, outputStdout=True, outputStderr=True, timeout=240, errors=[], ok=[], captureout=True, dieOnNonZeroExitCode=True)

        j.action.start(retry=2, name="luajitbuild",description='', cmds='', action=luajitbuild, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)
            
        def buildluarocks():
            #build luarocks
            cmdstr="""
    #set -ex
    cd $(param.basebuild.luarocks)
    mkdir -p build
    cd build
    cmake .. -DCMAKE_INSTALL_PREFIX=$(param.base.luajit)
    make install
    """
            j.do.execute(cmdstr, outputStdout=True, outputStderr=True, timeout=240, errors=[], ok=[], captureout=True, dieOnNonZeroExitCode=True)
            j.do.symlinkFilesInDir("$(param.base.luajit)/bin/", "/usr/local/bin/", delete=True)

        j.action.start(retry=2, name="buildluarocks",description='', cmds='', action=buildluarocks, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)
            
            
        toinstall=["penlight","fs","buffer","async","redis-async","parallel","trepl","readline","persist","sys","xlua","paths","pprint",\
            "redis-queue","redis-status","rq-monitor","thmap","sundown","strict","threads","utf8","util","lua-resty-snappy","lua-resty-libcjson",\
            "lua-resty-fileinfo","lua-resty-template","json","turbo","lustache","pgmoon","luazip","lanes","etlua","luaposix","lua-cjson",\
            "redis-lua","readline","luasocket","lpeg","serpent","i18n","hdf5","md5","curl"]#,"lzlib"]


        for item in toinstall:
            cmd="luarocks install %s"%item
            j.action.start(retry=3, name="%s"%cmd,description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)

        cmd="luarocks build https://raw.github.com/leafo/sitegen/master/sitegen-dev-1.rockspec"
        j.action.start(retry=2, name="build sitegen",description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)

        j.do.symlinkFilesInDir("$(param.base.luajit)/bin/", "/usr/local/bin/", delete=True)

        cmd="curl https://raw.githubusercontent.com/uleelx/lupy/master/lupy.lua > $(param.base.luajit)/share/lua/5.1/lupy.lua"
        j.action.start(retry=2, name="install lupy",description='', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)

        def cleanup():
            todelete=["$(param.base.luajit)/include/","$(param.base.luajit)/lib/pkgconfig/","$(param.base.luajit)/share/cmake/","$(param.base.luajit)/share/man/"]#,"$(param.base.luajit)/lib/luarocks/"
            for item in todelete:
                j.do.delete(item)
        j.action.start(retry=1, name="cleanup",description='', cmds="", action=cleanup, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)