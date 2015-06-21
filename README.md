# antsim

antsim is a multi agent simulation, which tries to emulate the trailfinding behavior of ants, which interact via scent and tactile sensors.

## Usage

Python Simulator.py
 - r (record)
 - rt (time in seconds to record)
 - rs (record every nth step)
 - f (filename)

 - v (view)
 - live (simulates in live mode, without saving to a file)

## Example
	Python Simulator.py -r -v -rt 60 -rs 5 -f test.hdf5

	Simulates for 60 seconds, saves every 5th step to file test.hdf5 and does show it afterwards
