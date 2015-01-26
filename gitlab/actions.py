from JumpScale import j
import os

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
    #Install dep
        j.do.execute('apt-get install -y build-essential zlib1g-dev libyaml-dev libssl-dev libgdbm-dev libreadline-dev libncurses5-dev libffi-dev checkinstall libxml2-dev')
        j.do.execute('apt-get install -y libxslt-dev libcurl4-openssl-dev libicu-dev logrotate python-docutils libkrb5-dev cmake')
        # j.system.platform.ubuntu.checkInstall('sudo', 'sudo')
        # j.system.platform.ubuntu.checkInstall('openssh-server', 'ssh')
        j.system.platform.ubuntu.checkInstall('curl', 'curl')
        j.system.platform.ubuntu.checkInstall('pkg-config', 'pkg-config')
        j.system.platform.ubuntu.checkInstall('git', 'git')
#        j.do.execute('apt-get install -y gcc')
        j.system.platform.ubuntu.checkInstall('postfix', 'postfix')

   # Install Ruby
        # j.do.createDir('/tmp/ruby')
        # j.do.chdir('/tmp/ruby')
        # j.do.execute('curl -L --progress http://cache.ruby-lang.org/pub/ruby/2.1/ruby-2.1.5.tar.gz | tar xz')
        # j.do.chdir('/tmp/ruby/ruby-2.1.5')
        # j.do.execute('./configure --disable-install-rdoc')
        # os.system('cd /tmp/ruby/ruby-2.1.5 && make')
        # j.do.execute('make install')

   # Add git user
        j.do.execute('adduser --disabled-login --gecos \'GitLab\' git')
        j.do.createDir('/home/git/gitlab')

   # Install postgresql 9.3
        j.system.platform.ubuntu.checkInstall('postgresql-9.3', 'psql')
        j.system.platform.ubuntu.checkInstall('postgresql-client', 'psql')
        j.do.execute('apt-get install -y libpq-dev')
        cmd = """
        export LC_ALL=$LANG
        export  LANGUAGE=$LANG
        pg_createcluster 9.3 main --start &&
        service postgresql start &&
        sudo -u postgres psql -d template1 -c 'CREATE USER git CREATEDB' &&
        sudo -u postgres psql -d template1 -c 'CREATE DATABASE gitlabhq_production OWNER git'
        """
        j.do.execute(cmd)

   # Install Redis server 

        j.system.platform.ubuntu.checkInstall('redis-server', 'redis-server')
        j.do.copyFile('/etc/redis/redis.conf', '/etc/redis/redis.conf.orig')
        j.do.execute("sed 's/^port .*/port 0/' /etc/redis/redis.conf.orig | sudo tee /etc/redis/redis.conf")
        filee = j.do.readFile('/etc/redis/redis.conf') + '\nunixsocket /var/run/redis/redis.sock' + '\nunixsocketperm 770'
        j.do.writeFile('/etc/redis/redis.conf', filee)
        if not j.do.isDir('/var/run/redis'):
            j.do.createDir('/var/run/redis')
        j.do.chown('/var/run/redis', 'redis')
        j.do.execute('chmod 755 /var/run/redis')
        if j.do.isDir('/etc/tmpfiles.d'):
            j.do.writeFile('/etc/tmpfiles.d/redis.conf', 'd  /var/run/redis  0755  redis  redis  10d  -')
        j.do.execute('service redis-server restart')
        j.do.execute('usermod -aG redis git')

   # Install Enginx
 #       print('userName: root\npassword: 5iveL!fe')
        
        return True
        
    def configure(self,**args):
    #     """
    #     this gets executed when files are installed
    #     this step is used to do configuration steps to the platform
    #     after this step the system will try to start the jpackage if anything needs to be started
    #     """
   # Install gitlab
        j.do.execute('chown git:git -R /home/git')
        j.do.execute('pwd')
        j.do.chdir('/home/git')
        j.do.execute('sudo -u git -H git clone https://git.aydo.com/binary/gitlab-ce.git gitlab')
        j.do.chdir('/home/git/gitlab')
        j.do.copyFile('config/gitlab.yml.example', 'config/gitlab.yml')
        j.do.chown('config/gitlab.yml', 'git')
        j.do.chown('log/', 'git')
        j.do.chown('tmp/', 'git')
        j.do.execute('chmod -R u+rwX,go-w log/ && chmod -R u+rwX tmp/')
        j.do.createDir('/home/git/gitlab-satellites')
        j.do.chown('/home/git/gitlab-satellites', 'git')
        j.do.execute('chmod u+rwx,g=rx,o-rwx /home/git/gitlab-satellites')
        j.do.execute('chmod -R u+rwX tmp/pids/')
        j.do.execute('chmod -R u+rwX tmp/sockets/')
        j.do.execute('chmod -R u+rwX  public/uploads')
        j.do.copyFile('config/unicorn.rb.example', 'config/unicorn.rb')
        j.do.copyFile('config/initializers/rack_attack.rb.example', 'config/initializers/rack_attack.rb')
        j.do.chown('config/', 'git')
        os.system('sudo -u git -H git config --global user.name \"GitLab\"')
        os.system('sudo -u git -H git config --global user.email \"$(param.email)\"')
        os.system("sudo -u git -H git config --global core.autocrlf input")
        j.do.copyFile('config/resque.yml.example', 'config/resque.yml')
        j.do.copyFile('config/database.yml.postgresql', 'config/database.yml')
        j.do.chown('config/resque.yml', 'git')
        j.do.chown('config/database.yml', 'git')
        j.do.execute('sudo -u git -H chmod o-rwx config/database.yml')
        j.do.copyFile('lib/support/init.d/gitlab', '/etc/init.d/gitlab')
        j.do.copyFile('lib/support/init.d/gitlab.default.example', '/etc/default/gitlab')
        j.do.execute('update-rc.d gitlab defaults 21')
        j.do.copyFile('/home/git/gitlab/lib/support/logrotate/gitlab', '/etc/logrotate.d/gitlab')

   # Install bundler Gem
        j.do.copyFile('/etc/login.defs', '/etc/login.defs.org')
        j.do.execute("cd /etc/ && sed 's/ENV_PATH\tPATH=.*/ENV_PATH\tPATH=\/opt\/jumpscale7\/bin:\/usr\/local\/sbin:\/usr\/local\/bin:\/usr\/sbin:\/usr\/bin:\/sbin:\/bin:\/usr\/games:\/usr\/local\/games/' login.defs.org | tee login.defs")
        j.do.execute('chown git:git -R /home/git')
        print 1
        j.do.execute('usermod -a -G root git')
        print 2
        j.do.execute('cd /home/git/gitlab && gem install bundler --no-ri --no-rdoc')
   # Configure Enginx
        if not j.do.isFile('/etc/nginx/sites-available/gitlab'):
            j.do.copyFile('/home/git/gitlab/lib/support/nginx/gitlab', '/etc/nginx/sites-available/gitlab')
        if not j.do.isLink('/etc/nginx/sites-enabled/gitlab'):
            j.do.execute('ln -s /etc/nginx/sites-available/gitlab /etc/nginx/sites-enabled/gitlab')
            j.do.delete('/etc/nginx/sites-enabled/default')
        print 3
        os.system("su - git -c 'cd /home/git/gitlab && bundle install --deployment --without development test mysql aws'")
        print 4
        os.system("su - git -c 'cd /home/git/gitlab && bundle exec rake gitlab:shell:install[v2.4.0] REDIS_URL=unix:/var/run/redis/redis.sock RAILS_ENV=production'")
        os.system("su - git -c 'cd /home/git/gitlab && bundle exec rake gitlab:setup RAILS_ENV=production'")
        os.system("su - git -c 'cd /home/git/gitlab && bundle exec rake gitlab:env:info RAILS_ENV=production'")
        os.system("su - git -c 'cd /home/git/gitlab && bundle exec rake assets:precompile RAILS_ENV=production'")
        j.do.execute('service nginx restart && service gitlab restart')

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