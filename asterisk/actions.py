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
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        cmd="""
sudo apt-get update && apt-get install gcc g++ libncurses5-dev uuid-dev libjansson* libxml2 libxml2-* sqlite3 libsqlite3-dev -y 

"""

        rc,out,err=j.do.executeCmds( cmd, outputStdout=True, outputStderr=True, useShell=True, log=True, cwd=None, timeout=360, captureout=True, dieOnNonZeroExitCode=False)
 


    def configure(self,**args):
	
	"""
        this only configure astrisk first 
        """
        j.do.execute('cd /opt/asterisk && ./configure')
        j.do.execute('cd /opt/asterisk && make distclean ')
        j.do.execute('cd /opt/asterisk/contrib/scripts && ./install_prereq install') 
	j.do.execute('cd /opt/asterisk/contrib/scripts && ./install_prereq install-unpackaged')
	j.do.execute('echo "######################## reconfigure Asterisk ############################ " ')
	j.do.execute('cd /opt/asterisk && ./configure')
	j.do.execute('cd /opt/asterisk && make menuselect')
	j.do.execute('echo "################# Installing Asterisk #################################"')
	j.do.chdir('/opt/asterisk')
	j.do.execute('pwd')
	j.do.execute('make') 
	j.do.execute('make install')
	j.do.execute('make samples')
	j.do.execute('make config') 
	j.do.execute('make install-logrotate')
	j.do.execute('echo "###################### Thank You #######################################"')
