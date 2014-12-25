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
        j.system.platform.ubuntu.checkInstall(["cmake"], "cmake")
        j.system.platform.ubuntu.checkInstall(["gcc"], "gcc")

        cmd='apt-get install --no-install-recommends -y ca-certificates curl git-core g++ dh-autoreconf pkg-config libgflags-dev liblua5.1-dev git tmux mercurial'
        j.action.start(retry=1, name="deps",description='install deps', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)


    def configure(self,**args):
        """
        """
        #build luajit
        self.build()

    def build(self,**args):


        # Get and compile :
        #   - snappy
        #   - add leveldb for good measure
        #   - for gflags and lua, get system binaries (Lua = 5.1)

        cmd="""
mkdir -p /usr/src/
set -e
# bail if anywhere in there
# SNAPPY
cd /usr/src
export SNAPPY_DIR=/usr/local/snappy
git clone https://github.com/siddontang/snappy.git
cd ./snappy
autoreconf --force --install
./configure --prefix=$SNAPPY_DIR
make
make install
"""
        j.action.start(retry=1, name="snappy",description='compile snappy', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)


        cmd="""
# ROCKSDB (to compile in shared mode)
mkdir -p /usr/src/
set -e
cd /usr/src
git clone https://github.com/facebook/rocksdb.git
cd rocksdb
git checkout -b 3.5.fb origin/3.5.fb
make shared_lib
mkdir -p /usr/local/rocksdb/lib
mkdir /usr/local/rocksdb/include
cp librocksdb.so /usr/local/rocksdb/lib
cp -r include /usr/local/rocksdb/
ln -s /usr/local/rocksdb/lib/librocksdb.so /usr/lib/librocksdb.so
        """
        j.action.start(retry=1, name="ROCKSDB",description='compile ROCKSDB', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

        cmd="""
# LEVELDB
set -e
export LEVELDB_DIR=/usr/local/leveldb
git clone https://github.com/siddontang/leveldb.git
cd ./leveldb
echo "echo \"PLATFORM_CFLAGS+=-I$SNAPPY_DIR/include\" >> build_config.mk" >> build_detect_platform
echo "echo \"PLATFORM_CXXFLAGS+=-I$SNAPPY_DIR/include\" >> build_config.mk" >> build_detect_platform
echo "echo \"PLATFORM_LDFLAGS+=-L $SNAPPY_DIR/lib -lsnappy\" >> build_config.mk" >> build_detect_platform
make SNAPPY=1
mkdir -p $LEVELDB_DIR/include/leveldb
install include/leveldb/*.h $LEVELDB_DIR/include/leveldb
mkdir -p $LEVELDB_DIR/lib
cp -P libleveldb.* $LEVELDB_DIR/lib
ln -s /usr/local/leveldb/lib/libleveldb.so.1 /usr/lib/libleveldb.so.1
"""
        j.action.start(retry=1, name="LEVELDB",description='compile LEVELDB', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

        cmd="""
set -e
# for all that, we need GO, let's put it in here
curl -s https://storage.googleapis.com/golang/go1.3.2.linux-amd64.tar.gz | tar -v -C /usr/local -xz
export GOPATH=/usr/src/GO
export GOROOT=/usr/local/go
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH

# LEDISDB with all bells and whistles
mkdir -p $GOPATH/src/github.com/siddontang/ledisdb
cd $GOPATH/src/github.com/siddontang
git clone https://github.com/siddontang/ledisdb.git
go get github.com/cupcake/rdb
go get github.com/cupcake/rdb/nopdecoder
cd ledisdb && . ./dev.sh && ./bootstrap && make
make test

"""
        # j.action.start(retry=1, name="ledisdb",description='compile ledisdb', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)


        def cleanup():
            todelete=["$(param.base.luajit)/include/","$(param.base.luajit)/lib/luarocks/","$(param.base.luajit)/lib/pkgconfig/","$(param.base.luajit)/share/cmake/","$(param.base.luajit)/share/man/"]
            for item in todelete:
                j.do.delete(item)
        # j.action.start(retry=1, name="cleanup",description='', cmds="", action=cleanup, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)