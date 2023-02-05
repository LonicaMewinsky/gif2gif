# gif2gif
Automatic1111 Stable Diffusion WebUI GIF Extension

### gif2gif script extension

The purpose of this script is to accept an animated gif as input, process frames as img2img typically would, and recombine them back into an animated gif. Not intended to have extensive functionality. Referenced code from prompts_from_file.

**Instructions:**
 - img2img batch *count* and *size* represent completed GIFs, not individual images.
    - eg a gif with 30 frames, batch count of 2, batch size of 3, will result in 6 gifs (180 images).
 - Drop or select gif in the below box; a preview should appear if it is a valid animated gif.
 - Adjust desired FPS if needed/wanted. Default slider position is original FPS.
 - Add interpolation frames if wanted. Preview should render.
   - Count of interp frames represent the number of blend steps between keyframes.
   - This is a very simple dynamic interp function; the keyframes are left as-is.
   - When *actual FPS* reaches 50, the maximum, the resultant gif will slow and extend to accomodate interp.
 - Results are dropped into outputs/img2img/gif2gif

**Tips:**
 - Configure and process the gif in img2img (it'll use the first frame) before running the script. Find a good seed!
 - Interpolation is not always necessary nor helpful.
 - Inpainting sort of works. Serendipitously.

**TODO:**
 - Figure out img2img subtabs (eg sketch). Extend functionality or find a way to leave them alone entirely.
 - Find a way to fold the script into img2img subtabs? Sketch, Inpaint, img2img..

![image](https://user-images.githubusercontent.com/93007558/216690484-d3679737-c179-46c9-8fd9-860816601451.png)

![R](https://user-images.githubusercontent.com/93007558/216517487-542271b1-6fdb-4e54-a261-e500f5cc5c7a.gif)![download](https://user-images.githubusercontent.com/93007558/216803715-81dfc9e6-8c9a-47d5-9879-27acfac34eb8.gif)

![source](https://user-images.githubusercontent.com/93007558/216689956-4740b35e-aa2c-4869-955c-27836b56a378.gif)![gif2gif-0052](https://user-images.githubusercontent.com/93007558/216690052-6694989a-b2cb-42a8-a1d4-fc0ebd42776b.gif)
