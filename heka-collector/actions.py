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

        BINARY_PATH = '/opt/code/git/binary/heka-collector/'
        BASE_PATH = self.jp_instance.hrd.get('param.base') 
        CONFIGS_PATH = os.path.join(BINARY_PATH, 'configs')
        INSTALLATION_CONFIGS_PATH = os.path.join(BASE_PATH, 'configs') 

        config_files = (
            'httpoutput.toml',
            'main.toml',
            'statsdagregator.toml',
        )

        j.system.fs.createDir(INSTALLATION_CONFIGS_PATH)
        for file_name in config_files:
            source_file = os.path.join(CONFIGS_PATH, file_name) 
            dest_file = os.path.join(INSTALLATION_CONFIGS_PATH, file_name) 
            log('Installing configuration file: ' + dest_file)
            j.system.fs.copyFile(source_file, dest_file)

        testing_source_file = os.path.join(CONFIGS_PATH, 'testing.toml')
        testing_dest_file = os.path.join(BASE_PATH, 'testing.toml')
        log('Installing the configuration file: testing.toml')
        j.system.fs.copyFile(testing_source_file, testing_dest_file)

        self.jp_instance.hrd.applyOnDir(INSTALLATION_CONFIGS_PATH)
