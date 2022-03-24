####################################               
# Author: Christian Dorfer
# Email: dorfer@aps.ee.ethz.ch                                
####################################

import pyvisa as visa
from time import sleep, time
from configobj import ConfigObj


class KeithleyK2470():

    def __init__(self, conf):
        self.conf = conf
        rm = visa.ResourceManager('@py')
        self._inst = rm.open_resource(self.conf['address'], timeout=self.conf.as_int('timeout_ms'))
        #self.write('ABORt')
        #self.write('*RST')
        sleep(2)
        print("Connected to: ", self.query("*idn?").rstrip())


    def write(self, command):
        self._inst.write(command)
        err = self.get_full_error_queue(verbose=False)
        for e in err:
            if e.split(',')[0] != '0':
                print(f"Errors while writing {command} to instrument")
                print(e)


    def query(self, command):
        try:
            return self._inst.query(command).strip()
        except visa.Error as err:
            msg = f"query '{command}'"
            print(f"\n\nVisaError: {err}\n  When trying {msg}  (full traceback below).")
            print(f"  Have you checked that the timeout (currently "
                  f"{self.timeout:,d} ms) is sufficently long?")
            try:
                self.get_full_error_queue(verbose=True)
                print("")
            except Exception as excep:
                print("Could not retrieve errors from the oscilloscope:")
                print(excep)
                print("")
            raise
        
    def get_full_error_queue(self, verbose=False):
        """All the latest errors from the oscilloscope, upto 30 errors
        (and store to the attribute ``errors``)"""
        errors = []
        for i in range(30):
            err = self._inst.query(":SYSTem:ERRor?").strip()
            if err[:2] == "+0":  # No error
                # Stop querying
                break
            else:
                # Store the error
                errors.append(err)
        if verbose:
            if not errors:
                print("Error queue empty")
            else:
                print("Latest errors from the oscilloscope (FIFO queue, upto 30 errors)")
                for i, err in enumerate(errors):
                    print(f"{i:>2}: {err}")
        return errors


    def close(self):
        self._inst.close()


    def configure(self):
        self.write('system:posetup rst') #reset the instrument
        #self.write('trace:delete "currpts"')

        #settings for enabling up to 2100 readings/second
        self.write(':SENSe:CURRent:NPLCycles 0.1') #set measurement time to 0.01 power line cycles (=0.2ms)
        self.write(':SENSe:CURRent:AZERo:STATe ON') #check if maybe it needs to be disabled for all functions
        self.write(':SOURce:VOLTage:READ:BACK OFF') #no voltage readback from source unit --> voltage might be off the real value
        self.write(':SENS:CURR:RANG 100E-9') #automatically removes the autorange setup of the instrument

        #set limitation on the current for the voltage source
        self.write('SOURCe:VOLTage:ILIMit 100E-9')

        #do an autozero for the current measurement
        self.write(':SENS:AZERo:ONCE') #do an autozero before the measurement


    def setBias(self, voltage):
        self.write(':SOUR:VOLT %f' % voltage)
        #sleep(1)
        #self.write(':SENS:AZERo:ONCE') #do an autozero before the measurement


    def toggleOutput(self, on=False):
        if on:
            self.write(':OUTPUT ON') 
        else:
            self.write(':OUTPUT OFF') 


    def getCurrent(self):
        data = self._inst.query_ascii_values('READ?') #takes 6ms
        return data



if __name__ == '__main__':
    config = ConfigObj('config.ini')['KeithleyK2470']
    k = KeithleyK2470(config)
    k.write("abort")
    sleep(1)
    k.write("*rst")
    sleep(1)
    k.configure()






