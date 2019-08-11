# MattFlow

A CFD python package for the shallow water equations.

MattFlow simulates the surface of the water after any initial conditions, such as drops or stones falling on.

<img src="https://media.giphy.com/media/jpVKPxzBiGoSvNYUrY/giphy.gif" width="265" height="150" /> <img src="https://media.giphy.com/media/VJNqBY7uKP3r0AvCcp/giphy.gif" width="265" height="150" /> <img src="https://media.giphy.com/media/QxYpANpE5snKSrdLJ5/giphy.gif" width="265" height="150" />

___

| requirements      | os        |
| ----------------  | --------- |
| python 3          | GNU/Linux |
| numpy 1.16.4      | Windows   |
| matplotlib 3.1.1  |           |
| ffmpeg (optional) |           |

## How to install & run MattFlow

1. anaconda environment (recomended)

```bash
$ mkdir mattflow
$ cd mattflow
$ conda create --name mattflow python=3 matplotlib
$ conda activate mattflow
$ pip install mattflow
$ mattflow
```

2. venv (python>=3.3)  

```bash
$ mkdir mattflow
$ cd mattflow
$ python3 -m venv mattflow_env
$ source mattflow_env/bin/activate
$ pip install mattflow
$ mattflow
```

3. pip

```bash
$ mkdir mattflow
$ cd mattflow
$ pip install --user mattflow
$ mattflow
```


## Swallow Water Equations

SWE is a simpified CFD problem which models the surface of the water, with the assumption  
that the horizontal length scale is much greater than the vertical length scale.  

SWE is a coupled system of 3 hyperbolic partial deferential equations, that derive from  
conservation of mass and conservation of linear momentum (Navier-Stokes) equations, in  
case of a horizontal stream bed, with no Coriolis, frictional or viscours forces ([wiki]).

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/9b9d481407c0c835525291740de8d1c446265ce2" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -18ex; width:46ex; height:19ex;" alt="{\displaystyle {\begin{aligned}{\frac {\partial (\rho \eta )}{\partial t}}&amp;+{\frac {\partial (\rho \eta u)}{\partial x}}+{\frac {\partial (\rho \eta v)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta u)}{\partial t}}&amp;+{\frac {\partial }{\partial x}}\left(\rho \eta u^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)+{\frac {\partial (\rho \eta uv)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta v)}{\partial t}}&amp;+{\frac {\partial (\rho \eta uv)}{\partial x}}+{\frac {\partial }{\partial y}}\left(\rho \eta v^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)=0.\end{aligned}}}">

where:  
_η_ : height  
_u_ : velocity along the x axis  
_υ_ : velocity along the y axis  
_ρ_ : density  
_g_ : gravity acceleration


## MattFlow structure
&emsp;**More details at this [jupyter notebook]**

0. configuration of the simulation via a config file
1. pre-process  
structured/cartesian mesh
2. solution  
   supported solvers:  
   - [Lax-Friedrichs] Reiman
   &nbsp;&nbsp;                | O(Δt, Δx<sup>2</sup>, Δy<sup>2</sup>)  
   - 2-stage [Rugne-Kutta]
   &nbsp; &nbsp; &nbsp;        | O(Δt<sup>2</sup>, Δx<sup>2</sup>, Δy<sup>2</sup>)
   &ensp;| default  
   - [MacCormack]
   &emsp; &emsp; &emsp; &emsp; | O(Δt<sup>2</sup>, Δx<sup>2</sup>, Δy<sup>2</sup>)
   &ensp;| experimental
3. post-processing  
   matplotlib animation

## Additional configurations

- mesh sizing
- domain sizing
- initial conditions (single drop, multiple drops, rain)
- boundary conditions (currently: reflective)
- solver
- plotting style
- animation options

Currently, you can configure the simulation at the _config_ module  

## TODO

1. exceptions
2. pytest
3. linting
4. Simple API to configure the simulation
5. Implementation of higher order schemes
6. Addition of source terms
7. Addition of viscous models
8. Moving core to C++, Cython or Numba
9. Support moving objects inside the domain
10. Unstructured mesh
11. Extent to 3D CFD

***Start the flow!***

>(C) 2019, Thanasis Mattas  
>atmattas@physics.auth.gr


[//]: # "links"

[wiki]: <https://en.wikipedia.org/wiki/Shallow_water_equations>
[Lax-Friedrichs]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Friedrichs_method>
[Rugne-Kutta]: <https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods>
[Lax-Wendroff]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Wendroff_method>
[MacCormack]: <https://en.wikipedia.org/wiki/MacCormack_method>
[jupyter notebook]: <https://colab.research.google.com/github/ThanasisMattas/mattflow/blob/master/notebooks/mattflow_notebook.ipynb#scrollTo=sqSJYpEwmJN3>
