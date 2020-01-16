import certifi
import glob

certifi_cert_file = certifi.where()
custom_certificates_path = 'custom_certificates/*.pem'

for cert_file in glob.glob(custom_certificates_path):
    with open(cert_file, 'rb') as opened:
        custom_cert = opened.read()

    with open(certifi_cert_file, 'ab') as opened:
        opened.write(custom_cert)
