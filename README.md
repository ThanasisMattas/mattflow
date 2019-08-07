# mattFlow

mattFlow is a CFD python package for the shallow water equations.  
It simulates drops or stones falling on the surface of the water.
___


| requirements      | os        |
| ----------------  | --------- |
| python 3          | GNU/Linux |
| numpy 1.16.4      | Windows   |
| matplotlib 3.1.1  |           |
| ffmpeg (optional) |           |


## How to run mattFlow

The required steps to run a simulation are gathered in the script ```mattFlow.py```


1. simple download

```bash
$ mkdir <dir_name>
$ cd <dir_name>
clone/downlad the mattFlow repository
$ python mattFlow.py
```

2. anaconda environment

```bash
$ conda create --name mattFlow numpy matplotlib
$ conda activate mattFlow
$ mkdir <dir_name>
$ cd <dir_name>
clone/downlad the mattFlow repository
$ python mattFlow.py
```


## Swallow Water Equations

SWE is a simpified CFD problem which models the surface of the water, with the  
assumption that the horizontal length scale is much greater than the vertical  
length scale.

SWE is a coupled system of 3 hyperbolic partial deferential equations, that  
derive from conservation of mass and conservation of linear momentum (Navier-  
Stokes) equations, in case of a horizontal steam bed, with no Coriolis, frictional  
or viscours forces ([wiki]).  

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/9b9d481407c0c835525291740de8d1c446265ce2" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -9.671ex; width:49.229ex; height:20.509ex;" alt="{\displaystyle {\begin{aligned}{\frac {\partial (\rho \eta )}{\partial t}}&amp;+{\frac {\partial (\rho \eta u)}{\partial x}}+{\frac {\partial (\rho \eta v)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta u)}{\partial t}}&amp;+{\frac {\partial }{\partial x}}\left(\rho \eta u^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)+{\frac {\partial (\rho \eta uv)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta v)}{\partial t}}&amp;+{\frac {\partial (\rho \eta uv)}{\partial x}}+{\frac {\partial }{\partial y}}\left(\rho \eta v^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)=0.\end{aligned}}}">

where:  
_η_ : height  
_u_ : velocity along the x axis  
_υ_ : velocity along the y axis  
_ρ_ : density  
_g_ : gravity acceleration


## mattFlow structure

0. configuration of the simulation via a config file
1. pre-process  
structured/cartesian mesh
2. solution  
   supported solvers:  
   - [Lax-Friedrichs] Reiman
   &ensp;                     | O(Δt, Δx<sup>2</sup>, Δy<sup>2</sup>)  
   - 2-stage [Rugne-Kutta]
   &emsp;&nbsp;               | O(Δt<sup>2</sup>, Δx<sup>2</sup>, Δy<sup>2</sup>)
   &ensp;| default  
   - [MacCormack]
   &emsp; &emsp; &emsp; &emsp;| O(Δt<sup>2</sup>, Δx<sup>2</sup>, Δy<sup>2</sup>)  
3. post-processing  
   matplotlib animation


## Additional configurations

- mesh sizing
- domain sizing
- simulation mode (single drop, multiple drops, rain)
- solver
- boundary conditions (currently: reflective)
- plotting style
- animation options

Currently, you can configure the simulation at the config file


## TODO

1. mattFlow exceptions
2. tests
3. Simple API to configure the simulation
4. Implementation of higher order schemes
5. Addition of source terms
6. Addition of viscous models
7. Support moving objects inside the domain
8. Unstructured mesh
9. Extent to 3D CFD


***Start the flow!***

>(C) 2019, Thanasis Mattas  
>atmattas@physics.auth.gr


[//]: # "links"

[wiki]: <https://en.wikipedia.org/wiki/Shallow_water_equations>
[Lax-Friedrichs]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Friedrichs_method>
[Rugne-Kutta]: <https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods>
[Lax-Wendroff]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Wendroff_method>
[MacCormack]: <https://en.wikipedia.org/wiki/MacCormack_method>