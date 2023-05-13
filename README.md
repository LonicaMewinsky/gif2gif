# gif2gif
Automatic1111 Stable Diffusion WebUI GIF/APNG/WebP Extension

### gif2gif script extension

The purpose of this script is to accept an animated image as input, process frames as img2img typically would, and recombine them back into an animated image. Intended to provide a fun, fast, animation-to-animation workflow that supports new models and methods such as Controlnet and InstructPix2Pix. Drop in a gif and go.

Supported inputs/output:
- Graphics Interchange Format (GIF)
- Animated Portable Network Graphics (APNG)
- Google lossless image (WebP)

![combined](https://user-images.githubusercontent.com/93007558/224235828-f4d0be70-67da-41fc-b225-558576b4b5d4.gif)

Experimental/WIP similar repos:
- [keyframer](https://github.com/LonicaMewinsky/sd-webui-keyframer) - Multiple images in same latent space. Good for keyframes.
- [frame2frame](https://github.com/LonicaMewinsky/frame2frame) - Handles video files (and gifs).

**Instructions:**
 - For ControlNet support, make sure to enable "Allow other script to control this extension" in settings.
 - img2img batch *count* represents completed animations, not individual images.
 - All images in a single batch will be blended together. May help with consistency between frames.
 - Drop or select file in the script's box; a preview should appear if it is a valid animated image.
 - Inpainting works, but currently limited to one mask applied to all frames equally.
   - Ensure the img2img *Inpaint* tab is selected before pressing a *send to..* button.
   - Blended image may take some time to generate.
 - Results are displayed in output gallery on right side.
 - Optionally blend output images. This will blend batches and ControlNet detectmaps together into one image.
 - [ControlNet](https://github.com/Mikubill/sd-webui-controlnet) extension handling improved:
   - "Target ControlNet models" dropdown added; specifies which models to replace input image with frames.
   - Allows, for example, a static *depth* background while animation feeds *openpose*.

**Tips:**
 - Configure and process the image in img2img (it'll use the first frame) before running the script. Find a good seed!
 - If you add an image into ControlNet image window, it will default to that image for guidance for ALL frames.

**Installation:**
 - Install from the Automatic1111 WebUI extensions list, restart UI or
 - Clone this repo into your Automatic1111 WebUI /extensions folder, restart UI
 
**Changelog:**
- 5/13/23: Made multiple output blending optional.
- 4/25/23: Extended support for APNG and WebP files.
- 4/18/23: Adjusted inpainting functionality to act more predictably with current A1111 release.
- 4/17/23: Pared back rarely-used options to focus on primary functions (made 'old' branch). Improved ControlNet handling.