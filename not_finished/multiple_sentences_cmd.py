#We are trying to enter the server, and automatize the process of importing
#data into geoserver production, but it is not possible, since we need more than one
# sentence to proceed, and we can only execute one

#command (Windows powershell): ssh bc3@192.168.250.1
#password: Sis-8905
import paramiko
import time

hostname = '192.168.250.1'
username = 'bc3'
port = 22
password = 'Sis-8905'

#We set the parameters to create the connection to the server
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.connect(hostname, port, username, password)

#here are all the commands
commands =['docker exec -it demo_geoserver.1.o3h9jxv7suzw2srtxb29ekzc4 bash', 'cd /opt/geoserver/data_dir/', 'dir'
]

for command in commands:
      print(f"{'#'*10} Executing the Command : {command} {'#'*10}")
      stdin, stdout, stderr = ssh.exec_command(command)
      time.sleep(.5)
      print(stdout.read().decode())