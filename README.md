# gif2gif
Automatic1111 gif extension

### gif2gif script extension

The purpose of this script is to accept an animated gif as input, process frames as img2img typically would, and recombine them back into an animated gif. Not intended to have extensive functionality. Referenced code from prompts_from_file.

**Instructions:**
 - img2img batch *count* represents how many individual recombined gifs are created.
 - img2img batch *size* represents how many times a gif is cycled into one recombined gif.
 - Drop or select gif in the below box; a preview should appear if it is a valid animated gif.
 - Adjust desired FPS if needed/wanted. Default slider position is original FPS.
 - Add interpolation frames if wanted. Preview should render.
   - Count of interp frames represent the number of blend steps between keyframes.
   - This is a very simple interp function; the keyframes are left as-is.
   - When *actual FPS* reaches 50, the maximum, the resultant gif will slow and extend to accomodate interp.
 - Results are dropped into outputs/img2img/gif2gif

**Tips:**
 - Configure and process the gif in img2img (it'll use the first frame) before running the script. Find a good seed!
 - Interpolation is not always necessary nor helpful.

![R](https://user-images.githubusercontent.com/93007558/216517487-542271b1-6fdb-4e54-a261-e500f5cc5c7a.gif) ![gif2gif-0011](https://user-images.githubusercontent.com/93007558/216517468-ce188729-5472-4558-a1bc-4059af1e0bc4.gif)
