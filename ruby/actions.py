from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def build(self,**args):
        """
        """
        

#        cmd = 'apt-get install -y bzip2 gcc build-essential zlib1g-dev libyaml-dev libssl-dev libgdbm-dev libreadline-dev libncurses5-dev libffi-dev curl checkinstall libxml2-dev libxslt-dev libcurl4-openssl-dev libicu-dev logrotate python-docutils pkg-config cmake libkrb5-dev'
        j.action.start(retry=1, name="apt_get_install",description='', cmds=cmd, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)
        
        def downloadruby():
            url='http://cache.ruby-lang.org/pub/ruby/2.2/ruby-2.2.0.tar.gz'
            j.do.downloadExpandTarGz( url, destdir="/tmp/ruby", deleteDestFirst=True, deleteSourceAfter=True)
        j.action.start(retry=1, name="ruby_installer",description='', action=downloadruby, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)
        
        cmds="""
cd /tmp
wget -O ruby-install-0.5.0.tar.gz https://github.com/postmodern/ruby-install/archive/v0.5.0.tar.gz
tar -xzvf ruby-install-0.5.0.tar.gz
cd ruby-install-0.5.0/
sudo make install
"""
        j.action.start(retry=1, name="ruby_installer",description='', cmds=cmds, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)


        cmds="ruby-install --install-dir /opt/ruby ruby"
        j.action.start(retry=1, name="ruby_build",description='', cmds=cmds, actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, jp=self.jp_instance)

        return True


    def package(self,**args):
        """
        """
        src="/opt/ruby/"
        dest="/opt/code/git/binary/ruby/ruby/"
        j.system.fs.copyDirTree(src,dest,eraseDestination=True)

