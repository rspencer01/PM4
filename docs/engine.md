## Writing an Engine

A few months ago I decided to give up on my self-delusion and just admit that I am writing an engine.

Yes, PM4 is about the procedural generation and rendering of the terrain, but I found that more and more I needed to focus on the "how" of the rendering, rather than the "what" of the procedural stuff.  This is sad, because procedural generation is the [really cool bit](https://vimeo.com/228391688).

But it does have some up sides.  As a learning curve, its been great to solidify my knowledge of how graphics programming works and what is necessary to build games quickly.  I haven't used many game engines before (a little playing around with Unity really), so its been fun to define my own way.

It also means that I have gotten nice and close to the metal.  Its enabled me to do some interesting things like transform feedback and tesselation, which I am not certain are available easily in other engines.

I am thus going to split Project Magrathea in two.  One part will be the "game" and the other the engine, which I will call "Dent".  I have already done a proof-of-concept on this by making [pong](https://github.com/rspencer01/pong) and (model_viewer)[https://github.com/rspencer01/model-viewer] using the engine parts of the codebase.  In fact, the model viewer is mostly a stub game, designed to test and enable development of the asset loader.

I am going to try to make the interface to Dent as neat as possible so that it is very easy to get up and started with it.  Here is an overview of what I'd like games to look like.  All of these are currently working to some extent.

 * Games will import python package `dent`.
 * Games will define `Scenes` which each have control over a `RenderPipeline` which will probably target the screen.
 * Rendering shaders will be defined by the game (although the engine should define some basic ones).
 * The game elements will interact with eachother through the `messaging` system.  This allows game replays (handled by `dent`).

This is a good enough start.  As I develop other projects with Dent, and continue to work on PM4, I'm sure the design will change.  In addition, eventually some parts of the system will have to be written in c++ or something to improve speed.

I haven't yet separated it out into a separate project.  Once I have extracted Dent code from PM4 code, I'll make a repository.  Stay tuned!
