"""
  —————— Calculation program: ——————
  distance traveled and number of stops, based on arrival time and speed, taking into account:
    acceleration information, driving speed, braking information,
    number of vehicle charges, charging time intervals and driving time
"""

# ————————— DATA THAT NEEDS TO BE CHANGED ACCORDING TO YOUR CALCULATION —————————

# --- Arrival characteristics ---
overall_race_time = 1440 # total arrival time for calculation
charge_time = 22 # single charge time
ride_time = 50 # driving time between charges

# --- Characteristics of the car ---
car_weight_kg = 1100 # car weight
brake_type = 'Econom' # types of braking: 'Racing', 'Sport', 'Standart', 'Econom'
V_final_kmh = 130 # car speed
T_to_avg_speed = 30 # acceleration time to V_final_km

# —————————        END OF DATA FOR CALCULATIONS        —————————


# accuracy of acceleration and braking calculations
N_accel_intervals = 50 # intervals for calculating simulated non-constant acceleration
N_brake_intervals = 50 # intervals for calculating simulated non-constant braking

speed_2 = (V_final_kmh / 3.6) # speed in m/s

# --- BRAKE MODEL COEFFICIENTS (для 140-0 kph) ---
# reliable coefficients for calc_braking_in_phases()
MODELS_120_FINAL = {
  "Racing": {"M": 0.009112, "B": 28.571, "V_base": 140},
  "Sport": {"M": 0.009902, "B": 35.511, "V_base": 140},
  "Standart": {"M": 0.010586, "B": 46.975, "V_base": 140},
  "Econom": {"M": 0.031586, "B": 75.975, "V_base": 120}
}

# ------------------------------------------------------------------------
# calculation of the total distance traveled per acceleration
def calc_non_uniform_accel_distance(V_final_kmh, T_total_sec, N_accel_intervals):
  """
    Calculates the total distance traveled per acceleration, dividing the motion into N intervals.
    The acceleration in each interval is assumed to be uniform.
    The time of the intervals increases from smaller to larger (arithmetic progression).
  """
  # 1. Converting terminal velocity to m/s
  V_final_mps = V_final_kmh / 3.6

  # 2. Calculation of the coefficient for time intervals (sum of arithmetic progression)
  # Progression amount: T = c * (1 + 2 + ... + N) = c * N * (N + 1) / 2
  # From here: c = 2 * T / (N * (N + 1))
  sum_of_weights = N_accel_intervals * (N_accel_intervals + 1) / 2
  c_time_factor = (2 * T_total_sec) / (N_accel_intervals * (N_accel_intervals + 1))
  
  # 3. Dividing the total time into N increasing intervals
  time_intervals = [c_time_factor * i for i in range(1, N_accel_intervals + 1)]
  
  # 4. Distribution of the final velocity into N intervals (uniform increment)
  # V_final = V_interval_1 + V_interval_2 + ... + V_interval_N
  V_step = V_final_mps / N_accel_intervals
  
  # Initialization
  total_distance_one_accel = 0.0
  V_start_of_interval = 0.0
  
  print(f"\n--- Acceleration to {V_final_kmh} km/h ---")
  print(f"Final speed in kilometers per hour:      {V_final_kmh} km/h ({V_final_mps:.2f} m/s)")
  print(f"Acceleration time:                       {T_total_sec:.2f} s")
  #print(f"Interval (how much time is spent on part of the acceleration)") #---hidden for the finale
  #print(f" Initial V -> Reached V | Acceleration Delta | Distance Traveled \n") #---hidden for the finale

  # 5. Iterate over each interval
  for i in range(N_accel_intervals):
    t_i = time_intervals[i]
    V_end_of_interval = V_start_of_interval + V_step

    # Acceleration calculation (a = dV / dt) for the current interval
    acceleration_i = V_step / t_i
    
    # Distance calculation (s = V_start * t + 0.5 * a * t^2)
    distance_i = (V_start_of_interval * t_i) + (0.5 * acceleration_i * t_i**2)
    
    total_distance_one_accel += distance_i

    #print(f"Interval {i+1} (t={t_i:.2f} с):") #---hidden for the finale
    #print(f"  V: {V_start_of_interval:.2f} -> {V_end_of_interval:.2f} m/s    | a: {acceleration_i:.2f} m/s² | s: {distance_i:.2f} м") #---hidden for the finale
    #print(f"  V: {V_start_of_interval * 3.6:.2f} -> {V_end_of_interval * 3.6:.2f} km/h |") #---hidden for the finale

    # Updating the initial speed for the next interval
    V_start_of_interval = V_end_of_interval
      
  print(f"Distance traveled during acceleration:   {total_distance_one_accel:.2f} meters.")
  print("")
  print("-------------------------------------------------------------------------------")
  
  return total_distance_one_accel


# ------------------------------------------------------------------------
# calculation of braking distance and time
def calc_braking_in_phases(V_final_kmh, car_weight_kg, brake_type, N_brake_intervals=10):
  """
    Calculates braking distance and time, breaking the movement into N phases with modified deceleration.
      :param V_final_kmh: Initial braking speed (km/h).
      :param car_weight_kg: Car weight (kg).
      :param brake_type: 'Racing' or 'Sport' or 'Standart'.
      :param N_brake_intervals: Number of speed intervals.
      :return: (Total_distance_m, Total_time_s)
  """

  # 1. Preliminary calculations and forecasting j_ust
  V_start_mps = V_final_kmh / 3.6
  
  # We use the previous function to get the base j_ust (average)
  model = MODELS_120_FINAL[brake_type]
  M, B, V_base = model['M'], model['B'], model['V_base']
  S_base_120 = M * car_weight_kg + B
  S_total_predicted = S_base_120 * (V_final_kmh / V_base)**2
  
  # We calculate the AVERAGE (target) deceleration to maintain the accuracy of S_total
  # j_avg = V^2 / (2S)
  j_avg = (V_start_mps**2) / (2 * S_total_predicted) 
  
  # 2. Breaking the speed into N steps
  V_step = V_start_mps / N_brake_intervals
  
  # Initialization
  total_brake_distance = 0.0
  total_brake_time = 0.0
  V_start_of_interval_mps = V_start_mps
  
  # Header output
  if brake_type == "Econom":
    print("\n--- Smooth braking (economical) ---")
  else:
    print(f"\n--- Braking (type of brake system: '{brake_type}') ---")
    
  print(f"Initial braking speed:                   {V_final_kmh} km/h ({V_start_mps:.2f} m/s)")
  print(f"Vehicle weight:                          {car_weight_kg} kg")
  print(f"Average deceleration:                    {j_avg:.2f} m/s²") # j_avg
  
  # 3. Iterate over each interval
  for i in range(N_brake_intervals):
    
    # V_end_of_interval
    V_end_of_interval_mps = V_start_of_interval_mps - V_step
    
    # V_mid_kmh - average interval speed (for modifier)
    V_mid_kmh = ((V_start_of_interval_mps + V_end_of_interval_mps) / 2) * 3.6

    # 4. Deceleration modification (j_i) for unevenness
    """
      Create a modifier that INCREASES j at low speed.
      Modifier: (N - i) + 1. At the beginning (i=0): 10. At the end (i=9): 1.
      This is the logic you wanted: the most deceleration at low V.
      BUT this will break with j_avg.
      Alternative modifier (more realistic: j = j_avg * k_i)
      For example, let's make the deceleration proportional to the inverse square of the speed
    """

    # j_factor: від 0.5 (on high V) до 1.5 (on low V).
    #j_factor = 0.5 + (1.0 * (N_brake_intervals - 1 - i) / (N_brake_intervals - 1)) 
    j_factor = 0.5 + (1.0 * i / (N_brake_intervals - 1))

    # We use linear dependence (j_i = j_avg * k_i)
    j_i = j_avg * j_factor
    
    # 5. Calculating time (T_i) and distance (S_i) for an interval
    
    # T = dV / j
    T_i = V_step / j_i
    
    # S = V_avg * T
    V_avg_mps = (V_start_of_interval_mps + V_end_of_interval_mps) / 2
    distance_i = V_avg_mps * T_i
    
    total_brake_distance += distance_i
    total_brake_time += T_i

    # Output step
    #print(f"Interval {i+1}: V_mid: {V_mid_kmh:.2f} km/h") #---hidden for the finale
    #print(f"  V: {V_start_of_interval_mps * 3.6:.2f} -> {V_end_of_interval_mps * 3.6:.2f} km/h | j_i: {-j_i:.2f} m/s² | T_i: {T_i:.2f} s | S_i: {distance_i:.2f} m") #---hidden for the finale

    # Updating the initial speed for the next interval
    V_start_of_interval_mps = V_end_of_interval_mps

  """
    Final correction: The coefficient j_factor artificially changes S_total.
    We adjust the path and time to the target values S_total_predicted and T_total_base

    T_total_base = S_total_predicted / (V_start_mps / 2)
    Correction factor for time
  """

  print(f"Total Braking Distance:                  {total_brake_distance:.2f} meters.")
  print(f"Total Braking Time:                      {total_brake_time:.2f} sec.")
  #print(f"Forecast S_total from the M*W+B model: {S_total_predicted:.2f} meters.") #---hidden for the finale
  print("-------------------------------------------------------------------------------")
  
  return total_brake_distance, total_brake_time

# function for rounding down
def rounding_func(value):
  return int(value)

# ------------------------------------------------------------------------
# calculating basic time data for car charging
def calc_timing(charge_time, ride_time, overall_race_time):
  """
    Calculates the time interval at which the car starts charging and when it starts again
    Calculates the number of charges for the measurement time interval (for example, 24 hours - 1440 minutes)
    Calculates the total time spent charging the car
  """
  recharge_qty = 0
  time_overall = 0
  stop_time = 0
  
  def func_stopping(time):
    return time + ride_time

  # try calculation (main function body)
  try:
    #print("--- Start of calculations ... --- \n") #---hidden for the finale
    while time_overall <= overall_race_time: # cycle up to 1440 minutes (24 h)

      recharge_qty += 1 # recharge counter
      stop_time = time_overall # calculating the time of each stop (start. 0 + 70)
      time_overall = time_overall + ride_time + charge_time # cycle counter (start. 0 + 50 + 20)
      
      recharge_hours_to_overall = (time_overall - charge_time) // 60 # calculating time in hours (start. 70 - 50 // 60 = 0 h)
      recharge_mins_to_overall = (time_overall - charge_time) % 60 # calculating time in min - remaining hours (start. 70 - 50 % 60 = 50 min)
      
      if time_overall > overall_race_time: # prevent recalculation beyond the selected time limit
        pass

      #elif time_overall == overall_race_time: #--- block hidden for final
        #if recharge_qty == 1: # if it is the first time charging then the end of recharge ('E)
          #print(f"Stop after {ride_time} minutes of riding, for {charge_time} minutes of charging.")
            # here are just two constants from the condition
          #print(f"Stopping for {func_stopping(stop_time)} minutes ({recharge_hours_to_overall} hour {recharge_mins_to_overall} min) of the total arrival.")
            # start. {func_stopping(stop_time)} - {func_stopping(0)} - вертає 0 + ride_time
          #print(f"We have {recharge_qty} charge left in {time_overall} minutes and continue moving.\n")
            # shows the calculated time time_overall (start. 0 + ride_time + charge_time) and recharge_qty (поч. 0 + 1)

        #else: # if NOT the first time charging then the end of recharges ('ES)
          #print(f"Stop after {ride_time} minutes of riding, for {charge_time} minutes of charging.") # here are just two constants from the condition
          #print(f"Stopping for {func_stopping(stop_time)} minutes ({recharge_hours_to_overall} hour {recharge_mins_to_overall} min) of the total arrival.")
          #print(f"At {time_overall} min we have charging: {recharge_qty}.\n")

      #else: # if not outside the selected time then this block #--- block hidden for final
        #if recharge_qty == 1: # if it is the first time charging then the end of recharge ('E)
          #print(f"Stop after {ride_time} minutes of riding, for {charge_time} minutes of charging.")
            # here are just two constants from the condition
          #print(f"Stopping for {func_stopping(stop_time)} minutes ({recharge_hours_to_overall} hour {recharge_mins_to_overall} min) of the total arrival.")
            # start. {func_stopping(stop_time)} - {func_stopping(0)} - returns - 0 + ride_time
          #print(f"We have {recharge_qty} charge left for {time_overall} minutes and we continue moving.\n")
            # shows the calculated time time_overall (start. 0 + ride_time + charge_time) і recharge_qty (поч. 0 + 1)

        #else: # if NOT the first time charging then end of recharges ('ES)
          #print(f"Stop after {ride_time} minutes of riding, for {charge_time} minutes of charging.") # here are just two constants from the condition
          #print(f"Stopping at {func_stopping(stop_time)} minutes ({recharge_hours_to_overall} hour {recharge_mins_to_overall} min) of the total arrival.")
          #print(f"In {time_overall} min we have charging: {recharge_qty}, and we continue moving.\n")

  except Exception as e: # catch a bug
    print(f"❌ **Error** cycle: {e} ❌")
    return type(e)

  else: # when all is done
    #print("--- Calculation completed! ---") #---hidden for the finale
    print(f"\n--- Time Calculations for arrival length: {overall_race_time} min. ---")

  finally: # final message
    last_stop_on = func_stopping(stop_time) - ride_time - charge_time

    recharge_hours_to_overall = ((recharge_qty - 1) * charge_time) // 60
    # time // 60 will give the number of hours (*20 is the charging time, can be in the form of a variable)
    recharge_mins_to_overall = ((recharge_qty - 1) * charge_time) % 60
    # time % 60 will give the number of minutes (*20 is the charging time, can be in the form of a variable)
    recharge_mins = (recharge_qty - 1) * charge_time

    racing_hours_to_overall = (overall_race_time - ((recharge_qty - 1) * charge_time)) // 60
    racing_mins_to_overall = (overall_race_time - ((recharge_qty - 1) * charge_time)) % 60
    racing_mins = (overall_race_time - ((recharge_qty - 1) * charge_time))

    last_charge = time_overall - ride_time - charge_time

    if charge_time % 1 != 0:
      print(f"When stopping after every {ride_time} minutes of driving, on {rounding_func(charge_time):.0f} min {(charge_time % 1) * 60:.0f} s charging, we have:") # тут просто дві сталі з умови
    else:
      print(f"When stopping after every {ride_time} minutes of driving, on {charge_time} min charging, we have:")

    if last_stop_on % 1 != 0: # all the same conditions - for the correct display of the remainder of the minutes
      print(f"The final stop for charging will be at {rounding_func(last_stop_on):.0f} min {(last_stop_on % 1) * 60:.0f} с ({last_stop_on // 60:.0f} hour {last_stop_on % 60:.0f} min {(last_stop_on % 1) * 60:.0f} s) of the total arrival.")
    else:
      print(f"The final stop for charging will be at {last_stop_on} min ({last_stop_on // 60} hour {last_stop_on % 60} min) of the total arrival.")

    if last_charge % 1 != 0:
      print(f"On {rounding_func(last_charge):.0f} min {(last_charge % 1) * 60:.0f} s we have charging: {recharge_qty - 1}.\n")
    else:
      print(f"On {last_charge} min we have charging: {recharge_qty - 1}.\n")

    print(f"In {overall_race_time} min of arrival ({overall_race_time // 60} hour {overall_race_time % 60} min) we recharged {recharge_qty - 1} times.")

    if recharge_mins % 1 != 0:
      print(f"Total time spent on recharging:          {rounding_func(recharge_mins):.0f} min {(recharge_mins % 1) * 60:.0f} s ({recharge_hours_to_overall:.0f} hour {recharge_mins_to_overall:.0f} min {(recharge_mins % 1) * 60:.0f} s).")
    else:
      print(f"Total time spent on recharging:          {rounding_func(recharge_mins):.0f} min ({recharge_hours_to_overall:.0f} hour {recharge_mins_to_overall:.0f} min).")

    if racing_mins % 1 != 0:
      print(f"Total driving time:                      {rounding_func(racing_mins):.0f} min {(racing_mins % 1) * 60:.0f} s ({racing_hours_to_overall:.0f} hour {racing_mins_to_overall:.0f} min {(racing_mins_to_overall % 1) * 60:.0f} s).")
    else:
      print(f"Total driving time:                      {rounding_func(racing_mins):.0f} min ({racing_hours_to_overall:.0f} hour {racing_mins_to_overall:.0f} min).")
    print("")

  print("-------------------------------------------------------------------------------")
  
  return recharge_qty, recharge_hours_to_overall, recharge_mins_to_overall, recharge_mins, racing_hours_to_overall, racing_mins_to_overall, racing_mins


# ------------------------------------------------------------------------
# calculating all distances based on speed in m/s, time constants, and data from other functions
def calc_distance(racing_mins, recharge_qty, total_distance_one_accel, speed_2, overall_race_time, T_to_avg_speed):
    """
    function to calculate all distances based on m/s and converted to km/h based on:
    distance traveled on the road at a given speed for the time on the road from the function
    calc_timing(racing_mins) subtract the distance for the time of all accelerations
    calculate the distance traveled for all accelerations from calc_timing(recharge_qty)
    already has calc_non_uniform_accel_distance(total_distance_one_accel)
    recharge_qty - here it is considered as the number of starts from a standstill
    """

    in_sec_overall_race_time = overall_race_time * 60 # Total arrival time in seconds
    in_sec_overall_racing_time = racing_mins * 60 # Total driving time in seconds
    in_sec_overall_accel_time = recharge_qty * T_to_avg_speed # Time in seconds spent on all accelerations
    in_sec_overall_braking_time = (recharge_qty-1) * total_brake_time # Time in seconds spent on all braking
    in_sec_overall_move_time = (racing_mins * 60) - in_sec_overall_accel_time - in_sec_overall_braking_time # Total travel time excluding accelerations
    total_overall_distance_accel = total_distance_one_accel * recharge_qty # Total distance of all accelerations including the first start
    total_overall_distance_braking = total_brake_distance * (recharge_qty-1)  # Total distance of all braking
    total_overall_distance_const_speed = speed_2 * (in_sec_overall_racing_time - in_sec_overall_accel_time - in_sec_overall_braking_time)  # Total distance covered for the entire race with constant V
    total_overall_distance = total_overall_distance_const_speed + total_overall_distance_accel + total_overall_distance_braking  # Total distance covered for the entire race, taking into account accelerations

    print(f"\n--- Main calculations ---")
    print(f"Check-in Time:_____________________________________________ {in_sec_overall_race_time / 60:.2f} min ({in_sec_overall_race_time} s).")
    print(f"Time for all accelerations:________________________________ {in_sec_overall_accel_time // 60:.0f} min {in_sec_overall_accel_time % 60:.0f} s ({in_sec_overall_accel_time:.0f} s).")
    
    # check to prevent incorrect display (0 min 60 sec) when time = 60 sec
    if (in_sec_overall_braking_time / 60) != 1:
      print(f"Time for all braking:______________________________________ {in_sec_overall_braking_time // 59.8:.0f} min {in_sec_overall_braking_time % 59.8:.0f} s ({in_sec_overall_braking_time:.0f} с).")
    else:
      print(f"Time for all braking:_____________________________________ {in_sec_overall_braking_time // 60:.0f} min {in_sec_overall_braking_time % 60:.0f} s ({in_sec_overall_braking_time:.0f} s).")

    print(f"Travel time:_______________________________________________ {in_sec_overall_racing_time / 60:.0f} min {in_sec_overall_racing_time % 60:.0f} s ({in_sec_overall_racing_time:.0f} s).")
    print(f"Travel time per arrival with constant V:___________________ {in_sec_overall_move_time / 60:.0f} min {in_sec_overall_move_time % 60:.0f} s ({in_sec_overall_move_time:.0f} s).")
    print(f"Distance of all accelerations:_____________________________ {total_overall_distance_accel / 1000:.2f} km ({total_overall_distance_accel:.0f} m).")
    print(f"All braking distances:_____________________________________ {total_overall_distance_braking / 1000:.2f} km ({total_overall_distance_braking:.0f} m).")

    print(f"Distance traveled per race with constant V:________________ {total_overall_distance_const_speed / 1000:.2f} km ({total_overall_distance_const_speed:.0f} m).")
    print(f"Total distance covered for the entire race:________________ {total_overall_distance / 1000:.2f} km ({total_overall_distance:.0f} m).\n")
    
    print("-------------------------------------------------------------------------------")


# Starting calculation of total arrival time and charging time
result_calc_timing = calc_timing(
    charge_time,
    ride_time,
    overall_race_time
)

# Starting the distance calculation for car acceleration
result_calc_accel_distance = calc_non_uniform_accel_distance(
  V_final_kmh,
  T_to_avg_speed,
  N_accel_intervals
)

# Starting the calculation of the car's braking distance
result_calc_braking = calc_braking_in_phases(
  V_final_kmh, 
  car_weight_kg, 
  brake_type,
  N_brake_intervals
)


recharge_qty = result_calc_timing[0]
recharge_hours_to_overall = result_calc_timing[1]
recharge_mins_to_overall = result_calc_timing[2]
recharge_mins = result_calc_timing[3]
racing_hours_to_overall = result_calc_timing[4]
racing_mins_to_overall = result_calc_timing[5]
racing_mins = result_calc_timing[6]

total_brake_distance = result_calc_braking[0]
total_brake_time = result_calc_braking[1]

total_distance_one_accel = result_calc_accel_distance

print(f"\n--- Interim data ---")
print(f"Number of points with zero car speed:  {recharge_qty}")
if racing_mins % 1 != 0:
  print(f"Total driving time:                      {rounding_func(racing_mins):.0f} min {(racing_mins % 1) * 60:.0f} s ({racing_hours_to_overall:.0f} hour {racing_mins_to_overall:.0f} min {(racing_mins_to_overall % 1) * 60:.0f} s ).")
else:
  print(f"Total driving time:                      {rounding_func(racing_mins):.0f} min ({racing_hours_to_overall:.0f} hour {racing_mins_to_overall:.0f} min).")
print(f"Distance per acceleration:               {total_distance_one_accel:.2f} meters.")
print("")
print("-------------------------------------------------------------------------------")

result_distance = calc_distance(
  racing_mins,
  recharge_qty,
  total_distance_one_accel,
  speed_2,
  overall_race_time,
  T_to_avg_speed
)

"""
Comments — #---hidden for the finale
    these parts of the code are hidden for the final version of the program
    can be opened to see how interval calculations work.
    To calculate an unknown acceleration time (for example, the acceleration time to 130 km/h when you know the acceleration to 100 km/h):
      you need to open (#---hidden for the finale) in the calc_non_uniform_accel_distance function
      set the known acceleration of the car to 100 km/h in Characteristics of the car section
      and then do the acceleration calculations according to the instructions
      (if the car 0-100 in 12.5 seconds then to 130 in approximately 20.495 seconds (Lancer 1.6: 0-100 = 12.5, 0-130 = 20.5)).
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
"""

"""
  charge_time = 22 # abnormal time for one charge
                   # (22 vs 23.1666 - anomaly if overall_race_T=1440, ride_T=50, kg=1100, kmh=130, T_to_avg = 30)
"""
