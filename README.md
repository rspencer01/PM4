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

Assets
------
Assets with a project like this are always difficult.  At the moment I am using
some mixamo animations and models.  These are not allowed to be distributed
freely.  However, they can be downloaded for free from the [mixamo](mixamo.com)
webpage.

I understand that this is crummy if you want to download and play this.  I am
thus working on having a downloadable binary which will allow distribution of
the assets in an embedded form.  Drop me an email if you want a copy.
