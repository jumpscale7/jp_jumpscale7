from JumpScale import j
import time

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
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        j.system.platform.ubuntu.createUser("mysql", passwd=j.base.idgenerator.generateGUID(), home="/home/mysql", creategroup=True)
        j.system.fs.createDir("$(system.paths.base)/apps/mariadb") 
        j.system.fs.chown(path="$(system.paths.base)/apps/mariadb", user="mysql")
        j.system.fs.createDir("/var/log/mysql")
        j.system.process.killProcessByPort(3306)
        j.do.delete("/var/run/mysqld/mysqld.sock")
        j.do.delete("/etc/mysql")
        j.do.delete("~/.my.cnf")
        j.do.delete("/etc/my.cnf")
        j.system.fs.createDir("/var/jumpscale/mysql")
	j.system.fs.createDir("$(system.paths.var)/mysql")
        j.system.fs.createDir("/tmp/mysql")
	j.do.execute('apt-get install libaio1 -y')
        return True

    def configure(self,**args):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        j.application.config.applyOnDir("$(system.paths.base)/apps/mariadb/cfg",filter=None, changeFileName=True,changeContent=True,additionalArgs={})       

        j.do.copyFile("$(system.paths.base)/apps/mariadb/share/english/errmsg.sys","$(system.paths.var)/mysql/errmsg.sys")
        j.system.fs.createDir("/usr/share/mysql/")
        j.system.fs.chown(path="/usr/share/mysql/", user="mysql")
        j.do.copyFile("$(system.paths.base)/apps/mariadb/share/english/errmsg.sys","/usr/share/mysql/errmsg.sys")
        j.system.fs.createDir("/var/run/mysqld/")
        j.system.fs.chown(path="$(system.paths.var)/mysql", user="mysql")
        j.system.fs.chown(path="/var/log/mysql/", user="mysql")
        j.system.fs.chown(path="/var/jumpscale/mysql", user="mysql")
        j.system.fs.chown(path="/tmp/mysql", user="mysql")
        j.system.fs.chown(path="$(system.paths.base)/apps/mariadb", user="mysql")
        
        if not j.system.fs.exists("/var/jumpscale/mysql/data"):
            print("############## in configure:")
            cmd="cd $(system.paths.base)/apps/mariadb;scripts/mysql_install_db --user=mysql --defaults-file=cfg/my.cnf --basedir=$(system.paths.base)/apps/mariadb --datadir=/var/jumpscale/mysql/data"
            print (cmd)
            j.do.executeInteractive(cmd)
            self.start()
            cmd="$(system.paths.base)/apps/mariadb/bin/mysqladmin -u root password '$(param.rootpasswd)'"
            time.sleep(5)
            j.system.process.execute(cmd)
            self.stop()
        return True
