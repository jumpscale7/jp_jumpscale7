from JumpScale import j

ActionsBase=j.packages.getActionsBaseClass()

import os.path

def log(message):
    print(' :: ' + message)


class Actions(ActionsBase):


    def build(self, **kwargs):
    
        BIN_TARBALL_URL = 'https://github.com/mozilla-services/heka/releases/download/v0.8.3/heka-0_8_3-linux-amd64.tar.gz'
        BUILD_BASE = '/opt/build/heka-master/'
        BIN_TARBALL_PATH = os.path.join(BUILD_BASE, 'heka-0_8_3-linux-amd64.tar.gz')
        BIN_ROOT = os.path.join(BUILD_BASE, 'heka-0_8_3-linux-amd64')   # The tarball will be extracted into this

        j.system.fs.createDir(BUILD_BASE)

        log('Downloading binary tarball')
        j.system.net.downloadIfNonExistent(BIN_TARBALL_URL, BIN_TARBALL_PATH, md5_checksum='d23d0e599263b5111bf310fbea838ff3')

        log('Uncompressing binary tarball')
        j.system.fs.targzUncompress(BIN_TARBALL_PATH, BUILD_BASE, removeDestinationdir=False)
        

    def configure(self, *args, **kwargs):

        INSTALLATION_CONFIGS_PATH = os.path.join(self.jp_instance.hrd.get('param.base'), 'configs') 

        self.jp_instance.hrd.applyOnDir(INSTALLATION_CONFIGS_PATH)
