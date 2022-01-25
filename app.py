import subprocess
import sys
import tkinter

from tkinter import Label
from ctypes import windll, create_unicode_buffer

import psutil
import cpuinfo

#init gui
gui = tkinter.Tk()

#window settings
gui.overrideredirect(True)
gui.lift()
gui.wm_attributes("-topmost", True)
gui.wm_attributes("-disabled", True)
gui.config(bg='gray')
gui.wm_attributes("-transparentcolor", "gray")


elements = []
def set_font(name, size):
    for el in elements:
        el.config(font=(name, size))

def get_window():
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    
    # 1-liner alternative: return buf.value if buf.value else None
    if buf.value:
        return buf.value
    else:
        return None

def parse(argv):
    args = {}
    for arg in argv:
        if arg.startswith("--"):
            key, value = arg.replace("--", "").split("=")

            args[key] = value

    return args

def set_position(size, side):
    if side == "topleft":
        data = size+"+0+0"
    elif side == "topright":
        data = size+"-0+0"

    gui.geometry(data)

def nvidia_smi(self, query):
    return str(subprocess.check_output(f"nvidia-smi --query-gpu={query} --format=csv")).replace("\\r", "").split("\\n")[1]

def get_stats():
    gpu_data = str(subprocess.check_output(f"nvidia-smi --query-gpu=utilization.gpu,utilization.memory,temperature.gpu,memory.total,memory.free,memory.used,name --format=csv")).replace("\\r", "").replace(" ", "").split("\\n")[1].split(",")
    cpu_data = cpuinfo.get_cpu_info()
    mem_data = psutil.virtual_memory()

    stats = {
        "gpu": {
            "name": gpu_data[6],
            "usage": gpu_data[0],
            "temperature": gpu_data[2],
            "mem": {
                "usage": gpu_data[1],
                "total": gpu_data[3],
                "free": gpu_data[4],
                "used": gpu_data[5]
            }
        },
        "cpu": {
            "name": cpu_data["brand_raw"],
            "usage": psutil.cpu_percent(),
            "freq": cpu_data["hz_advertised_friendly"]
        },
        "memory": {
            "total": format(mem_data.total/1000000000, '.2f'),
            "used": format(mem_data.used/1000000000, '.2f'),
            "free": format(mem_data.free/1000000000, '.2f'),
            "usage": mem_data.percent
        }
        
    }

    return stats


stats = get_stats()
gpu=Label(text=f"GPU: {stats['gpu']['name']} {stats['gpu']['usage']} ({stats['gpu']['temperature']}C)", background="gray", fg="white")
gpu_mem=Label(text=f"GPU Memory: {stats['gpu']['mem']['usage']} ({stats['gpu']['mem']['used']} / {stats['gpu']['mem']['total']})", background="gray", fg="white")

cpu=Label(text=f"CPU: {stats['cpu']['name']} {stats['cpu']['usage']}% ({stats['cpu']['freq']})", background="gray", fg="white")
mem=Label(text=f"Memory: {stats['memory']['usage']}% ({stats['memory']['used']}GB / {stats['memory']['total']}GB)", background="gray", fg="white")

gpu.place(x=0, y=0)
gpu_mem.place(x=0, y=20)
cpu.place(x=0, y=40)
mem.place(x=0, y=60)


elements.extend([gpu, gpu_mem, cpu, mem])
set_font("Arial", 12)
set_position("600x600", "topleft")

args = parse(sys.argv)

if "apps" in args:
    app_list = args["apps"].split(", ")
else:
    app_list = []

def update_stats():
    stats = get_stats()
    gpu.config(text=f"GPU: {stats['gpu']['name']} {stats['gpu']['usage']} ({stats['gpu']['temperature']}C)")
    gpu_mem.config(text=f"GPU Memory: {stats['gpu']['mem']['usage']} ({stats['gpu']['mem']['used']} / {stats['gpu']['mem']['total']})")
    cpu.config(text=f"CPU: {stats['cpu']['name']} {stats['cpu']['usage']}% ({stats['cpu']['freq']})")
    mem.config(text=f"Memory: {stats['memory']['usage']}% ({stats['memory']['used']}GB / {stats['memory']['total']}GB)")

def update():
    if "all" in args:
        update_stats()
    else:
        pass

    gui.after(1000, update)

#threading.Thread(target=update, daemon=True).start()
gui.after(1000, update)
gui.mainloop()