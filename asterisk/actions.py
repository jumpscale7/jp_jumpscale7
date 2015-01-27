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
        ############ Asterisk
        j.do.execute('sudo apt-get update')
        j.do.execute('sudo apt-get update && apt-get install gcc make g++ libncurses5-dev uuid-dev libjansson* libxml2 libxml2-* sqlite3 libsqlite3-dev libxslt1-dev  -y')
        return True


    def configure(self,**kwargs):
        j.do.execute('cp -rf /opt/jumpscale7/apps/asterisk/config /etc/init.d')
        j.do.execute('update-rc.d asterisk defaults')

    def stop(self,**kwargs):
        if j.system.fs.exists('/opt/jumpscale7/apps/asterisk/config'):
            j.do.execute('cd /opt/jumpscale7/apps/asterisk/config && ./asterisk stop ')
