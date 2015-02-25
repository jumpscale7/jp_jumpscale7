from JumpScale import j

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
        # j.system.platform.ubuntu.createUser("mysql", passwd=j.base.idgenerator.generateGUID(), home="/home/mysql", creategroup=True)
        
        # j.system.fs.chown(path="/opt/mariadb/", user="mysql")
        # j.system.fs.createDir("/var/log/mysql")

        # j.system.process.killProcessByPort(3306)
        # j.do.delete("/var/run/mysqld/mysqld.sock")
        # j.do.delete("/etc/mysql")
        # j.do.delete("~/.my.cnf")
        # j.do.delete("/etc/my.cnf")
        # j.system.fs.createDir("/var/jumpscale/mysql")
        # j.system.fs.createDir("/tmp/mysql")

        return True

    def configure(self,serviceobject):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """


        return True

