from JumpScale import j
import os

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,**args):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
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
#        os.system('export PATH=$PATH:/opt/ruby/bin')
   # Postgresql partation
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres psql -d template1 -c \'CREATE USER git CREATEDB\'')
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres psql -d template1 -c \'CREATE DATABASE gitlabhq_production OWNER git\'')
   # Install gitlab
        j.do.execute('sudo -u git -H mkdir /home/git/repositories')
        j.do.execute('sudo -u git -H mkdir -m 2770 /home/git/gitlab-satellites')
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
