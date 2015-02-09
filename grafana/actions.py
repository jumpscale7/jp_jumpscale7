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
        influxjp = j.packages.get(name='influxdb_client', instance=influx_instance)
        host = influxjp.hrd.get('param.influxdb.client.address')
        
        if j.system.net.isIpLocal(host):
            host = 'window.location.hostname'
        else:
            host = "'%s'" % host
        
        port = str(influxjp.hrd.get('param.influxdb.client.port'))
        username = influxjp.hrd.get('param.influxdb.client.login')
        password = influxjp.hrd.get('param.influxdb.client.passwd')
        configsamplepath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', 'jslib', 'grafana', 'config.sample.js')  
        configpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', 'jslib', 'grafana', 'config.js')
        if not j.system.fs.exists(configpath):
            j.system.fs.createEmptyFile(configpath)
               
        j.system.fs.copyFile(configsamplepath, configpath)
        template = {'param.influxdb.client.address': host, 'param.influxdb.client.port':port, 'param.influxdb.client.login':username, 'param.influxdb.client.passwd':password}
        new_content = j.application.config.applyOnContent(open(configpath).read(), additionalArgs=template)
        open(configpath, "w").write(new_content)