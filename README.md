# Python-simulation-of-record-breaking-MItsubishi-FTO-EV-run.
I developed a program that simulates the record-breaking MItsubishi FTO-EV run with its work and calculations. But by changing a few parameters in this program, you can look at the results of any trip simulation, taking into account speed, acceleration, number of stops, and total travel time.

To change the arrival time or charging parameters of the car, change the corresponding data in the: Arrival characteristics section.
To change the characteristics of the car, change the data in the: Characteristics of the car section.

Comments — #---hidden for the finale
    these parts of the code are hidden for the final version of the program
    can be opened to see how interval calculations work.
    To calculate an unknown acceleration time (for example, the acceleration time to 130 km/h when you know the acceleration to 100 km/h):
      you need to open (#---hidden for the finale) in the calc_non_uniform_accel_distance function, set the known acceleration of the car to 100 km/h in Characteristics of the car section, and then do the acceleration       calculations according to the instructions (if the car 0-100 in 12.5 seconds then to 130 in approximately 20.495 seconds (Lancer 1.6: 0-100 = 12.5, 0-130 = 20.5)).
      Instructions to do this calc:
        1- Run the program
        2- Take the last segment of acceleration to 100 and count how many times it will reach the required speed and multiply by a time slightly greater than the time of the same segment
          For example, the acceleration of the last segment was as follows:
                        Interval 50 (t=0.39 seconds):
                          V: 27.22 -> 27.78 m/s | a: 1.42 m/s² | s: 10.78 m
                          V: 98.00 -> 100.00 km/h | - here the speed increase is 2 km/h
              1 - Take the time t=0.39 s, increase it by 30%, to 0.533 s (number of % = speed difference you need to calc)
              2 - Find out how many such segments will fit in the acceleration to the desired speed (here 15)
                  (130 - 100) / 2 = 15 (this is the figure of the speed increase for one segment of the calculation)
              3 - 15 * 0.533 = 7.995 seconds
              4 - then add this acceleration to the acceleration to 100 km/h 12.5 + 7.995 = 20.5 s
