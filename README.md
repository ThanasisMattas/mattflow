# MattFlow

A CFD python package for the shallow water equations.

MattFlow simulates the surface of the water after any initial conditions, such as drops or stones falling on.

<img src="https://media.giphy.com/media/jpVKPxzBiGoSvNYUrY/giphy.gif" width="265" height="150" /> <img src="https://media.giphy.com/media/VJNqBY7uKP3r0AvCcp/giphy.gif" width="265" height="150" /> <img src="https://media.giphy.com/media/QxYpANpE5snKSrdLJ5/giphy.gif" width="265" height="150" />

___

| requirements         | os        |
| -------------------- | --------- |
| python3              | GNU/Linux |
| numpy >= 1.19.2      | Windows   |
| matplotlib >= 3.3.2  |           |
| numba >= 0.51.2      |           |
| joblib >= 0.13.2     |           |
| ffmpeg (optional)    |           |

## How to install & run MattFlow

1. anaconda environment (recommended)

```bash
$ conda create --name mattflow python=3 numba
$ conda activate mattflow
$ pip install mattflow
$ mattflow
```

2. venv (python>=3.3)

```bash
$ python3 -m venv mattflow_env
$ source mattflow_env/bin/activate
$ pip install mattflow
$ mattflow
```

3. pip

```bash
$ pip install --user mattflow
$ mattflow
```

## Swallow Water Equations

SWE is a simpified CFD problem which models the surface of the water, with the assumption<br />
that the horizontal length scale is much greater than the vertical length scale.

SWE is a coupled system of 3 hyperbolic partial differential equations, that derive from the<br />
conservation of mass and the conservation of linear momentum (Navier-Stokes) equations, in<br />
case of a horizontal stream bed, with no Coriolis, frictional or viscours forces ([wiki]).

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/9b9d481407c0c835525291740de8d1c446265ce2" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -18ex; width:46ex; height:19ex;" alt="{\displaystyle {\begin{aligned}{\frac {\partial (\rho \eta )}{\partial t}}&amp;+{\frac {\partial (\rho \eta u)}{\partial x}}+{\frac {\partial (\rho \eta v)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta u)}{\partial t}}&amp;+{\frac {\partial }{\partial x}}\left(\rho \eta u^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)+{\frac {\partial (\rho \eta uv)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta v)}{\partial t}}&amp;+{\frac {\partial (\rho \eta uv)}{\partial x}}+{\frac {\partial }{\partial y}}\left(\rho \eta v^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)=0.\end{aligned}}}">

where:<br />
_η_ : height<br />
_u_ : velocity along the x axis<br />
_υ_ : velocity along the y axis<br />
_ρ_ : density<br />
_g_ : gravity acceleration

## MattFlow structure

**More details at this [Colab notebook]**

0. configuration of the simulation via a config file
1. pre-process<br />
structured/cartesian mesh
2. solution<br />
   supported solvers:
   - [Lax-Friedrichs] Riemann
   &nbsp;&nbsp;                | O(Δt, Δx<sup>2</sup>, Δy<sup>2</sup>)
   - 2-stage [Runge-Kutta]
   &nbsp; &nbsp; &nbsp; &nbsp; | O(Δt<sup>2</sup>, Δx<sup>2</sup>, Δy<sup>2</sup>)
   &ensp;| default
   - [MacCormack]
   &emsp; &emsp; &emsp; &emsp; &nbsp; | O(Δt<sup>2</sup>, Δx<sup>2</sup>, Δy<sup>2</sup>)
   &ensp;| experimental
3. post-processing<br />
   matplotlib animation

## Additional configurations

- mesh sizing
- domain sizing
- initial conditions (single drop, multiple drops, rain)
- boundary conditions (currently: reflective)
- solver
- multiprocessing
- plotting style
- animation options

Currently, you can configure the simulation at the _config_ module

## TODO

1. CI
2. API (TUI-GUI)
3. Optimization: Moving core to C++ or Cython, Numba
4. Higher order schemes
5. Addition of source terms
6. Addition of viscous models
7. Algorithm that converts every computational second to a real-time second,
   playing with the fps<br /> at the post-processing timelapse, because each
   iteration uses different time-step (CFL condition)
8. Moving objects inside the domain
9. Unstructured mesh
10. Extent to 3D CFD?

<br />
<br />

Special thanks to [Marios Mitalidis] for the valuable feedback.

<br />

***Start the flow!***

>(C) 2019, Athanasios Mattas<br />
>thanasismatt@gmail.com


[//]: # "links"

[wiki]: <https://en.wikipedia.org/wiki/Shallow_water_equations>
[Lax-Friedrichs]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Friedrichs_method>
[Runge-Kutta]: <https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods>
[Lax-Wendroff]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Wendroff_method>
[MacCormack]: <https://en.wikipedia.org/wiki/MacCormack_method>
[Colab notebook]: <https://colab.research.google.com/github/ThanasisMattas/mattflow/blob/master/notebooks/mattflow_notebook.ipynb#scrollTo=sqSJYpEwmJN3>
[Marios Mitalidis]: <https://github.com/mmitalidis>