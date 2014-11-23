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

    def prepare(self,hrd,**args):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        # j.system.platform.ubuntu.createGroup("mysql")
        # j.system.platform.ubuntu.createUser("mysql", passwd="1234", home="/home/mysql", creategroup=True)
        
        # j.system.fs.chown(path="/opt/mariadb/", user="mysql")
        # j.system.fs.createDir("/var/log/mysql")

        j.system.process.killProcessByPort(3306)
        j.system.fs.createDir("$(system.paths.var)/mysql")

        # j.system.fs.createDir("/usr/share/mysql/")
        # j.system.fs.createDir("/var/run/mysqld/")
        # j.do.copyFile("/opt/mariadb/share/english/errmsg.sys","/usr/share/mysql/errmsg.sys")
        # j.system.fs.chown(path="/usr/share/mysql/", user="mysql")

        # j.system.fs.chown(path="/var/log/mysql/", user="mysql")

        return True

    def configure(self,hrd,**args):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        j.application.config.applyOnDir("$(base)/cfg",filter=None, changeFileName=True,changeContent=True,additionalArgs={})
        

        j.do.copyFile("$(base)/share/english/errmsg.sys","$(system.paths.var)/mysql/errmsg.sys")
        j.system.fs.createDir("$(base)/data")


        if not j.system.fs.exists(path="$(base)/data/mysql/"):
            # j.events.inputerror_critical("cannot install mariadb on $(base)/data, data does already exist","jpackage.install.mariadb.alreadythere")
            cmd="cd $(base);scripts/mysql_install_db --user=root --defaults-file=cfg/my.cnf --basedir=$(base) --datadir=$(base)/data/"
            print (cmd)
            j.do.executeInteractive(cmd)

            self.start(hrd)

            cmd="$(base)/bin/mysqladmin -u root password '$(rootpasswd)'"
            j.do.execute(cmd)

            self.stop(hrd)

        return True

    # def start(self,hrd,**args):
    #     #start mysql in background
    #     if j.system.net.tcpPortConnectionTest("localhost",3306):
    #         return

    #     import JumpScale.baselib.screen

    #     cmd="/opt/mariadb/bin/mysqld --basedir=/opt/mariadb --datadir=/opt/mariadb/data --plugin-dir=/opt/mariadb/lib/plugin/ --user=root --console --verbose"
    #     j.system.platform.screen.createSession("servers",["mariadb"])
    #     j.system.platform.screen.executeInScreen(sessionname="servers", screenname="mariadb", cmd=cmd, wait=0, cwd=None, env=None, user='root', tmuxuser=None)

    #     #now wait till we can access the port
    #     res=j.system.net.waitConnectionTest("localhost",3306,2)
    #     if res==False:
    #         j.events.inputerror_critical("mariadb did not become active, check in byobu","jpackage.install.mariadb.startup")

    def stop(self,hrd,**args):
        """
        if you want a gracefull shutdown implement this method
        a uptime check will be done afterwards (local)
        return True if stop was ok, if not this step will have failed & halt will be executed.
        """        
        cmd="$(base)/bin/mysql -u root --password='$(rootpasswd)' --execute='shutdown;'"
        print (cmd)
        j.do.execute(cmd)  

        if self.check_down_local(hrd):
            return True
        else:
            j.events.opserror_critical("Cannot stop %s."%self.jp,"jpackage.stop")

    # def halt(self,hrd,**args):
    #     """
    #     hard kill the app, std a linux kill is used, you can use this method to do something next to the std behaviour
    #     """
    #     return True

    # def check_uptime_local(self,hrd,**args):
    #     """
    #     do checks to see if process(es) is (are) running.
    #     this happens on system where process is
    #     """
    #     return True

    # def check_requirements(self,hrd,**args):
    #     """
    #     do checks if requirements are met to install this app
    #     e.g. can we connect to database, is this the right platform, ...
    #     """
    #     return True

    # def monitor_local(self,hrd,**args):
    #     """
    #     do checks to see if all is ok locally to do with this package
    #     this happens on system where process is
    #     """
    #     return True

    # def monitor_remote(self,hrd,**args):
    #     """
    #     do checks to see if all is ok from remote to do with this package
    #     this happens on system from which we install or monitor (unless if defined otherwise in hrd)
    #     """
    #     return True

    # def cleanup(self,hrd,**args):
    #     """
    #     regular cleanup of env e.g. remove logfiles, ...
    #     is just to keep the system healthy
    #     """
    #     return True

    # def data_export(self,hrd,**args):
    #     """
    #     export data of app to a central location (configured in hrd under whatever chosen params)
    #     return the location where to restore from (so that the restore action knows how to restore)
    #     we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
    #     """
    #     return False

    # def data_import(self,id,hrd,**args):
    #     """
    #     import data of app to local location
    #     if specifies which retore to do, id corresponds with line item in the $name.export file
    #     """
    #     return False

    # def uninstall(self,hrd,**args):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass


