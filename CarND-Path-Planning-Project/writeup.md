# CarND-Path-Planning-Project
Self-Driving Car Engineer Nanodegree Program

## Goals
In this project your goal is to safely navigate around a virtual highway with other traffic that is driving +-10 MPH of the 50 MPH speed limit. You will be provided the car's localization and sensor fusion data, there is also a sparse map list of waypoints around the highway. The car should try to go as close as possible to the 50 MPH speed limit, which means passing slower traffic when possible, note that other cars will try to change lanes too. The car should avoid hitting other cars at all cost as well as driving inside of the marked road lanes at all times, unless going from one lane to another. The car should be able to make one complete loop around the 6946m highway. Since the car is trying to go 50 MPH, it should take a little over 5 minutes to complete 1 loop. Also the car should not experience total acceleration over 10 m/s^2 and jerk that is greater than 10 m/s^3.

## Basic Build Instructions

1. Clone this repo.
2. Make a build directory: `mkdir build && cd build`
3. Compile: `cmake .. && make`
4. Run it: `./path_planning`.

## Dependencies

* cmake >= 3.5
  * All OSes: [click here for installation instructions](https://cmake.org/install/)
* make >= 4.1
  * Linux: make is installed by default on most Linux distros
  * Mac: [install Xcode command line tools to get make](https://developer.apple.com/xcode/features/)
  * Windows: [Click here for installation instructions](http://gnuwin32.sourceforge.net/packages/make.htm)
* gcc/g++ >= 5.4
  * Linux: gcc / g++ is installed by default on most Linux distros
  * Mac: same deal as make - [install Xcode command line tools]((https://developer.apple.com/xcode/features/)
  * Windows: recommend using [MinGW](http://www.mingw.org/)
* [uWebSockets](https://github.com/uWebSockets/uWebSockets)
  * Run either `install-mac.sh` or `install-ubuntu.sh`.
  * If you install from source, checkout to commit `e94b6e1`, i.e.
    ```
    git clone https://github.com/uWebSockets/uWebSockets 
    cd uWebSockets
    git checkout e94b6e1
    ```
## Result
![result](./result.jpg)

The car can run along the lane with out any accident and don't violate any speed, acceleration or jerk limit for more than 20 miles.

The car can change the lane if some slow driving car ahead safely.

## Implementation

### Future path prediction

We have a global variable `lane`, which point to the lane the car is targeting. Also, we have `ref_vel`, which control the speed. With these, we first fist a spline based on 3 sampled points and last 2 points from previous prediction. The the next points are generated and appended to previous prediction until we have 50 points totally.

Spline generation are in line 340 to 387 of main.cpp.
Points generation are in line 392 to 420 of main.cpp.

### Collision avoidance

To avoid collision with other cars, we first use the sensor fusion to get other cars information. Then we predict where that are will be. Finally, we check if our car will be in the safe zone of that car.

If there is a chance to collision, the car will either slow down or change to other lane.

This part of code is in line 272 to 306.

### Lane changing

As described in previous section, we need to change the lane when obstacles ahead. Also, we want to keep in the middle lane if possible.

Thus, we have different plan when the car in different lanes, which can be go left, go right, speed up or speed down.

To control the acceleration and jerk, we control the `acc` variable as constant.

This part is in line 308 to 338.
