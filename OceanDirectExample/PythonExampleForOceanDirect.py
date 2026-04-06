# -*- coding: utf-8 -*-
# main code starts on line 419
"""
Created on Fri Jun  5 15:58:47 2020

@author: Ocean Insight Inc.
"""
from oceandirect.OceanDirectAPI import OceanDirectAPI, OceanDirectError, FeatureID
import argparse, os
from datetime import datetime
from collections import deque

def printBinary(value):
    bitCount = 32 #32 bits
    numValue = int(value)

    print("bits (%d) = " % numValue, end='')
    for i in range(32, -1, -1):
        print("%d " % ((numValue >> i) & 0x01), end='')

    print(" ")

def acquisitionDelay(device):
    #device.set_acquisition_delay(120)
    #print("acquisitionDelay(device): set acqDelay 120")

    acqDelay    = device.get_acquisition_delay()
    acqDelayInc = device.get_acquisition_delay_increment()
    acqDelayMin = device.get_acquisition_delay_minimum()
    acqDelayMax = device.get_acquisition_delay_maximum()

    print("acquisitionDelay(device): acqDelay     =  %d " % acqDelay)
    print("acquisitionDelay(device): acqDelayInc  =  %d " % acqDelayInc)
    print("acquisitionDelay(device): acqDelayMin  =  %d " % acqDelayMin)
    print("acquisitionDelay(device): acqDelayMax  =  %d " % acqDelayMax)
    print("")

    #400us
    value = 400
    device.set_acquisition_delay(value)
    print("acquisitionDelay(device): set acqDelay =  %d " % value)

    acqDelay = device.get_acquisition_delay()
    print("acquisitionDelay(device): get acqDelay(expected 400)  =  %d " % acqDelay)
    print("")


def gpio(device):
    supported = device.is_feature_id_enabled(FeatureID.GPIO)
    print("gpio(device): GPIO feature supported  = %s" % supported)

    if not supported:
        print("")
        return

    tempCount = device.Advanced.get_gpio_pin_count()
    print("gpio(device): pin count          =  %d " % tempCount)

    try:
        outputVector = device.Advanced.gpio_get_output_enable2()
        printBinary(outputVector)
        print("---------------------------------------------------------------\n\n")
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))

    try:
        device.Advanced.gpio_set_output_enable1(0, 1)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(0)
        print("gpio(device): set output vector bits / mask     =  00000000 / 0(True)")
        print("gpio(device): get bit(0) output                 =  0(%s)" % bitOutput1)
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00000001")
        printBinary(outputVector)
        print("\n")

        device.Advanced.gpio_set_output_enable1(2, 1)
        device.Advanced.gpio_set_output_enable1(3, 1)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(2)
        bitOutput2 = device.Advanced.gpio_get_output_enable1(3)
        print("gpio(device): set output vector bits / mask     =  00000001 / 2(True),3(True)")
        print("gpio(device): get bit(2,3) output               =  2(%s) / 3(%s)" % (bitOutput1, bitOutput2) )
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00001101")
        printBinary(outputVector)
        print("\n")

        device.Advanced.gpio_set_output_enable1(0, 0)
        device.Advanced.gpio_set_output_enable1(1, 1)
        device.Advanced.gpio_set_output_enable1(3, 0)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(0)
        bitOutput2 = device.Advanced.gpio_get_output_enable1(1)
        bitOutput3 = device.Advanced.gpio_get_output_enable1(3)
        print("gpio(device): set output vector bits / mask     =  00001101 / 0(False),True(1),3(False)")
        print("gpio(device): get bit(0,1,3) output             =  0(%s) / 1(%s) / 3(%s)" % (bitOutput1, bitOutput2, bitOutput3))
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00000110")
        printBinary(outputVector)
        print("\n")

        device.Advanced.gpio_set_output_enable1(0, 1)
        device.Advanced.gpio_set_output_enable1(3, 1)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(0)
        bitOutput2 = device.Advanced.gpio_get_output_enable1(3)
        print("gpio(device): set output vector bits / mask     =  00000110 / 0(True),3(True)")
        print("gpio(device): get bit(0,3) output               =  0(%s) / 3(%s)" % (bitOutput1, bitOutput2))
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00001111")
        printBinary(outputVector)
        print("")
        print("---------------------------------------------------------------\n\n")
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): gpio_output_bits() / %d = %s" % (errorCode, errorMsg))

    try:
        device.Advanced.gpio_set_value1(0, 1)
        device.Advanced.gpio_set_value1(1, 1)
        value1 = device.Advanced.gpio_get_value1(0)
        value2 = device.Advanced.gpio_get_value1(1)
        print("gpio(device): set value vector values / mask   =  00000000 / 0(True), 1(True)")
        print("gpio(device): get bit(0,1) value               =  0(%s) / 1(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00000011")
        printBinary(valueVector)
        print("")

        device.Advanced.gpio_set_value1(2, 1);
        device.Advanced.gpio_set_value1(3, 1);
        value1 = device.Advanced.gpio_get_value1(2)
        value2 = device.Advanced.gpio_get_value1(3)
        print("gpio(device): set value vector values / mask   =  00000011 / 2(True),3(True)")
        print("gpio(device): get bit(2,3) value               =  2(%s) / 3(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00001111")
        printBinary(valueVector)
        print("")

        device.Advanced.gpio_set_value1(0, 0)
        device.Advanced.gpio_set_value1(2, 0)
        value1 = device.Advanced.gpio_get_value1(0)
        value2 = device.Advanced.gpio_get_value1(2)
        print("gpio(device): set value vector values / mask   =  00001111 / 0(False), 2(False)")
        print("gpio(device): get bit(0,2) value               =  0(%s) / 2(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00001010")
        printBinary(valueVector)
        print("")

        device.Advanced.gpio_set_value1(1, 0)
        device.Advanced.gpio_set_value1(3, 0)
        value1 = device.Advanced.gpio_get_value1(1)
        value2 = device.Advanced.gpio_get_value1(3)
        print("gpio(device): set value vector values / mask   =  00001010 / 1(False), 3(False)")
        print("gpio(device): get bit(1,3) value               =  1(%s) / 3(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00000000")
        printBinary(valueVector)
        print("\n")

    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))

    #Output bit masks
    try:
        #15 = 1111
        device.Advanced.gpio_set_output_enable2(15)
        print("gpio(device): set output mask(15)        =  00001111")

        mask = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): expecting output mask (15) =  %d" % mask)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))

    #Value bit masks
    try:
        #12 = 1100
        device.Advanced.gpio_set_value2(12)
        print("")
        print("gpio(device): set value mask(12)        =  00001100")

        mask = device.Advanced.gpio_get_value2()
        print("gpio(device): expecting value mask (12) =  %d" % mask)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))
    print("")

def singleStrobe(device):
    values = [False, True]
    for enable in values:
        device.Advanced.set_single_strobe_enable(enable);
        print("singleStrobe(device): set enable      =  %s " % enable)

        enable2 = device.Advanced.get_single_strobe_enable();
        print("singleStrobe(device): get enable      =  %s " % enable2)
        print("")

    device.Advanced.set_single_strobe_enable(True);
    enable = device.Advanced.get_single_strobe_enable()
    print("singleStrobe(device): enable(True)    =  %s " % enable)


    strobeWidth = 552
    device.Advanced.set_single_strobe_width(strobeWidth)
    print("singleStrobe(device): set strobeWidth =  %d " % strobeWidth)
    strobeWidth = device.Advanced.get_single_strobe_width()
    print("singleStrobe(device): get strobeWidth =  %d " % strobeWidth)
    print("")

    strobeDelay = 322
    device.Advanced.set_single_strobe_delay(strobeDelay)
    print("singleStrobe(device): set strobeDelay =  %d " % strobeDelay)
    strobeDelay = device.Advanced.get_single_strobe_delay()
    print("singleStrobe(device): get strobeDelay =  %d " % strobeDelay)
    print("")

    enable2 = device.Advanced.get_single_strobe_enable();
    print("singleStrobe(device): get enable      =  %s " % enable2)
    print("")

    try:
        delayMin = device.Advanced.get_single_strobe_delay_minimum()
        print("singleStrobe(device): delayMin         =  %d " % delayMin)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_delay_minimum() %d = %s" % (errorCode, errorMsg))

    try:
        delayMax = device.Advanced.get_single_strobe_delay_maximum()
        print("singleStrobe(device): delayMax         =  %d " % delayMax)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_delay_maximum() %d = %s" % (errorCode, errorMsg))

    try:
        delayInc = device.Advanced.get_single_strobe_delay_increment()
        print("singleStrobe(device): delayInc         =  %d " % delayInc)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_delay_increment() %d = %s" % (errorCode, errorMsg))

    try:
        widthMin = device.Advanced.get_single_strobe_width_minimum()
        print("singleStrobe(device): widthMin         =  %d " % widthMin)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_width_minimum() %d = %s" % (errorCode, errorMsg))

    try:
        widthMax = device.Advanced.get_single_strobe_width_maximum()
        print("singleStrobe(device): widthMax         =  %d " % widthMax)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_width_maximum() %d = %s" % (errorCode, errorMsg))

    try:
        widthInc = device.Advanced.get_single_strobe_width_increment()
        print("singleStrobe(device): widthInc         =  %d " % widthInc)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_width_increment() %d = %s" % (errorCode, errorMsg))

    try:
        cycleMax = device.Advanced.get_single_strobe_cycle_maximum()
        print("singleStrobe(device): cycleMax         =  %d " % cycleMax)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("singleStrobe(device): get_single_strobe_cycle_maximum() %d = %s" % (errorCode, errorMsg))
    print("")

def continuousStrobe(device):
    periodInc = 0
    try:
        periodInc = device.Advanced.get_continuous_strobe_period_increment()
        print("continuousStrobe(device): period increment =  %d " % periodInc)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("continuousStrobe(device): get_continuous_strobe_period_increment() %d = %s" % (errorCode, errorMsg))

    strobePeriod = device.Advanced.get_continuous_strobe_period()
    print("continuousStrobe(device): get strobePeriod =  %d " % strobePeriod)

    strobeEnable = device.Advanced.get_continuous_strobe_enable()
    print("continuousStrobe(device): get strobeEnable =  %s " % strobeEnable)

    values = [False, True]
    for enable in values:
        device.Advanced.set_continuous_strobe_enable(False)
        print("continuousStrobe(device): get strobeEnable =  %s " % enable)
        strobeEnable = device.Advanced.get_continuous_strobe_enable()
        print("continuousStrobe(device): set strobeEnable =  %s " % enable)
        print("")

    try:
        periodMin = device.Advanced.get_continuous_strobe_period_minimum()
        print("continuousStrobe(device): periodMin          =  %d " % periodMin)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("continuousStrobe(device): get_continuous_strobe_period_minimum() %d = %s" % (errorCode, errorMsg))

    try:
        periodMax = device.Advanced.get_continuous_strobe_period_maximum()
        print("continuousStrobe(device): periodMax          =  %d " % periodMax)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("continuousStrobe(device): get_continuous_strobe_period_maximum() %d = %s" % (errorCode, errorMsg))



    strobePeriodList = [1200, 1505, 800, 453]
    for period in strobePeriodList:
        if (periodInc > 1) and ((period % periodInc) != 0):
            print("continuousStrobe(device): set strobePeriod =  %d  ====> ********* expecting EXCEPTION!" % period)

        try:
            device.Advanced.set_continuous_strobe_period(period)
            print("continuousStrobe(device): set strobePeriod =  %d " % period)
        except OceanDirectError as err:
            [errorCode, errorMsg] = err.get_error_details()
            print("continuousStrobe(device): set_continuous_strobe_period() %d = %s" % (errorCode, errorMsg))

        try:
            period = device.Advanced.get_continuous_strobe_period()
            print("continuousStrobe(device): get strobePeriod =  %d " % period)
        except OceanDirectError as err:
            [errorCode, errorMsg] = err.get_error_details()
            print("continuousStrobe(device): get_continuous_strobe_period() %d = %s" % (errorCode, errorMsg))
        print("")

    try:
        strobeWidth = 216
        device.Advanced.set_continuous_strobe_width(strobeWidth)
        print("continuousStrobe(device): set strobeWidth    =  %d " % strobeWidth)

        strobeWidth = device.Advanced.get_continuous_strobe_width()
        print("continuousStrobe(device): get strobeWidth    =  %d " % strobeWidth)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("continuousStrobe(device): %d = %s" % (errorCode, errorMsg))

    print("")

def scanToAverageBoxcar(device, scanToAve, boxcarWidth):
    try:
        value = device.get_scans_to_average()
        print("scanToAverageBoxcar(): cur scans_to_average        =  %d" % value)

        value = device.get_integration_time()
        print("scanToAverageBoxcar(): current integrationTimeUs   =  %d" % value)

        minAveIntTime = device.get_minimum_averaging_integration_time()
        print("scanToAverageBoxcar(): minAverageIntegrationTimeUs =  %d" % minAveIntTime)
        print("")
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("scanToAverageBoxcar(): set/get / %d = %s" % (errorCode, errorMsg))

    try:
        print("scanToAverageBoxcar(): set_scans_to_average        =  %d" % scanToAve)
        device.set_scans_to_average(scanToAve)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("scanToAverageBoxcar(): ERROR with code/scanToAverage, %d = %s ************" % (errorCode, scanToAve))

    try:
        value = device.get_scans_to_average()
        print("scanToAverageBoxcar(): get_scans_to_average        =  %d" % value)

    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("scanToAverageBoxcar(device): set/get / %d = %s" % (errorCode, errorMsg))

    try:
        device.set_boxcar_width(boxcarWidth)
        print("scanToAverageBoxcar(): set_boxcar_width            =  %d" % boxcarWidth)

        value = device.get_boxcar_width()
        print("scanToAverageBoxcar(): get_boxcar_width            =  %d" % value)

    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("scanToAverageBoxcar(): set/get / %d = %s" % (errorCode, errorMsg))
    print("")

def get_spec_formatted(device, sn):
    try:
        #100ms
        device.set_integration_time(100000); # In microseconds
        print("Reading spectra for dev s/n = %s" % sn, flush=True)
        for i in range(1):
            spectra = device.get_formatted_spectrum()
            wavelength = device.get_wavelengths()
            # 4.615 pixels per 1 nm from base 345 nm
            # 3648 Total pixels over 349 nm - 1046 nm
            # Spectra - intensity counts from pixel
            # Wavelength - wavelength in [nm] from pixel
            '''
            #Background test 1
            print("spectra [%d] \u03BB = %0.3f - %0.3f: %d, %d, %d, %d, %d, %d" % (i, wavelength[0], wavelength[5], spectra[0], spectra[1], spectra[2], spectra[3], spectra[4], spectra[5]), flush=True)
            # Delta peak lambda = 410.17 nm
            print("spectra [%d] \u03BB = %0.3f - %0.3f: %d, %d, %d, %d, %d, %d" % (i, wavelength[300], wavelength[305], spectra[300], spectra[301], spectra[302], spectra[303], spectra[304], spectra[305]), flush=True)
            # Gamma peak lambda = 434.04 nm
            print("spectra [%d] \u03BB = %0.3f - %0.3f: %d, %d, %d, %d, %d, %d" % (i, wavelength[410], wavelength[415], spectra[410], spectra[411], spectra[412], spectra[413], spectra[414], spectra[415]), flush=True)
            # Beta peak lambda = 486.14 nm
            print("spectra [%d] \u03BB = %0.3f - %0.3f: %d, %d, %d, %d, %d, %d" % (i, wavelength[657], wavelength[662], spectra[657], spectra[658], spectra[659], spectra[660], spectra[661], spectra[662]), flush=True)
            #Background test 2
            print("spectra [%d] \u03BB = %0.3f - %0.3f: %d, %d, %d, %d, %d, %d" % (i, wavelength[750], wavelength[755], spectra[750], spectra[751], spectra[752], spectra[753], spectra[754], spectra[755]), flush=True)
            '''

            # Write to file
            # epoch time (s)  - Since Jan 1st, 1970
            directory = "Spectroscopy_Results"
            filename = "Spectra_output_%d_%d.txt" % (i, int(datetime.now().timestamp()))
            write_lists_to_file(wavelength, spectra, directory, filename)

        print("len(spectra) =  %d" % (device.get_formatted_spectrum_length()))
    except OceanDirectError as e:
        [errorCode, errorMsg] = err.get_error_details()
        print("get_spec_formatted(device): exception / %d = %s" % (errorCode, errorMsg))

def get_spec_raw_with_meta(device, sn):
    try:
        #100ms
        device.set_integration_time(100000);

        print("[START] Reading spectra for dev s/n = %s" % sn, flush=True)
        for i in range(10):
            spectra = []
            timestamp = []
            total_spectra = device.Advanced.get_raw_spectrum_with_metadata(spectra, timestamp, 3)
            print("len(spectra) =  %d" % (total_spectra) )

            #print sample count on each spectra
            for x in range(total_spectra):
                print("spectraWithMetadata: %d ==>  %d, %d, %d, %d" % (timestamp[x], spectra[x][100], spectra[x][101], spectra[x][102], spectra[x][103]))
    except OceanDirectError as e:
        [errorCode, errorMsg] = err.get_error_details()
        print("get_spec_raw_with_meta(device): exception / %d = %s" % (errorCode, errorMsg))

def write_lists_to_file(list1, list2, directory, filename, title1="Wavelength [nm]"
, title2="Intensity [counts]"):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    # Ensure the lists are of the same length
    max_length = max(len(list1), len(list2))
    list1 += [""] * (max_length - len(list1))  # Pad list1 if needed
    list2 += [""] * (max_length - len(list2))  # Pad list2 if needed
    # Determine max width needed for indicies
    max_width1 = max(len(f"{item:.20g}") for item in list1)
    #max_width2 = max(len(f"{item:.20g}") for item in list2)
    list1 = [title1] + list1
    list2 = [title2] + list2

    with open(filepath, "w") as file:
        for item1, item2 in zip(list1, list2):
            # Format item position based on width
            item1_str = f"{item1:.20g}" if isinstance(item1, (int, float)) else str(item1)
            item2_str = f"{item2:.20g}" if isinstance(item2, (int, float)) else str(item2)
            file.write(f"{item1_str:<{max_width1}}\t{item2_str}\n")
            #file.write(f"{item1}\t\t{item2}\n")

if __name__ == "__main__":
    #
    # To test this file quickly, do the following:
    # 1. Copy this file into <install_folder>\Python (ex: C:\Program Files\Ocean Insight\OceanDirect SDK-1.31.0\Python)
    # 2. Open a window shell and go to that folder
    # 3. Run this command:  python3 .\PythonExampleForOceanDirect.py
    #
    od = OceanDirectAPI()
    od.set_multicast_msg_send_retry(2)            # Number of times to send probing message
    od.set_multicast_msg_response_read_retry(4)   # Number of times to read probing response.
    od.set_multicast_msg_response_read_delay(300) # Delay before reading probing response.
    try:
        print("Network configuration initiated")
        od.add_network_device("192.168.4.240", "OceanSR4") # 172.30.63.171
        #od.add_network_device("172.30.63.171", "OceanSR4") # 172.30.63.171
        device_count = od.find_devices()
    except:
        device_count = od.find_usb_devices()
        if device_count > 0: print("USB configuration initiated")
    device_ids = od.get_device_ids()

    (major, minor, point) = od.get_api_version_numbers()
    print("API Version  : %d.%d.%d " % (major, minor, point))
    print("Total Devices : %d     \n" % device_count)
    #print("Device IDs (bus label): " % device_ids)
    #od.close_device(id)

    if device_count == 0:
        print("No device found.")
    else:
        for id in device_ids:
            try:
                device = od.open_device(id)
                print("Device : %d       " % id)
            except OceanDirectError as err:
                [errorCode, errorMsg] = err.get_error_details()
                print("main(): open_device() %d = %s" % (errorCode, errorMsg))
                od.close_device(id)
                continue
            try:
                serialNumber = device.get_serial_number()
                print("Serial Number: %s     \n" % serialNumber)
            except OceanDirectError as err:
                [errorCode, errorMsg] = err.get_error_details()
                print("main(): get_serial_number() %d = %s" % (errorCode, errorMsg))
                continue

            # The interface type which could be one 0(Loopback), 1(wired ethernet), 2 (WIFI), and 3 (USB - CDC Ethernet).
            '''NOT SUPPORTED: print("Network Status", device.Advanced.get_network_interface_status(3))'''
            # Ethernet configuration
            '''NOT SUPPORTED: print("Ethernet Status", device.Advanced.get_ethernet_gigabit_enable_status(3))'''
            #print(device.Advanced.get_ip_address_assigned_mode()) # True (False) if the ip address was generated via DHCP (static)
            #print(device.Advanced.ipv4_is_dhcp_enabled(0))
            #print(device.Advanced.ipv4_get_number_of_ip_addresses(0))
            #device.Advanced.ipv4_set_dhcp_enable(0, False)

            get_spec_formatted(device, serialNumber)

            # If devices don't support metadata then you will get an exception.
            #get_spec_raw_with_meta(device, serialNumber)
            #gpio(device)

            print("Baseline %d" % device.Advanced.get_autonull_baseline_level())
            print("Max ADC Count %d" % device.Advanced.get_autonull_maximum_adc_count())
            print("Saturation Level %d" % device.Advanced.get_autonull_saturation_level())
            #print("Bad Pixel Range", device.Advanced.get_bad_pixel_indices())
            #print("Active Pixel Range", device.Advanced.get_active_pixel_range())
            #print("Optical Dark Pixel Range", device.Advanced.get_optical_dark_pixel_range())
            #print("Transition Pixel Range", device.Advanced.get_transition_pixel_range())
            print("Closing device!\n")
            od.close_device(id)
    od.shutdown()
    print("**** exiting program ****")
