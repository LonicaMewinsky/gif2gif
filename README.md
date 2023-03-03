# gif2gif
Automatic1111 Stable Diffusion WebUI GIF Extension

### gif2gif script extension

The purpose of this script is to accept an animated gif as input, process frames as img2img typically would, and recombine them back into an animated gif. Intended to provide a fun, fast, gif-to-gif workflow that supports new models and methods such as InstructPix2Pix. Drop in a gif and go. Referenced code from prompts_from_file.

**Instructions:**
 - For ControlNet support, make sure to enable "Allow other script to control this extension" in settings.
 - img2img batch *count* represents completed GIFs, not individual images.
 - All images in a single batch will be blended together. May help with consistency between frames.
 - Drop or select gif in the script's box; a preview should appear if it is a valid animated gif.
 - Inpainting works, but currently limited to one mask applied to all frames equally.
 - Adjust desired FPS if needed/wanted. Default slider position is original FPS.
 - Add interpolation frames if wanted. Preview should render.
   - Count of interp frames represent the number of blend steps between keyframes.
   - This is a very simple dynamic interp function; the keyframes are left as-is.
   - When *actual FPS* reaches 50, the maximum, the resultant gif will slow and extend to accomodate interp.
 - Results are dropped into outputs/img2img/gif2gif

**Tips:**
 - Configure and process the gif in img2img (it'll use the first frame) before running the script. Find a good seed!
 - If you add an image into ControlNet image window, it will default to that image for guidance for ALL frames.
 - Interpolation is not always necessary nor helpful.

**Installation:**
 - Install from the Automatic1111 WebUI extensions list, restart UI or
 - Clone this repo into your Automatic1111 WebUI /extensions folder, restart UI
 
**Changelog:**
- 3/02/23: Changed inpainting functionality -- blends frames for better representation.
- 2/26/23: Changed batch size functionality.
- 2/26/23: Added loopback denoise decay slider.
- 2/25/23: Added loopback denoise slider.
- 2/24/23: Added loopback support. Less than 0.2 denoise recommended.
- 2/23/23: Added upscaling support. Can possibly help with controlnet annotations.
- 2/23/23: Updated UI, fixed a bug, extended support for "multi-model" controlnet.
- 2/20/23: Fixed issue with first frame not working with controlnet extension.
- 2/14/23: Now works, mostly, with https://github.com/Mikubill/sd-webui-controlnet extension.
- 2/10/23: Updated inpainting window to behave more predictably
- 2/10/23: Fixed inpainting window odd behavior on images smaller than 480h

![image](https://user-images.githubusercontent.com/93007558/222612321-74832002-6b3f-4022-ac0c-b6e93acebabe.png)
![werk-it](https://user-images.githubusercontent.com/93007558/222612353-36db8c42-38ba-42cc-8fb5-da59ab875ee4.gif)
![R](https://user-images.githubusercontent.com/93007558/216517487-542271b1-6fdb-4e54-a261-e500f5cc5c7a.gif)![download](https://user-images.githubusercontent.com/93007558/216803715-81dfc9e6-8c9a-47d5-9879-27acfac34eb8.gif)

![source](https://user-images.githubusercontent.com/93007558/216689956-4740b35e-aa2c-4869-955c-27836b56a378.gif)![gif2gif-0052](https://user-images.githubusercontent.com/93007558/216690052-6694989a-b2cb-42a8-a1d4-fc0ebd42776b.gif)
