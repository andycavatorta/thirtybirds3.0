

sudo apt install lm-sensors

sudo sensors-detect  [ manual process.  any way to automate?]

pip3 install PySensors


import sensors
sensors.init()
max_temp = 0
sensors.init()
for chip in sensors.iter_detected_chips():
    for feature in chip:
        if "Core" in feature.label:
            core_temp = int(feature.get_value())
            print(core_temp)
            if core_temp > max_temp:
                max_temp = core_temp

print max_temp

