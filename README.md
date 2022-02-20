# veff

Python video processing pipeline and library.

Took inspiration from Webpack

## Todo
 - Change the config file to be a python file instead of a JSON document, to give the user more control over the options they pass.
 - Rolling video loading. At the moment we load an entire video into memory which uses up a ridiculous amount of memory. Instead we should load and process the input video in batches.

## Effect ideas

This is a work in progress repo at the moment, so here are some ideas for new effects I could write.

### High and low pass filters
Passing in a lower and/or upper thresholds for pixels to be changed.
They could be zero'd out, changed according to an equation or through a function.

### Interpolation
Interpolating between frames, inserting a new one inbetween each frame which steps the pixel values from frame 1 to frame 2 by adding half the difference between the two frames to the first frame. This would simulate slow motion.
