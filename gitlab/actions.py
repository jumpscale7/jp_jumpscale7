from JumpScale import j
import os

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,**args):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        j.do.execute('apt-get install -y build-essential libgd3 zlib1g-dev libyaml-dev libssl-dev libgdbm-dev libreadline-dev libncurses5-dev libffi-dev checkinstall libxml2-dev libxslt-dev libcurl4-openssl-dev libicu-dev logrotate pkg-config cmake libkrb5-dev')
    #Install postfix
        j.system.platform.ubuntu.checkInstall('postfix', 'postfix')

   # Add git user
        j.do.execute('adduser --disabled-login --gecos \'GitLab\' git')

        j.do.createDir('/home/git/gitlab')
        j.do.copyFile('/etc/login.defs', '/etc/login.defs.org')
        j.do.execute("cd /etc/ && sed 's/ENV_PATH\tPATH=.*/ENV_PATH\tPATH=\/opt\/jumpscale7\/bin:\/opt\/postgresql\/bin:\/opt\/jumpscale7\/apps\/redis:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games:\/opt\/ruby\/bin/' login.defs.org | tee login.defs")
        j.do.execute('chmod +w /etc/sudoers')
        j.do.copyFile('/etc/sudoers', '/etc/sudoers.org')
        j.do.execute("cd /etc/ && sed 's/Defaults\tsecure_path=.*/Defaults\tsecure_path=\/opt\/jumpscale7\/bin:\/opt\/postgresql\/bin:\/opt\/jumpscale7\/apps\/redis:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games:\/opt\/ruby\/bin/' /etc/sudoers.org | tee /etc/sudoers")

        return True
        
    def configure(self,**args):
        os.system('export PATH=$PATH:/opt/ruby/bin')
   # Postgresql partation
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres psql -d template1 -c \'CREATE USER git CREATEDB\'')
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres psql -d template1 -c \'CREATE DATABASE gitlabhq_production OWNER git\'')
   # Install gitlab
        j.do.execute('sudo gem install bundler --no-ri --no-rdoc')
        j.do.execute('chown git:git -R /home/git')
        j.do.execute('sudo -u git -H mkdir /home/git/repositories')
        j.do.createDir('/home/git/gitlab-satellites')
        j.do.chown('/home/git/gitlab-satellites', 'git')
        j.do.execute('chmod u+rwx,g=rx,o-rwx /home/git/gitlab-satellites')
        j.do.copyFile('/home/git/gitlab/lib/support/init.d/gitlab.default.example', '/etc/default/gitlab')
        j.do.copyFile('/home/git/gitlab/lib/support/logrotate/gitlab', '/etc/logrotate.d/gitlab')
        j.do.execute('chown git:git -R /home/git')
        j.do.execute('usermod -a -G root git')
   # Configure Enginx
        if not j.do.isFile('/opt/nginx/cfg/sites-available/gitlab'):
            j.do.copyFile('/home/git/gitlab/lib/support/nginx/gitlab', '/opt/nginx/cfg/sites-available/gitlab')
        if not j.do.isLink('/opt/nginx/cfg/sites-enabled/gitlab'):
            j.do.execute('ln -s /opt/nginx/cfg/sites-available/gitlab /opt/nginx/cfg/sites-enabled/gitlab')
            j.do.delete('/opt/nginx/cfg/sites-enabled/default')

        j.do.execute("sed 's/production:\ unix:.*/production:\ unix:\/opt\/jumpscale7\/var\/redis\/gitlab\/redis.sock/' /home/git/gitlab/config/resque.yml.org | tee /home/git/gitlab/config/resque.yml")
        os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake gitlab:setup RAILS_ENV=production")
        nginx = j.packages.get(name='nginx', instance='main')
        nginx.restart()
        print('userName: root\npassword: 5iveL!fe')
        return True
