from JumpScale import j

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
        C = """
#Grid information
id = @ASK descr:'id of grid' default:1
node.id = 0
node.machineguid = %s
node.roles = @ASK descr:'roles this node subscribes to' default:node type:list
""" % j.application.getUniqueMachineId()
        hpath = j.system.fs.joinPaths(j.dirs.hrdDir, 'system', 'grid.hrd')
        if not j.system.fs.exists(path=hpath):
            j.system.fs.writeFile(hpath, C)
        j.application.loadConfig()
        j.application.config.get('grid.id')
        j.application.config.get('grid.node.roles')
