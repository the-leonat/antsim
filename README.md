# antsim

antsim is a multi agent simulation, which tries to emulate the trailfinding behavior of ants, which interact via scent and tactile sensors.

## Usage

Python Simulator.py
 - r (record)
 - rt (time in seconds to record)
 - rs (record every nth step)
 - f (filename)

 - v (view)

## Example
	Python Simulator.py -r -v -rt 60 -rs 5 -rf test.hdf5

	Simulates for 60 seconds, saves every 5th step to file test.hdf5 and shows it afterwards
	
You can also simulate live with the 
 - live 
command. this wont save to a file, but display the simulated data right away. 
