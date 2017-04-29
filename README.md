Project Magrathea v4
====================

Past
----

This (as you may tell by the name) is the fourth Project Magrathea.
The first three were written in C++ and experimented with birds, fractal trees,
water and other things.

Present
-------

This edition of PM features

* real world data from near the Cederberg mountains, South Africa
* tesselation shaders for terrain geometry
* software texture paging for ground geometry detail
* a Python codebase

### Wait, what?

Yes, the CPU code is in Python.  This forces me to be a little smarter about
what I do on the CPU versus the GPU.  It also allows hot swapping of modules.

Future
------
This will hopefully soon be merged with _Taverner_ for an actual game experience.

Note
----
We use a custom assimp, available from [here](https://github.com/rspencer01/assimp).
