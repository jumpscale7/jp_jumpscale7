from JumpScale import j
import ipdb
import pdb

ActionsBase = j.packages.getActionsBaseClass()


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

    def prepare(self, **args):
        hpath = j.system.fs.joinPaths(j.dirs.hrdDir, 'system', 'grid.hrd')
        if not j.system.fs.exists(path=hpath):    
            C = """
#Grid information
id = %(grid.id)s
node.id = 0
node.machineguid = %(machineguid)s
node.roles = %(grid.node.roles)s
""" % {'machineguid':j.application.getUniqueMachineId(), 'grid.id': self.jp_instance.hrd.get('grid.id'), 'grid.node.roles':self.jp_instance.hrd.get('grid.node.roles')}
            j.system.fs.writeFile(hpath, C)
        j.application.loadConfig()
        j.application.config.get('grid.id')
        j.application.config.get('grid.node.roles')
        self.jp_instance.hrd.pop('grid.id')
        self.jp_instance.hrd.pop('grid.node.roles')
        self.jp_instance.hrd.save()
