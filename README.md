# NERD CROPPER #

This project uses mathematical functions like `x^2 + 2x + 5`, `sin(x)`, `cos(x)` to generate images using a Simplex Noise function.

# How to run # 

There's a config file in which you should provide number of `lanes` or `columns`. Number of `lanes` should match the number of `functions` used to generate the image.
Look through the config file, tweak it, and see what happens.

# Minimal example of config file #

````{
    "leftEdgeMargin": 15,
    "rightEdgeMargin": 15,
    "lanesNumber": 1,           - number of lanes
    "bandSize": 256,
    "topEdgeMargin": 10,
    "bottomEdgeMargin": 10,
    "laneOffset": 60,
    "xAxisMaxJitter": 40,       - max jitter in pixels. Kernel will walk on the X axis randomly.
    "minPrintOffset": 10,
    "maxPrintOffset": 50,
    "minPrintStrength": 50,
    "maxPrintStrength": 100,
    "bandDefinitions" : [
        {
            "0": ["((x^2)/2) + ((y^2)/2) - 1", "UNDER"]   - [0] -> function definition, [1] => Which portion of space should be filled with simplex noise
        }
    ]
}
````

If you have any questions, open an issue.
