from JumpScale import j
import time
import socket
import fcntl
import struct

ActionsBase = j.packages.getActionsBaseClass()

class Actions(ActionsBase):
    

    def configure(self, **args):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        hrd = self.jp_instance.hrd
        configsamplepath = j.system.fs.joinPaths('/opt/', 'statsd-collector', 'CollectorConfig.js')
        configpath = j.system.fs.joinPaths('/opt/', 'statsd-collector', 'statsd.collector.conf.js')
        if not j.system.fs.exists(configpath):
            j.system.fs.createEmptyFile(configpath)

        j.system.fs.copyFile(configsamplepath, configpath)
        hrd.applyOnFile(configpath)
