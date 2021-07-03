# MattFlow

![Conda] ![Build_Status] ![codecov]

<br />

A CFD python package for the Shallow Water Equations

MattFlow simulates the surface of the water after any initial conditions, such as drops or stones falling on.

<img src="https://media.giphy.com/media/jpVKPxzBiGoSvNYUrY/giphy.gif" width="265" height="150" /> <img src="https://media.giphy.com/media/VJNqBY7uKP3r0AvCcp/giphy.gif" width="265" height="150" /> <img src="https://media.giphy.com/media/QxYpANpE5snKSrdLJ5/giphy.gif" width="265" height="150" />

___

| requirements         | os        |
| -------------------- | --------- |
| python3              | GNU/Linux |
| click >= 7.0         | Windows   |
| joblib >= 0.13.2     | OSX       |
| matplotlib >= 3.3.1  |           |
| numba >= 0.51.2      |           |
| numpy >= 1.18.5      |           |
| ffmpeg (optional)    |           |

## Install

```bash
$ conda create --name mattflow -y
$ conda activate mattflow
$ conda install -c mattasa mattflow
```

```bash
$ pip install mattflow
```

## Usage

```bash
$ mattflow [OPTIONS]
```

```text
Options:
  -m, --mode [drop|drops|rain]    [default: drops]
  -d, --drops INTEGER             number of drops to generate  [default: 5]
  -s, --style [water|contour|wireframe]
                                  [default: wireframe]
  --rotation / --no-rotation      rotate the domain  [default: True]
  -b, --basin                     render the fluid basin
  --show / --no-show              [default: True]
  --save
  --format [mp4|gif]              [default: mp4]
  --fps INTEGER                   [default: 18]
  --dpi INTEGER                   [default: 75]
  --fig-height INTEGER            figure height (width is 1.618 * height)
                                  [default: 18]
  --help                          Show this message and exit.
```

## Shallow Water Equations

SWE is a simplified CFD problem which models the surface of the water, with the assumption<br />
that the horizontal length scale is much greater than the vertical length scale.

SWE is a coupled system of 3 hyperbolic partial differential equations, that derive from the<br />
conservation of mass and the conservation of linear momentum (Navier-Stokes) equations, in<br />
case of a horizontal stream bed, with no Coriolis, frictional or viscous forces ([wiki]).

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/9b9d481407c0c835525291740de8d1c446265ce2" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -18ex; width:46ex; height:19ex;" alt="{\displaystyle {\begin{aligned}{\frac {\partial (\rho \eta )}{\partial t}}&amp;+{\frac {\partial (\rho \eta u)}{\partial x}}+{\frac {\partial (\rho \eta v)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta u)}{\partial t}}&amp;+{\frac {\partial }{\partial x}}\left(\rho \eta u^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)+{\frac {\partial (\rho \eta uv)}{\partial y}}=0,\\[3pt]{\frac {\partial (\rho \eta v)}{\partial t}}&amp;+{\frac {\partial (\rho \eta uv)}{\partial x}}+{\frac {\partial }{\partial y}}\left(\rho \eta v^{2}+{\frac {1}{2}}\rho g\eta ^{2}\right)=0.\end{aligned}}}">

where:<br />
_η_ : height<br />
_u_ : velocity along the x axis<br />
_υ_ : velocity along the y axis<br />
_ρ_ : density<br />
_g_ : gravity acceleration

## Structure
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ThanasisMattas/mattflow/blob/master/notebooks/mattflow_notebook.ipynb)

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

## Configuration options

- mesh sizing
- domain sizing
- initial conditions (single drop, multiple drops, rain)
- boundary conditions (currently: reflective)
- solver
- multiprocessing
- plotting style
- animation options

## TODO

1. GUI
2. Cython/C++
3. Higher order schemes
4. Source terms
5. Viscous models
6. Algorithm that converts every computational second to a real-time second,
   modifying the fps at<br />the post-processing animation, because each
   iteration uses different time-step (CFL condition).
7. Moving objects inside the domain
8. 3D


## License

[GNU General Public License v3.0]
<br />
<br />

Special thanks to [Marios Mitalidis] for the valuable feedback.

<br />

***Start the flow!***


>(C) 2019, Athanasios Mattas<br />
>thanasismatt@gmail.com

[//]: # "links"

[Conda]: <https://img.shields.io/conda/v/mattasa/mattflow>
[Build_Status]: <https://travis-ci.com/ThanasisMattas/mattflow.svg?branch=master>
[codecov]: <https://codecov.io/gh/ThanasisMattas/mattflow/branch/master/graph/badge.svg>
[Lincense]: <https://img.shields.io/github/license/ThanasisMattas/mattflow>

[wiki]: <https://en.wikipedia.org/wiki/Shallow_water_equations>
[Lax-Friedrichs]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Friedrichs_method>
[Runge-Kutta]: <https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods>
[Lax-Wendroff]: <https://en.wikipedia.org/wiki/Lax%E2%80%93Wendroff_method>
[MacCormack]: <https://en.wikipedia.org/wiki/MacCormack_method>
[GNU General Public License v3.0]: <https://github.com/ThanasisMattas/mattflow/blob/master/COPYING>
[Marios Mitalidis]: <https://github.com/mmitalidis>