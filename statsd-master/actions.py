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
        influx_instance = self.jp_instance.hrd.get('param.influxdb.connection')
        hrd = j.application.getAppInstanceHRD('influxdb_client', influx_instance)
        template = {
            'host' : hrd.get('param.influxdb.client.address'),
            'port': hrd.get('param.influxdb.client.port'),
            'login' : hrd.get('param.influxdb.client.login'),
            'passwd' : hrd.get('param.influxdb.client.passwd'),
            'dbname' : hrd.get('param.influxdb.client.dbname')
        
        }
        
        configsamplepath = j.system.fs.joinPaths('/opt/', 'statsd-master', 'MasterConfig.js')
        configpath = j.system.fs.joinPaths('/opt/', 'statsd-master', 'statsd.master.conf.js')
        if not j.system.fs.exists(configpath):
            j.system.fs.createEmptyFile(configpath)

        j.system.fs.copyFile(configsamplepath, configpath)
        hrd.applyOnFile(configpath, template)
