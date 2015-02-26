from JumpScale import j
import JumpScale.baselib.sslsigning
import OpenSSL

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):


    def configure(self,serviceobject):
        """
        generate configuration for openvpn
        """
        path = serviceobject.hrd.get('param.ca.dir')

        cacrt_filename = "%s/ca.crt"%path
        cakey_filename = "%s/ca.key"%path
        j.system.fs.removeDirTree(path)
        j.system.fs.createDir(path)
        #generate self-signed cert and keypair if not present if path
        j.tools.sslSigning.create_self_signed_ca_cert(path)

        cacert_filecontent=j.system.fs.fileGetContents(cacrt_filename)
        cakey_filecontent=j.system.fs.fileGetContents(cakey_filename)
        ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,cacert_filecontent)
        ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,cakey_filecontent)

        j.tools.sslSigning.createSignedCert(path, "$(param.keyname)")
        hostname = j.system.net.getHostname()
        prikey,req=j.tools.sslSigning.createCertificateSigningRequest(hostname)
        clientcert=j.tools.sslSigning.signRequest(req, ca_cert, ca_key)

        serviceobject.hrd.set('openvpn.client.crt',clientcert)
        serviceobject.hrd.set('openvpn.client.crt',prikey)
        serviceobject.hrd.set('openvpn.ca.crt',cacert_filecontent)

        config = """
    client
    dev tunW
    remote %s %s
    ca ca.crt
    proto tcp
    cert %s.crt
    key %s.key
    keepalive 10 120
    verb 4
    connect-retry 20
    """ % ('$(param.remote.ip)', '$(param.port)',
              '$(param.keyname)',
              '$(param.keyname)')

        j.system.fs.writeFile('/etc/openvpn/%s.crt'% "$(param.keyname)", clientcert)
        j.system.fs.writeFile('/etc/openvpn/%s.key'% "$(param.keyname)", prikey)
        j.system.fs.writeFile('/etc/openvpn/%s.conf'% "$(param.keyname)", config)

        return True

    def removedata(self, serviceObj):
        j.system.fs.removeDirTree("$(param.dest.dir)")
        return True