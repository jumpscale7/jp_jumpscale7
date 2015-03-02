from JumpScale import j
from JumpScale.baselib.atyourservice.ActionsBase import remote
ActionsBase=j.atyourservice.getActionsBaseClass()


import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will install a node over ssh
        """
        def update():
            j.do.execute("apt-get update")
        j.actions.start(name="update",description='update', action=update, stdOutput=True, serviceObj=serviceObj)

        def upgrade():
            j.do.execute("apt-get upgrade -y")
        j.actions.start( name="upgrade",description='upgrade', action=upgrade, stdOutput=True, serviceObj=serviceObj)
        def extra():
            j.do.execute("apt-get install byobu curl -y")
        j.actions.start(name="extra",description='extra', action=extra, stdOutput=True, serviceObj=serviceObj)

        def jumpscale():
            j.do.execute("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            j.do.execute("sh /tmp/installjs.sh")
        j.actions.start(name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, serviceObj=serviceObj)

        return True


    def removedata(self,serviceObj):
        """
        delete vmachine
        """
        j.do.execute("killall tmux;killall python;echo")
        j.do.execute("rm -rf /opt")
        return True

    def execute(self,serviceObj,cmd):
        ip = serviceObj.hrd.get("instance.machine.ssh.ip")
        port = serviceObj.hrd.get("instance.machine.ssh.port")
        keyname =  serviceObj.hrd.get('instance.ssh.key.name') if serviceObj.hrd.exists('instance.ssh.key.name') else None
        login = serviceObj.hrd.get('instance.ssh.user') if serviceObj.hrd.exists('instance.ssh.user') else None
        password = serviceObj.hrd.get('instance.ssh.pwd') if serviceObj.hrd.exists('instance.ssh.pwd') else None
        keyHRD = j.application.getAppInstanceHRD("sshkey",keyname) if keyname != None else None

        cl = None
        c = j.remote.cuisine
        if keyHRD !=None:
            c.fabric.env["key"] = keyHRD.get('instance.ssh.key.priv')
            cl = c.connect(ip,port)
        else:
            cl = c.connect(ip,port,password)
        cl.run(cmd)

    def upload(self, serviceObj,source,dest):
        keyname = serviceobj.hrd.get("instance.ssh.key.name")
        sshkeyHRD = j.application.getAppInstanceHRD("sshkey",keyname)
        sshkey = sshkeyHRD.get("instance.ssh.key.priv")

        ip = serviceobj.hrd.get("instance.machine.ssh.ip")
        port = serviceobj.hrd.get("instance.machine.ssh.port")
        dest = "%s:%s" % (ip,dest)
        self._rsync(source,dest,sshkey,port)

    def download(self, serviceobj,source,dest):
        keyname = serviceobj.hrd.get("instance.ssh.key.name")
        sshkeyHRD = j.application.getAppInstanceHRD("sshkey",keyname)
        sshkey = sshkeyHRD.get("instance.ssh.key.priv")

        ip = serviceobj.hrd.get("instance.machine.ssh.ip")
        port = serviceobj.hrd.get("instance.machine.ssh.port")
        source = "%s:%s" % (ip,source)
        self._rsync(source,dest,sshkey,port)

    def _rsync(self,source,dest,key,port=22):
        def generateUniq(name):
            import time
            epoch = int(time.time())
            return "%s__%s" % (epoch,name)

        print("copy %s %s" % (source,dest))
        # if not j.do.exists(source):
            # raise RuntimeError("copytree:Cannot find source:%s"%source)

        if dest.find(":") != -1:
            # it's an upload
            if j.do.isDir(source):
                if dest[-1]!="/":
                    dest+="/"
                if source[-1]!="/":
                    source+="/"
        if source.find(":") != -1:
            # it's a download
            if j.do.isDir(dest):
                if dest[-1]!="/":
                    dest+="/"
                if source[-1]!="/":
                    source+="/"

        keyloc = "/tmp/%s" % generateUniq('id_dsa')
        j.system.fs.writeFile(keyloc,key)
        j.system.fs.chmod(keyloc,0o600)
        ssh = "-e 'ssh -i %s -p %s'" % (keyloc,port)

        destPath = dest
        if dest.find(":") != -1:
            destPath = dest.split(':')[1]

        verbose = "-q"
        if j.application.debug:
            verbose = "-v"
        cmd="rsync -a --rsync-path=\"mkdir -p %s && rsync\" %s %s %s %s"%(destPath,verbose,ssh,source,dest)
        print cmd
        j.do.execute(cmd)
        j.system.fs.remove(keyloc)