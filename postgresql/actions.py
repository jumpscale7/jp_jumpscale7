from JumpScale import j
import time
ActionsBase=j.atyourservice.getActionsBaseClass()

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

    def prepare(self,serviceobject):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        j.system.platform.ubuntu.createUser("postgres", passwd=j.base.idgenerator.generateGUID(), home="/home/postgresql", creategroup=True)
        
        j.system.process.killProcessByPort("$(param.port)")
        j.system.fs.createDir("/tmp/postgres")

        return True

    def configure(self,serviceobject):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        # j.application.config.applyOnDir("$(param.base)/cfg",filter=None, changeFileName=True,changeContent=True,additionalArgs={})  

        if j.system.fs.exists(path="$(datadir)"):
            # Already configured once. Nothing to do here.
            return
        
        j.system.fs.createDir("$(datadir)")
        j.system.fs.chown(path="$(param.base)", user="postgres")
        j.system.fs.chown(path="$(datadir)", user="postgres")        
        j.system.fs.chmod("$(datadir)",0777)

        cmd="su -c '$(param.base)/bin/initdb -D $(datadir)' postgres"
        j.system.process.executeWithoutPipe(cmd)

        def replace(path,newline,find):
            lines=j.system.fs.fileGetContents(path)
            out=""
            found=False
            for line in lines.split("\n"):
                if line.find(find)<>-1:
                    line=newline
                    found=True
                out+="%s\n"%line
            if found==False:
                out+="%s\n"%newline
            j.system.fs.writeFile(filename=path,contents=out)

        replace("$(datadir)/pg_hba.conf","host    all             all             0.0.0.0/0               md5","0.0.0.0/0")

        j.system.fs.createDir("/var/log/postgresql")
    
        self.start()
        time.sleep(2)

        cmd="cd $(param.base)/bin;./psql -U postgres template1 -c \"alter user postgres with password '$(param.rootpasswd)';\" -h localhost"
        j.do.execute(cmd)

        # self.stop()

        return True

    # def start(self,serviceobject):
    #     #start postgresql in background
    #     if j.system.net.tcpPortConnectionTest("localhost",3306):
    #         return

    #     import JumpScale.baselib.screen

    #     cmd="/opt/mariadb/bin/postgresqld --basedir=/opt/mariadb --datadir=/opt/mariadb/data --plugin-dir=/opt/mariadb/lib/plugin/ --user=root --console --verbose"
    #     j.system.platform.screen.createSession("servers",["mariadb"])
    #     j.system.platform.screen.executeInScreen(sessionname="servers", screenname="mariadb", cmd=cmd, wait=0, cwd=None, env=None, user='root', tmuxuser=None)

    #     #now wait till we can access the port
    #     res=j.system.net.waitConnectionTest("localhost",3306,2)
    #     if res==False:
    #         j.events.inputerror_critical("mariadb did not become active, check in byobu","jpackage.install.mariadb.startup")

    def stop(self,serviceobject):
        """
        if you want a gracefull shutdown implement this method
        a uptime check will be done afterwards (local)
        return True if stop was ok, if not this step will have failed & halt will be executed.
        """
        # No process actually running
        if not j.system.process.getPidsByPort("$(param.port)"):
            return
        
        cmd="sudo -u postgres $(param.base)/bin/pg_ctl -D /var/jumpscale/postgresql stop  -m fast"
        # print (cmd)
        rc,out,err=j.do.execute(cmd, dieOnNonZeroExitCode=False, outputStdout=False, outputStderr=True,timeout=5)
        if rc>0:
            if rc==999:
                cmd="sudo -u postgres $(param.base)/bin/pg_ctl -D /var/jumpscale/postgresql stop  -m immediate"
                rc,out,err=j.do.execute(cmd, dieOnNonZeroExitCode=False, outputStdout=False, outputStderr=True,timeout=5)
            else:
                raise RuntimeError("could not stop %s"%serviceobject)


        # if self.check_down_local(hrd):
        #     return True
        # else:
        #     j.events.opserror_critical("Cannot stop %s."%self.jp,"jpackage.stop")

    # def halt(self,serviceobject):
    #     """
    #     hard kill the app, std a linux kill is used, you can use this method to do something next to the std behaviour
    #     """
    #     return True

    # def check_uptime_local(self,serviceobject):
    #     """
    #     do checks to see if process(es) is (are) running.
    #     this happens on system where process is
    #     """
    #     return True

    # def check_requirements(self,serviceobject):
    #     """
    #     do checks if requirements are met to install this app
    #     e.g. can we connect to database, is this the right platform, ...
    #     """
    #     return True

    # def monitor_local(self,serviceobject):
    #     """
    #     do checks to see if all is ok locally to do with this package
    #     this happens on system where process is
    #     """
    #     return True

    # def monitor_remote(self,serviceobject):
    #     """
    #     do checks to see if all is ok from remote to do with this package
    #     this happens on system from which we install or monitor (unless if defined otherwise in hrd)
    #     """
    #     return True

    # def cleanup(self,serviceobject):
    #     """
    #     regular cleanup of env e.g. remove logfiles, ...
    #     is just to keep the system healthy
    #     """
    #     return True

    # def data_export(self,serviceobject):
    #     """
    #     export data of app to a central location (configured in hrd under whatever chosen params)
    #     return the location where to restore from (so that the restore action knows how to restore)
    #     we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
    #     """
    #     return False

    # def data_import(self,id,hrd,serviceObj):
    #     """
    #     import data of app to local location
    #     if specifies which retore to do, id corresponds with line item in the $name.export file
    #     """
    #     return False

    # def uninstall(self,serviceobject):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass


