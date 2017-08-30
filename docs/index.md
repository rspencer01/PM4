## Welcome to Project Magrathea

Project Magrathea is an attempt to make a large, explorable world, procedurally populated with enough things to make it believable.  Currently the world is 64 kilometers on a side and has mountains, trees, villages, roads and people wandering around.

This is an open-ended project, but it is already quite advanced.

Have a look at some of the [screenshots](screenshots.html).

<div>
<a href="screenshots.html">
  <img style="width:49%;" src="static/screenshot1.jpg">
  <img style="width:49%;" src="static/screenshot2.jpg">
</a>
</div>
<p></p>

## Running the software

You will require
 * `git lfs`
 * `pyopengl`
 * `tqdm`
 * `pyassimp` (a recent version, probably compiled from source)

Apart from that, installation should be as simple as
~~~ bash
$ git clone https://github.com/rspencer01/PM4.git
$ cd PM4
$ ./PM4
~~~
The first time you run Project Magrathea, it will take a while (about 10 minutes) to construct all the assets it requires and may run slowly.  However, each time after that it should be very quick to start and run smoothly.

## Helping out

I'd love to have some help with this project.  Its been a labor of love for over four years (in various forms) for me.  [See how you can help.](help.html)

## Notes and articles

These aren't quite blog posts, as they aren't regular, but are interesting things I've come across in the course of the project

 * ### [Git LFS Woes](lfs-woes.html)
 * ### [Bumpy Grass](grass-bump.html)
 * ### [Writing an Engine](engine.html)
