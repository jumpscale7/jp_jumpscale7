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

        def deps():
            if not j.do.exists("/usr/bin/virsh"):
                cmd="apt-get install qemu-kvm qemu virt-manager virt-viewer libvirt-bin bridge-utils -y"
                rc,out,err=j.do.execute( cmd, outputStdout=True, outputStderr=True, useShell=True, log=True, cwd=None, timeout=360, captureout=True, dieOnNonZeroExitCode=False)

        j.action.start(retry=2, name="deps",description='install deps', cmds='', action=deps, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance) 


        C="""
apt-get install curlftpfs -y
mkdir -p /mnt/ftp
curlftpfs pub:pub1234@git.aydo.com /mnt/ftp
mkdir -p /mnt/vmstor/kvm/images
rsync -arv --partial --progress /mnt/ftp/images/ubuntu1404/ /mnt/vmstor/kvm/images/ubuntu1404/
rsync -arv --partial --progress /mnt/ftp/images/openwrt/ /mnt/vmstor/kvm/images/openwrt/
"""                

        j.action.start(retry=2, name="getimages",description='get ubuntu & openwrt images (can take a while)', cmds=C, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance) 
        

        netconfig="""
# Network interfaces file 
auto lo
iface lo inet loopback

# eth0 interface
auto eth0
iface eth0 inet manual

# br0 interface 
auto br0
iface br0 inet static
address 192.168.1.190
network 192.168.1.0
netmask 255.255.255.0
broadcast 192.168.1.255
gateway 192.168.1.1
dns-nameservers 4.2.2.2
bridge_ports eth0
bridge_stp off        
"""
