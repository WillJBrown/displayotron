import os
import subprocess

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
    return output


def getcputemp():
    temp_c = run_cmd('/bin/cat /sys/class/thermal/thermal_zone0/temp').decode()
    return float(temp_c)/1000

def getgputemp():
    temp_g = run_cmd('/opt/vc/bin/vcgencmd measure_temp').decode()
    temp_g = temp_g.split('=')[1]
    temp_g = temp_g.split('\'')[0]
    return float(temp_g)

def getcpuclock():
    cpu_clk = run_cmd('/opt/vc/bin/vcgencmd measure_clock arm').decode()
    cpu_clk = cpu_clk.split('=')[1]
    return float(cpu_clk)/1000000000

def getgpuclock():
    gpu_clk = run_cmd('/opt/vc/bin/vcgencmd measure_clock v3d').decode()
    gpu_clk = gpu_clk.split('=')[1]
    return float(gpu_clk)/1000000000
