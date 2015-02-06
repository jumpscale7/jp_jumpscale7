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

    # def prepare(self,**args):
    #     """
    #     this gets executed before the files are downloaded & installed on appropriate spots
    #     """
    #     j.do.execute('apt-get purge \'nginx*\' -y')
    #     j.do.execute('apt-get autoremove -y')
    #     j.system.process.killProcessByPort(80)
    #     j.system.fs.createDir("/var/nginx/cache/fcgi")
    #     j.system.fs.createDir("/var/log/nginx")
    #     return True

    def configure(self,**args):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        def createENV():
            # create GOPATH
            j.system.fs.createDir("/opt/go/workspace")
            j.system.fs.createDir("/opt/go/workspace/pkg")
            j.system.fs.createDir("/opt/go/workspace/src")
            j.system.fs.createDir("/opt/go/workspace/bin")
            j.do.execute(command="sed -i '/PATH/d' /root/.bashrc")
            j.do.execute(command="sed -i '/GOPATH/d' /root/.bashrc")
            j.do.execute(command="sed -i '/GOROOT/d' /root/.bashrc")

            j.do.execute(command="echo 'export GOPATH=/opt/go/workspace' >> /root/.bashrc")
            j.do.execute(command="echo 'export GOROOT=/opt/go' >> /root/.bashrc")
            _,path,_ = j.do.execute("echo $PATH",outputStdout=False)
            cmd = "echo 'export PATH=%s:$GOROOT/bin:$GOPATH/bin' >> /root/.bashrc" % path.strip()
            j.do.execute(command=cmd)
        j.action.start(retry=0, name="createENV",description='create GOPATH', cmds='', action=createENV, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)
        return True

        def installGodep():
            j.do.execute("go get -u github.com/tools/godep")
            j.action.start(retry=0, name="installGodep",description='install GOPATH', cmds='', action=installGodep, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

    def removedata(self,**args):
        j.system.fs.removeDirTree("/opt/go")
        j.do.execute(command="sed -i '/GOPATH/d' /root/.bashrc")
        j.do.execute(command="sed -i '/GOROOT/d' /root/.bashrc")