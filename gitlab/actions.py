from JumpScale import j
import os

ActionsBase=j.packages.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,**args):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        j.system.platform.ubuntu.checkInstall('cmake', 'make')
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

   # Install Enginx
#        j.system.platform.ubuntu.checkInstall('nginx', 'nginx')
        
        return True
        
    def configure(self,**args):
        os.system('export PATH=$PATH:/opt/ruby/bin')
   # Postgresql partation
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres psql -d template1 -c \'CREATE USER git CREATEDB\'')
        j.do.execute('cd /opt/postgresql/bin; sudo -u postgres psql -d template1 -c \'CREATE DATABASE gitlabhq_production OWNER git\'')
   # Install gitlab
        j.do.execute('sudo gem install bundler --no-ri --no-rdoc')
        j.do.execute('chown git:git -R /home/git')
        j.do.execute('pwd')
        j.do.chdir('/home/git')
        j.do.chdir('/home/git/gitlab')
        j.do.execute('chmod -R u+rwX,go-w log/ && chmod -R u+rwX tmp/')
        j.do.createDir('/home/git/gitlab-satellites')
        j.do.chown('/home/git/gitlab-satellites', 'git')
        j.do.execute('chmod u+rwx,g=rx,o-rwx /home/git/gitlab-satellites')
        j.do.execute('chmod -R u+rwX tmp/pids/')
        j.do.execute('chmod -R u+rwX tmp/sockets/')
        j.do.execute('chmod -R u+rwX  public/uploads')
        os.system('sudo -u git -H git config --global user.name \"GitLab\"')
        os.system('sudo -u git -H git config --global user.email \"$(param.email)\"')
        os.system("sudo -u git -H git config --global core.autocrlf input")
        j.do.execute('sudo -u git -H chmod o-rwx config/database.yml')
#        j.do.copyFile('/home/git/gitlab/lib/support/init.d/gitlab', '/etc/init.d/gitlab')
        j.do.copyFile('/home/git/gitlab/lib/support/init.d/gitlab.default.example', '/etc/default/gitlab')
#        j.do.execute('update-rc.d gitlab defaults 21')
        j.do.copyFile('/home/git/gitlab/lib/support/logrotate/gitlab', '/etc/logrotate.d/gitlab')
        os.system("cd /home/git/gitlab && sudo -u git -H bundle install --deployment --without development test mysql aws")
        os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake gitlab:shell:install[v2.4.0] REDIS_URL=unix:/opt/jumpscale7/var/redis/gitlab/redis.sock RAILS_ENV=production")
        j.do.copyFile('/home/git/gitlab-shell/config.yml', '/home/git/gitlab-shell/config.yml.org')
        os.system("cd /home/git/gitlab-shell && sed 's/socket:.*/socket:\ \"\/opt\/jumpscale7\/var\/redis\/gitlab\/redis.sock\"/' config.yml.org | tee config.yml")

        j.do.execute('chown git:git -R /home/git')
        j.do.execute('usermod -a -G root git')
   # Configure Enginx
#        if not j.do.isFile('/etc/nginx/sites-available/gitlab'):
#            j.do.copyFile('/home/git/gitlab/lib/support/nginx/gitlab', '/etc/nginx/sites-available/gitlab')
#        if not j.do.isLink('/etc/nginx/sites-enabled/gitlab'):
#            j.do.execute('ln -s /etc/nginx/sites-available/gitlab /etc/nginx/sites-enabled/gitlab')
#            j.do.delete('/etc/nginx/sites-enabled/default')
   # Configure Enginx
        if not j.do.isFile('/opt/nginx/cfg/sites-available/gitlab'):
            j.do.copyFile('/home/git/gitlab/lib/support/nginx/gitlab', '/opt/nginx/cfg/sites-available/gitlab')
        if not j.do.isLink('/opt/nginx/cfg/sites-enabled/gitlab'):
            j.do.execute('ln -s /opt/nginx/cfg/sites-available/gitlab /opt/nginx/cfg/sites-enabled/gitlab')
            j.do.delete('/opt/nginx/cfg/sites-enabled/default')

        j.do.copyFile('/home/git/gitlab/config/resque.yml', '/home/git/gitlab/config/resque.yml.org')
        j.do.execute("sed 's/production:\ unix:.*/production:\ unix:\/opt\/jumpscale7\/var\/redis\/gitlab\/redis.sock/' /home/git/gitlab/config/resque.yml.org | tee /home/git/gitlab/config/resque.yml")
        os.system("cd /home/git/gitlab-shell && sudo -u git -H git fetch && sudo -u git -H git checkout v`cat /home/git/gitlab/GITLAB_SHELL_VERSION`")
        os.system("sudo -u git -H RAILS_ENV=production bin/background_jobs start")
        os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake gitlab:setup RAILS_ENV=production")
        os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake gitlab:env:info RAILS_ENV=production")
        os.system("cd /home/git/gitlab && sudo -u git -H bundle exec rake assets:precompile RAILS_ENV=production")
#        j.do.execute('service nginx restart')

        print('userName: root\npassword: 5iveL!fe')
        return True

    # def stop(self,**args):
    #     """
    #     if you want a gracefull shutdown implement this method
    #     a uptime check will be done afterwards (local)
    #     return True if stop was ok, if not this step will have failed & halt will be executed.
    #     """
    #     return True

    # def halt(self,**args):
    #     """
    #     hard kill the app, std a linux kill is used, you can use this method to do something next to the std behaviour
    #     """
    #     return True

    # def check_uptime_local(self,**args):
    #     """
    #     do checks to see if process(es) is (are) running.
    #     this happens on system where process is
    #     """
    #     return True

    # def check_requirements(self,**args):
    #     """
    #     do checks if requirements are met to install this app
    #     e.g. can we connect to database, is this the right platform, ...
    #     """
    #     return True

    # def monitor_local(self,**args):
    #     """
    #     do checks to see if all is ok locally to do with this package
    #     this happens on system where process is
    #     """
    #     return True

    # def monitor_remote(self,**args):
    #     """
    #     do checks to see if all is ok from remote to do with this package
    #     this happens on system from which we install or monitor (unless if defined otherwise in hrd)
    #     """
    #     return True

    # def cleanup(self,**args):
    #     """
    #     regular cleanup of env e.g. remove logfiles, ...
    #     is just to keep the system healthy
    #     """
    #     return True

    # def data_export(self,**args):
    #     """
    #     export data of app to a central location (configured in hrd under whatever chosen params)
    #     return the location where to restore from (so that the restore action knows how to restore)
    #     we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
    #     """
    #     return False

    # def data_import(self,id,hrd,**args):
    #     """
    #     import data of app to local location
    #     if specifies which retore to do, id corresponds with line item in the $name.export file
    #     """
    #     return False

    # def uninstall(self,**args):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass

