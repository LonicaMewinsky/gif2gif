# gif2gif
Automatic1111 Stable Diffusion WebUI GIF Extension

### gif2gif script extension

The purpose of this script is to accept an animated gif as input, process frames as img2img typically would, and recombine them back into an animated gif. Intended to provide a fun, fast, gif-to-gif workflow that supports new models and methods such as Controlnet and InstructPix2Pix. Drop in a gif and go. Referenced code from prompts_from_file.

![combined](https://user-images.githubusercontent.com/93007558/224235828-f4d0be70-67da-41fc-b225-558576b4b5d4.gif)

Experimental/WIP similar repos:
- [keyframer](https://github.com/LonicaMewinsky/sd-webui-keyframer) - Multiple images in same latent space. Good for keyframes.
- [frame2frame](https://github.com/LonicaMewinsky/frame2frame) - Handles video files (and gifs).

**Instructions:**
 - For ControlNet support, make sure to enable "Allow other script to control this extension" in settings.
 - img2img batch *count* represents completed GIFs, not individual images.
 - All images in a single batch will be blended together. May help with consistency between frames.
 - Drop or select gif in the script's box; a preview should appear if it is a valid animated gif.
 - Inpainting works, but currently limited to one mask applied to all frames equally.
   - Optionally blend all frames together for more predictable inpaint coverage.
 - Adjust desired FPS if needed/wanted. Default slider position is original FPS.
 - Add interpolation frames if wanted. Preview should render.
   - Count of interp frames represent the number of blend steps between keyframes.
   - This is a very simple dynamic interp function; the keyframes are left as-is.
   - When *actual FPS* reaches 50, the maximum, the resultant gif will slow and extend to accomodate interp.
 - Results are dropped into outputs/img2img/gif2gif, and displayed in output gallery on right side
 - [ControlNet](https://github.com/Mikubill/sd-webui-controlnet) extension handling improved:
   - Script will no longer overwrite existing ControlNet input images.
   - Script will only target ControlNet models with no input image specified.
   - Allows, for example, a static depth background while animation feeds openpose.

![ControlNetInst](https://user-images.githubusercontent.com/93007558/224233623-88abcf87-3e01-4bf3-8209-6ee691b1f749.jpg)

**Tips:**
 - Configure and process the gif in img2img (it'll use the first frame) before running the script. Find a good seed!
 - If you add an image into ControlNet image window, it will default to that image for guidance for ALL frames.
 - Interpolation is not always necessary nor helpful.

**Installation:**
 - Install from the Automatic1111 WebUI extensions list, restart UI or
 - Clone this repo into your Automatic1111 WebUI /extensions folder, restart UI
 
**Changelog:**
- 3/09/23: ControlNet extension handling completely re-worked.
- 3/06/23: GIFs are now sent to results gallery(!) and "re-use last seed" works more reliably.
- 3/03/23: Added support for embedding generation into into GIF.
- 3/03/23: Blended inpainting picture had major performance issues on some systems; made optional.
