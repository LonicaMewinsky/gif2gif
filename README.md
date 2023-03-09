# gif2gif
Automatic1111 Stable Diffusion WebUI GIF Extension

### gif2gif script extension

The purpose of this script is to accept an animated gif as input, process frames as img2img typically would, and recombine them back into an animated gif. Intended to provide a fun, fast, gif-to-gif workflow that supports new models and methods such as Controlnet and InstructPix2Pix. Drop in a gif and go. Referenced code from prompts_from_file.

[ControlNet](https://github.com/Mikubill/sd-webui-controlnet) extensions handling improved.
 - Script will now only fill empty model image prompts with animation frames.
 - You can, for example, leave a static depth image in place while HED is animated.

Experimental/WIP similar repos:
- [Concurrent gif2gif](https://github.com/LonicaMewinsky/Concurrent-gif2gif) - Multiple frames in same latent space.
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

**Tips:**
 - Configure and process the gif in img2img (it'll use the first frame) before running the script. Find a good seed!
 - If you add an image into ControlNet image window, it will default to that image for guidance for ALL frames.
 - Interpolation is not always necessary nor helpful.

**Installation:**
 - Install from the Automatic1111 WebUI extensions list, restart UI or
 - Clone this repo into your Automatic1111 WebUI /extensions folder, restart UI
 
**Changelog:**
- 3/06/23: GIFs are now sent to results gallery(!) and "re-use last seed" works more reliably.
- 3/03/23: Added support for embedding generation into into GIF.
- 3/03/23: Blended inpainting picture had major performance issues on some systems; made optional.

![R](https://user-images.githubusercontent.com/93007558/216517487-542271b1-6fdb-4e54-a261-e500f5cc5c7a.gif)![download](https://user-images.githubusercontent.com/93007558/216803715-81dfc9e6-8c9a-47d5-9879-27acfac34eb8.gif)

![source](https://user-images.githubusercontent.com/93007558/216689956-4740b35e-aa2c-4869-955c-27836b56a378.gif)![gif2gif-0052](https://user-images.githubusercontent.com/93007558/216690052-6694989a-b2cb-42a8-a1d4-fc0ebd42776b.gif)

![werk-it](https://user-images.githubusercontent.com/93007558/222612353-36db8c42-38ba-42cc-8fb5-da59ab875ee4.gif)
![image](https://user-images.githubusercontent.com/93007558/222612321-74832002-6b3f-4022-ac0c-b6e93acebabe.png)
