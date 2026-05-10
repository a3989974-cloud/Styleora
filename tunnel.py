import subprocess, os

proc = subprocess.Popen(
    ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=3',
     '-i', os.path.expanduser('~/.ssh/serveo_key'),
     '-N', '-R', 'styleora:80:127.0.0.1:8000', 'serveo.net'],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
)
with open(os.path.join(os.path.dirname(__file__), 'tunnel_url.txt'), 'w') as f:
    f.write('https://styleora.serveo.net')
print('https://styleora.serveo.net')
proc.wait()
