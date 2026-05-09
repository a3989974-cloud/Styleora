import subprocess, re, sys, os, signal

proc = subprocess.Popen(
    ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=NUL', '-o', 'ServerAliveInterval=30', '-R', '80:localhost:8000', 'nokey@localhost.run'],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
)
url = None
for line in iter(proc.stdout.readline, ''):
    m = re.search(r'https://([\w-]+\.lhr\.life)', line)
    if m:
        url = m.group(0)
        with open(os.path.join(os.path.dirname(__file__), 'tunnel_url.txt'), 'w') as f:
            f.write(url)
        print(url, flush=True)
        break
proc.wait()
