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

        reset=True
        if reset:
            j.do.delete("/opt/code/github/siddontang/",force=True)
            j.do.delete("/opt/code/github/facebook/rocksdb/",force=True)
            j.do.delete("/opt/build/ledisdb",force=True)
            j.do.delete("/opt/ledisdb",force=True)
            j.do.delete("/opt/jumpscale7/hrd/apps/jpackage.jumpscale.ledisdb.main.hrd",force=True)
            j.do.delete("/opt/jumpscale7/cfg/actions/jp_jumpscale_ledisdb.json",force=True)


    def configure(self,**args):
        """
        """
        pass

    def build(self,**args):

        #WAS QUITE UGLY, COPY PASTE FROM BASH FILES. DID SOME CLEANUP ALREADY (KRISTOF)
        #ALSO THE WAY HOW WE COMPILED IN NON SANDBOXED DIRS IS UGLY, NOW MOVED IT TO SANDBOXED DIRS
        #MORE JUMPSCALE PRIMITIVES SHOULD BE USED
        #ALL THE GIT CHECKOUTS SHOULD HAVE BEEN DONE AS PART OF THE JP.HRD (the code recipe) & then copy to a build directory (see what we did for luajit_build), ALSO FIXED

        # Get and compile :
        #   - snappy
        #   - add leveldb for good measure
        #   - for gflags and lua, get system binaries (Lua = 5.1)


#         #BUILDLUA
#         cmd="""
# set -e
# cd $(param.basebuild)/lua/
# cp src/luaconf.h.orig src/luaconf.h
# make linux
# cp src/lua /opt/ledisdb/lib/
# cp src/luac /opt/ledisdb/lib/
# cp src/liblua.a /opt/ledisdb/lib/
# """
#         j.action.start(retry=1, name="lua",description='compile lua', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

        cmd="""
set -e
# bail if anywhere in there
# SNAPPY
cd $(param.basebuild)/snappy/
export SNAPPY_DIR=/opt/ledisdb
autoreconf --force --install
./configure --prefix=$SNAPPY_DIR
make
make install
"""
        j.action.start(retry=1, name="snappy",description='compile snappy', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)


        cmd="""
set -e
cd $(param.basebuild)/rocksdb/
# git checkout -b 3.5.fb origin/3.5.fb
make shared_lib
cp librocksdb.so /opt/ledisdb/lib
cp -r include /opt/ledisdb
"""
        j.action.start(retry=1, name="ROCKSDB",description='compile ROCKSDB', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

        cmd="""
# LEVELDB
set -e
cd $(param.basebuild)/leveldb/
export LEVELDB_DIR=/opt/ledisdb
export SNAPPY_DIR=/opt/ledisdb
echo "echo \"PLATFORM_CFLAGS+=-I$SNAPPY_DIR/include\" >> build_config.mk" >> build_detect_platform
echo "echo \"PLATFORM_CXXFLAGS+=-I$SNAPPY_DIR/include\" >> build_config.mk" >> build_detect_platform
echo "echo \"PLATFORM_LDFLAGS+=-L $SNAPPY_DIR/lib -lsnappy\" >> build_config.mk" >> build_detect_platform
make SNAPPY=1
mkdir -p $LEVELDB_DIR/include/leveldb
install include/leveldb/*.h $LEVELDB_DIR/include/leveldb
mkdir -p $LEVELDB_DIR/lib
cp -P libleveldb.* $LEVELDB_DIR/lib
# ln -s /usr/local/leveldb/lib/libleveldb.so.1 /usr/lib/libleveldb.so.1
"""
        j.action.start(retry=1, name="LEVELDB",description='compile LEVELDB', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)
        #@todo is not working, still issue

        #is now embedded below in this action file
        # #copy our dev.sh file from ledisdb repo
        # src="/opt/code/git/binary/ledisdb/build/dev.sh"
        # dest="/opt/build/ledisdb/ledisdb/dev.sh"
        # j.do.copyFile(src,dest)

        cmd="""
set -ex
. /opt/go/goenv.sh
cd /opt/go/myproj

go get -u github.com/cupcake/rdb
go get -u github.com/cupcake/rdb/nopdecoder
go get -u github.com/szferi/gomdb
go get -u github.com/boltdb/bolt
go get -u github.com/ugorji/go/codec
go get -u github.com/BurntSushi/toml
go get -u github.com/edsrzf/mmap-go
go get -u github.com/syndtr/goleveldb/leveldb
go get -u github.com/siddontang/go/bson
go get -u github.com/siddontang/go/log
go get -u github.com/siddontang/go/snappy
go get -u github.com/siddontang/go/num
go get -u github.com/siddontang/go/filelock
go get -u github.com/siddontang/go/sync2
go get -u github.com/siddontang/go/arena
"""

        j.action.start(retry=1, name="godeps",description='get godeps', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

        cmd="""
set -ex

export LEDISROOT="/opt/build/ledisdb/ledisdb/"

export GOPATH=/opt/go/myproj:$LEDISROOT
export GOROOT=/opt/go
export PATH=$GOROOT/bin:$GOROOT/myproj/bin:$PATH

#default snappy and leveldb install path
#you may change yourself
SNAPPY_DIR=/opt/ledisdb
LEVELDB_DIR=/opt/ledisdb
ROCKSDB_DIR=/opt/ledisdb
LUA_DIR=/opt/ledisdb

GO_BUILD_TAGS=
CGO_CFLAGS=
CGO_CXXFLAGS=
CGO_LDFLAGS=

#get lua5.1 from build dir
cp /opt/code/git/binary/ledisdb/lua/* /opt/ledisdb/lib
cp /opt/code/git/binary/ledisdb/luainclude/* /opt/ledisdb/include

# check dependent libray, now we only check simply, maybe later add proper checking 

# check snappy 
if [ -f $SNAPPY_DIR/include/snappy.h ]; then
    echo 1
    CGO_CFLAGS="$CGO_CFLAGS -I$SNAPPY_DIR/include"
    CGO_CXXFLAGS="$CGO_CXXFLAGS -I$SNAPPY_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$SNAPPY_DIR/lib -lsnappy"
    LD_LIBRARY_PATH="$SNAPPY_DIR/lib"
    DYLD_LIBRARY_PATH="$SNAPPY_DIR/lib"
fi

# check leveldb
if [ -f $LEVELDB_DIR/include/leveldb/c.h ]; then
    echo 2
    CGO_CFLAGS="$CGO_CFLAGS -I$LEVELDB_DIR/include"
    CGO_CXXFLAGS="$CGO_CXXFLAGS -I$LEVELDB_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$LEVELDB_DIR/lib -lleveldb"
    LD_LIBRARY_PATH="$LEVELDB_DIR/lib"
    DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH"
    GO_BUILD_TAGS="$GO_BUILD_TAGS leveldb"
fi

# check rocksdb
if [ -f $ROCKSDB_DIR/include/rocksdb/c.h ]; then
    echo 3
    CGO_CFLAGS="$CGO_CFLAGS -I$ROCKSDB_DIR/include"
    CGO_CXXFLAGS="$CGO_CXXFLAGS -I$ROCKSDB_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$ROCKSDB_DIR/lib -lrocksdb"
    LD_LIBRARY_PATH="$ROCKSDB_DIR/lib"
    DYLD_LIBRARY_PATH="$ROCKSDB_DIR/lib"
    GO_BUILD_TAGS="$GO_BUILD_TAGS rocksdb"
fi


#check lua
if [ -f $LUA_DIR/include/lua.h ]; then
    echo 4
    CGO_CFLAGS="$CGO_CFLAGS -I$LUA_DIR/include"
    CGO_LDFLAGS="$CGO_LDFLAGS -L$LUA_DIR/lib -llua"
    LD_LIBRARY_PATH="$LUA_DIR/lib"
    DYLD_LIBRARY_PATH="$LUA_DIR/lib"
    GO_BUILD_TAGS="$GO_BUILD_TAGS lua"
fi

# export CGO_CFLAGS
# export CGO_CXXFLAGS
# export CGO_LDFLAGS
# export LD_LIBRARY_PATH
# export DYLD_LIBRARY_PATH
# export GO_BUILD_TAGS

echo "GO BUILD TAGS:$GO_BUILD_TAGS"

#I read about bug to use other version (but does not resolve my issue)
cd /opt/go/myproj/src/github.com/syndtr/goleveldb/leveldb
git checkout 871eee0a7546bb7d1b2795142e29c4534abc49b3
cd /opt/go/myproj
go build github.com/syndtr/goleveldb/leveldb

#build dir needs to be under goroot
cp -R $(param.basebuild)/ledisdb /opt/go/myproj/src/github.com/siddontang/ledisdb/
cd /opt/go/myproj/src/github.com/siddontang/ledisdb/

make
make test

"""
        j.action.start(retry=1, name="ledisdb",description='compile ledisdb', cmds=cmd, action=None, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)


        def cleanup():
            todelete=["$(param.base.luajit)/include/","$(param.base.luajit)/lib/luarocks/","$(param.base.luajit)/lib/pkgconfig/","$(param.base.luajit)/share/cmake/","$(param.base.luajit)/share/man/"]
            for item in todelete:
                j.do.delete(item)
        # j.action.start(retry=1, name="cleanup",description='', cmds="", action=cleanup, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=False, jp=self.jp_instance)