from tm1637 import TM1637
import RPi.GPIO as GPIO

import multiprocessing, time


class WorkoutBuddy():
    REST_TIME = 90
    CLK_PIN = 24
    DIO_PIN = 23
    INPUT_PIN = 17
    MAX_SETS = 5
    
    _time = 0
    _set = 1
    _thread = None
    _tm = None
    _gpio = None

    # Debouncing
    _accept_input = True

    def __init__(self):
        # Use board numbering scheme
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
                self.INPUT_PIN,
                GPIO.FALLING, 
                callback=self.set_completed,
                bouncetime=200
        )

        # Write and init display
        self._tm = TM1637(clk=self.CLK_PIN, dio=self.DIO_PIN)
        self._time = self.REST_TIME
        self.display()

    def __str__(self):
        return f"{self._time}, {self._set}"

    def display(self):
        self._tm.numbers(self._time, self._set)


    def set_completed(self, channel):
        if self._thread is not None:
            self._thread.terminate()
        
        # Press button to reset to 1st set
        if self._set == self.MAX_SETS:
            self._set = 1
            self._time = self.REST_TIME
            self.display()
        else:
            self._set += 1
            self.rest_between_sets()
    
    def stop_thread(self):
        self._thread.terminate()

    def rest_between_sets(self):
        self._time = self.REST_TIME
        self._thread = multiprocessing.Process(target=self.countdown_thread)
        self._thread.start()

    def countdown_thread(self):
        self.display()
        while self._time > 0:
            time.sleep(1)
            self._time -= 1
            self.display()
    

if __name__ == "__main__":
    wb = WorkoutBuddy()
    while True:
        pass # Spinlock
