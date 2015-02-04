from JumpScale import j
import time
ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):
    
     def configure(self,**args):
       """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
       """
       influx_instance = self.jp_instance.hrd.get('param.influxdb.connection')
       influxjp = j.packages.get(name='influxdb_client', instance=influx_instance)
       host = influxjp.hrd.get('param.influxdb.client.address')
       port = str(influxjp.hrd.get('param.influxdb.client.port'))
       username = influxjp.hrd.get('param.influxdb.client.login')
       password = influxjp.hrd.get('param.influxdb.client.passwd')
       configsamplepath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', 'jslib', 'grafana', 'config.sample.js')  
       configpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'portals', 'jslib', 'grafana', 'config.js')
       if not j.system.fs.exists(configpath):
           j.system.fs.createEmptyFile(configpath)
              
       j.system.fs.copyFile(configsamplepath, configpath)
       data = open(configpath).read()
       template = {'$host': host, '$port':port, '$username':username, '$password':password}
       for k, v in template.iteritems():
           data = data.replace(k, '"%s"' % v)
       open(configpath, 'w').write(data)
