from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import os.path

def log(message):
    print(' :: ' + message)

class Actions(ActionsBase):

    def build(self,serviceobject):
        
        BUILD_BASE = '/opt/build/odoo'
        PKG = BUILD_BASE + '/pkg'
        j.system.fs.createDir(BUILD_BASE)

        APT_DEPS = ('libpq-dev', 'libxml2-dev', 'libxslt1-dev', 'python-dev', 'libldap2-dev', 'libsasl2-dev', 'python-virtualenv') 
        for dep in APT_DEPS:
            log('Installing ubuntu dep: ' + dep)
            j.system.platform.ubuntu.install(dep)
        
        SOURCE_TARBALL_URL = 'https://github.com/odoo/odoo/archive/8.0.0.tar.gz'
        log('Downloading source tarball')
        local_file = os.path.join(BUILD_BASE, 'odoo.tar.gz')
        j.system.net.downloadIfNonExistent(SOURCE_TARBALL_URL, local_file, md5_checksum='a92253ea9e07b9bca7f1a4de2bb7d371')

        log('Extracting downloaded files')
        uncompressed_path = os.path.join(BUILD_BASE, 'uncompressed')
        j.system.fs.targzUncompress(local_file, uncompressed_path)

        if j.system.fs.exists(PKG):
            j.system.fs.removeDirTree(PKG)

        log('Copying over the extracted files')
        j.system.fs.copyDirTree(os.path.join(uncompressed_path, 'odoo-8.0.0'), PKG)
        
        def python_deps():
            return open(os.path.join(PKG, 'requirements.txt')).read().split()

        for python_dep in python_deps():
            install_path = os.path.join(PKG, 'pip-' + python_dep)
            install_command = 'pip install --exists-action=w --target="%(target)s" %(dep)s' % {'dep': python_dep, 'target': install_path}
            log(install_command)
            j.action.start(name='pip install ' + python_dep, cmds=install_command, jp=self.jp_instance)
            copy_command = 'cp -r %(install_path)s/* %(pkg_path)s/' % {'install_path': install_path, 'pkg_path': PKG}
            log(copy_command)
            j.action.start(name='pip copy installed ' + python_dep, cmds=copy_command, jp=self.jp_instance)

            # Delete all the leftover 'pip-*' directories
            command = 'rm -r %s/pip-*' % PKG
            log(command)
            j.action.start(name='pip delete leftover pip files', cmds=command, jp=self.jp_instance)
            
            # Install npm dependencies
            for npm_dep in ('less', 'less-plugin-clean-css'):
                command = '/opt/nodejs/bin/npm install -g ' + npm_dep
                j.action.start(name='npm-install ' + npm_dep, cmds=command, jp=self.jp_instance)
            

    def configure(self, serviceObj):

        if not j.system.unix.unixUserExists('odoo'):
            j.system.unix.addSystemUser('odoo', homedir='/var/lib/odoo')

        user_commands = 'sudo -u postgres /opt/postgresql/bin/createuser -s -w $(param.db.user); sudo -u postgres /opt/postgresql/bin/psql --command "ALTER USER $(param.db.user) WITH PASSWORD \'$(param.db.password)\'"' 
        j.action.start(name='Create Postgresql odoo user', cmds=user_commands, jp=self.jp_instance)

        # Copy over the files from the model_database
        j.system.fs.copyDirTree(os.path.join(self.jp_instance.hrd.get('param.base'), 'model_database/filestore'), '/var/lib/odoo/.local/share/Odoo/filestore')
        j.system.fs.chown('/var/lib/odoo/', 'odoo')
        
        # Load the database dump from model_databasse
        commands = 'sudo -u $(param.db.user) /opt/postgresql/bin/createdb codescalers ; sudo -u $(param.db.user) /opt/postgresql/bin/psql -f %(sql_dump_path)s codescalers' % {'sql_dump_path': os.path.join(self.jp_instance.hrd.get('param.base'), 'model_database/dump.sql')}
        j.action.start(name='Load model database image', cmds=commands, jp=self.jp_instance)
