import copy
import os
import modules.scripts as scripts
import modules.images
import gradio as gr
import numpy as np
import tempfile
import random
from PIL import Image, ImageSequence
from modules.processing import Processed, process_images
from modules.shared import state, sd_upscalers

with open(os.path.join(scripts.basedir(), "instructions.txt"), 'r') as file:
    mkd_inst = file.read()

#Rudimentary interpolation
def interp(gif, iframes, dur):
    try:
        working_images, resframes = [], []
        pilgif = Image.open(gif)
        for frame in ImageSequence.Iterator(pilgif):
            converted = frame.convert('RGBA')
            working_images.append(converted)
        resframes.append(working_images[0]) #Seed the first frame
        alphas = np.linspace(0, 1, iframes+2)[1:]
        for i in range(1, len(working_images), 1):
            for a in range(len(alphas)):
                intermediate_image = Image.blend(working_images[i-1],working_images[i],alphas[a])
                resframes.append(intermediate_image)
        resframes[0].save(gif,
            save_all = True, append_images = resframes[1:], loop = 0,
            optimize = False, duration = dur, format='GIF')
        return gif
    except:
        return False

#Get num closest to 8
def cl8(num):
    rem = num % 8
    if rem <= 4:
        return round(num - rem)
    else:
        return round(num + (8 - rem))

def upscale(image, upscaler_name, upscale_mode, upscale_by, upscale_to_width, upscale_to_height, upscale_crop):
    if upscale_mode == 1:
        upscale_by = max(upscale_to_width/image.width, upscale_to_height/image.height)
    
    upscaler = next(iter([x for x in sd_upscalers if x.name == upscaler_name]), None)
    assert upscaler or (upscaler_name is None), f'could not find upscaler named {upscaler_name}'

    image = upscaler.scaler.upscale(image, upscale_by, upscaler.data_path)
    if upscale_mode == 1 and upscale_crop:
        cropped = Image.new("RGB", (upscale_to_width, upscale_to_height))
        cropped.paste(image, box=(upscale_to_width // 2 - image.width // 2, upscale_to_height // 2 - image.height // 2))
        image = cropped

    return image

def blend_images(images):
    sizes = [img.size for img in images]
    min_width, min_height = min(sizes, key=lambda s: s[0]*s[1])
    blended_img = Image.new('RGB', (min_width, min_height))
    
    for x in range(min_width):
        for y in range(min_height):
            colors = [img.getpixel((x, y)) for img in images]
            avg_color = tuple(int(sum(c[i] for c in colors) / len(colors)) for i in range(3))
            blended_img.putpixel((x, y), avg_color)
    
    return blended_img

class Script(scripts.Script):
    def __init__(self):
        self.gif_name = str()
        self.gif_frames = []
        self.orig_fps = 0
        self.orig_duration = 0
        self.orig_total_seconds = 0
        self.orig_n_frames = 0
        self.orig_dimensions = (0,0)
        self.ready = False
        self.desired_fps = 0
        self.desired_interp = 0
        self.desired_duration = 0
        self.desired_total_seconds = 0
        self.slowmo = False
        self.gif2gifdir = tempfile.TemporaryDirectory()
        self.img2img_component = gr.Image()
        self.img2img_inpaint_component = gr.Image()
        self.img2img_gallery = gr.Gallery()
        self.img2img_w_slider = gr.Slider()
        self.img2img_h_slider = gr.Slider()
        return None

    def title(self):
        return "gif2gif"

    def show(self, is_img2img):
        return is_img2img
    
    def ui(self, is_img2img):
        #Controls
        with gr.Tabs():
            with gr.Tab("Settings"):
                with gr.Column():
                    with gr.Row():
                        with gr.Column():
                            with gr.Box():
                                fps_slider = gr.Slider(1, 50, step = 1, label = "Desired FPS")
                                interp_slider = gr.Slider(label = "Interpolation frames", value = 0)
                                gif_resize = gr.Checkbox(value = True, label="Resize result back to original dimensions")
                                gif_clear_frames = gr.Checkbox(value = True, label="Delete intermediate frames after GIF generation")
                                gif_common_seed = gr.Checkbox(value = True, label="For -1 seed, all frames in a GIF have common seed")
                        with gr.Column():   
                            with gr.Row():
                                with gr.Box():
                                    with gr.Column():
                                        fps_actual = gr.Textbox(value="", interactive = False, label = "Actual FPS")
                                        seconds_actual = gr.Textbox(value="", interactive = False, label = "Actual total duration")
                                        frames_actual = gr.Textbox(value="", interactive = False, label = "Actual total frames")
                                with gr.Box():
                                    with gr.Column():
                                        fps_original = gr.Textbox(value="", interactive = False, label = "Original FPS")
                                        seconds_original = gr.Textbox(value="", interactive = False, label = "Original total duration")
                                        frames_original = gr.Textbox(value="", interactive = False, label = "Original total frames")
            with gr.Tab("Loopback"):
                loop_backs = gr.Slider(0, 50, step = 1, label = "Generation loopbacks", value = 0)
                loop_denoise = gr.Slider(0.01, 1, step = 0.01, value=0.10, interactive = True, label = "Loopback denoise strength")
                loop_decay = gr.Slider(0, 2, step = 0.05, value=1.0, interactive = True, label = "Loopback decay")
            with gr.Tab("Upscaling"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Box():
                                ups_upscaler = gr.Dropdown(value = "None", interactive = True, choices = [x.name for x in sd_upscalers], label = "Upscaler")
                                ups_only_upscale = gr.Checkbox(value = False, label = "Skip generation, only upscale")
                        with gr.Column():
                            with gr.Tabs():
                                with gr.Tab("Scale by") as tab_scale_by:
                                    with gr.Box():   
                                        ups_scale_by = gr.Slider(1, 8, step = 0.1, value=2, interactive = True, label = "Factor")
                                with gr.Tab("Scale to") as tab_scale_to:
                                    with gr.Box():
                                        with gr.Column():
                                            ups_scale_to_w = gr.Slider(0, 8000, step = 8, value=512, interactive = True, label = "Target width")
                                            ups_scale_to_h = gr.Slider(0, 8000, step = 8, value=512, interactive = True, label = "Target height")
                                            ups_scale_to_crop = gr.Checkbox(value = False, label = "Crop to fit")
            with gr.Tab("Inpainting", open = False):
                with gr.Column():
                    make_blend = gr.Button("Send blended image to img2img Inpainting tab")
            with gr.Tab("Readme", open = False):
                gr.Markdown(mkd_inst)
        with gr.Column():
            upload_gif = gr.File(label="Upload GIF", visible=True, file_types = ['.gif','.webp','.plc'], file_count = "single")
            display_gif = gr.Image(label = "Preview GIF", Source="Upload", visible=False, interactive=True, type="filepath")

        def processgif(file):
            try:
                pimg = ImageSequence.Iterator(Image.open(file.name))[0]
            except:
                print("Could not load GIF.") #Make no changes
                return gr.Image.update(), gr.Image.update(), gr.Image.update(), gr.Slider.update(), gr.Textbox.update(), gr.Textbox.update(), gr.Textbox.update()
            init_gif = Image.open(file.name)
            self.gif_name = file.name
            self.orig_dimensions = init_gif.size
            self.orig_duration = init_gif.info["duration"]
            self.orig_n_frames = init_gif.n_frames
            self.orig_total_seconds = round((self.orig_duration * self.orig_n_frames)/1000, 2)
            self.orig_fps = round(1000 / int(init_gif.info["duration"]), 2)
            #Need to also put images in img2img/inpainting windows (ui will not run without)
            #Gradio painting tools act weird with smaller images.. resize to 480 if smaller
            self.gif_frames = []
            for frame in ImageSequence.Iterator(init_gif):
                if frame.height < 480:
                    converted = frame.resize((round(480*frame.width/frame.height), 480), Image.Resampling.LANCZOS).convert('RGBA')
                else:
                    converted = frame.convert('RGBA')
                self.gif_frames.append(converted)
            self.ready = True
            self.img2img_gallery.update([file.name])
            return self.gif_frames[0], self.gif_frames[0], cl8(pimg.width), cl8(pimg.height), gr.File.update(visible=False), gr.Image.update(value=file.name, visible=True), self.orig_fps, self.orig_fps, (f"{self.orig_total_seconds} seconds"), self.orig_n_frames

        def clear_gif(gif):
            if gif == None:
                return None, None, gr.File.update(value=None, visible=True), gr.Image.update(visible=False)
            else:
                return gr.Image.update(), gr.Image.update(), gr.File.update(), gr.Image.update()  
            
        def fpsupdate(fps, interp_frames):
            if (self.ready and fps and (interp_frames != None)):
                self.desired_fps = fps
                self.desired_interp = interp_frames
                total_n_frames = self.orig_n_frames + ((self.orig_n_frames -1) * self.desired_interp)
                calcdur = (1000 / fps) / (total_n_frames/self.orig_n_frames)
                if calcdur < 20:
                    calcdur = 20
                    self.slowmo = True
                self.desired_duration = calcdur
                self.desired_total_seconds = round((self.desired_duration * total_n_frames)/1000, 2)
                gifbuffer = (f"{self.gif2gifdir.name}/previewgif.gif")
                self.gif_frames[0].save(gifbuffer,
                    save_all = True, append_images = self.gif_frames[1:], loop = 0,
                    optimize = False, duration = self.desired_duration)
                return gifbuffer, round(1000/self.desired_duration, 2), f"{self.desired_total_seconds} seconds", total_n_frames
        
        def send_blend():
            blend = blend_images(self.gif_frames)
            return blend
        
        #Control change events
        fps_slider.change(fn=fpsupdate, inputs = [fps_slider, interp_slider], outputs = [display_gif, fps_actual, seconds_actual, frames_actual])
        interp_slider.change(fn=fpsupdate, inputs = [fps_slider, interp_slider], outputs = [display_gif, fps_actual, seconds_actual, frames_actual])
        ups_scale_mode = gr.State(value = 0)
        tab_scale_by.select(fn=lambda: 0, inputs=[], outputs=[ups_scale_mode])
        tab_scale_to.select(fn=lambda: 1, inputs=[], outputs=[ups_scale_mode])
        upload_gif.upload(fn=processgif, inputs = upload_gif, outputs = [self.img2img_component, self.img2img_inpaint_component, self.img2img_w_slider, self.img2img_h_slider, upload_gif, display_gif, fps_slider, fps_original, seconds_original, frames_original])
        display_gif.change(fn=clear_gif, inputs=display_gif, outputs=[self.img2img_component, self.img2img_inpaint_component, upload_gif, display_gif])
        make_blend.click(fn=send_blend, inputs=None, outputs=[self.img2img_inpaint_component])

        return [gif_resize, gif_clear_frames, gif_common_seed, loop_backs, loop_denoise, loop_decay, ups_upscaler, ups_only_upscale, ups_scale_mode, ups_scale_by, ups_scale_to_w, ups_scale_to_h, ups_scale_to_crop]

    #Grab the img2img image components for update later
    #Maybe there's a better way to do this?
    def after_component(self, component, **kwargs):
        if component.elem_id == "img2img_image":
            self.img2img_component = component
            return self.img2img_component
        if component.elem_id == "img2maskimg":
            self.img2img_inpaint_component = component
            return self.img2img_inpaint_component
        if component.elem_id == "img2img_width":
            self.img2img_w_slider = component
            return self.img2img_w_slider
        if component.elem_id == "img2img_height":
            self.img2img_h_slider = component
            return self.img2img_h_slider
        
    #Main run
    def run(self, p, gif_resize, gif_clear_frames, gif_common_seed, loop_backs, loop_denoise, loop_decay, ups_upscaler, ups_only_upscale, ups_scale_mode, ups_scale_by, ups_scale_to_w, ups_scale_to_h, ups_scale_to_crop):
        try:
            inc_frames = self.gif_frames
        except:
            print("Something went wrong with GIF. Processing still from img2img.")
            proc = process_images(p)
            return proc
        outpath = os.path.join(p.outpath_samples, "gif2gif")
        
        #Handle upscaling
        if (ups_upscaler != "None"):
            inc_frames = [upscale(frame, ups_upscaler, ups_scale_mode, ups_scale_by, ups_scale_to_w, ups_scale_to_h, ups_scale_to_crop) for frame in inc_frames]
            if ups_only_upscale:
                gif_filename = (modules.images.save_image(inc_frames[0], outpath, "gif2gif", extension = 'gif')[0])
                print(f"gif2gif: Generating GIF to {gif_filename}..")
                inc_frames[0].save(gif_filename,
                    save_all = True, append_images = inc_frames[1:], loop = 0,
                    optimize = False, duration = self.desired_duration)
                return Processed(p, inc_frames)
        
        #Fix/setup vars
        return_images, all_prompts, infotexts, inter_images = [], [], [], []
        state.job_count = self.orig_n_frames * p.n_iter * (loop_backs+1)
        p.do_not_save_grid = True
        p.do_not_save_samples = gif_clear_frames
        gif_n_iter = p.n_iter
        p.n_iter = 1

        #Iterate batch count
        print(f"Will process {gif_n_iter} GIF(s) with {state.job_count * p.batch_size} total generations.")
        for x in range(gif_n_iter):
            if state.skipped: state.skipped = False
            if state.interrupted: break
            copy_p = copy.copy(p)
            color_correction = [modules.processing.setup_color_correction(copy_p.init_images[0])]
            if(gif_common_seed and (p.seed == -1)):
                modules.processing.fix_seed(copy_p)
            
            #Iterate frames
            for frame in inc_frames:
                if state.skipped: state.skipped = False
                if state.interrupted: break
                copy_p.denoising_strength = p.denoising_strength #reset denoise
                frame_loop_denoise = loop_denoise
                state.job = f"{state.job_no + 1} out of {state.job_count}"
                copy_p.init_images = [frame] * p.batch_size #inject current frame
                copy_p.control_net_input_image = frame.convert("RGB") #account for controlnet
                proc = process_images(copy_p) #process
                #Do loopbacks
                for _ in range(loop_backs):
                    copy_p.init_images = [proc.images[0].convert("RGB")] * p.batch_size
                    copy_p.color_corrections = color_correction
                    copy_p.denoising_strength = frame_loop_denoise
                    proc = process_images(copy_p)
                    frame_loop_denoise = round(frame_loop_denoise*loop_decay, 2)
                #Handle batches
                proc_batch = []
                for pi in proc.images:
                    if type(pi) is Image.Image:
                        proc_batch.append(pi)
                if len(proc_batch) > 1 and p.batch_size > 1:
                    inter_images.append(blend_images(proc_batch))
                else:
                    inter_images.append(proc_batch[0])
                all_prompts += proc.all_prompts
                infotexts += proc.infotexts
            #Resize and make gif
            if(gif_resize):
                for i in range(len(inter_images)):
                    inter_images[i] = inter_images[i].resize(self.orig_dimensions)
            #First make temporary file via save_images, then save actual gif over it..
            #Probably a better way to do this, but this easily maintains file name and .txt file logic
            gif_filename = (modules.images.save_image(inc_frames[0], outpath, "gif2gif", extension = 'gif', info = infotexts[0])[0])
            print(f"gif2gif: Generating GIF to {gif_filename}..")
            inter_images[0].save(gif_filename,
                save_all = True, append_images = inter_images[1:], loop = 0,
                optimize = False, duration = self.desired_duration)
            if(self.desired_interp > 0):
                print(f"gif2gif: Interpolating {gif_filename}..")
                interp(gif_filename, self.desired_interp, self.desired_duration)
            
            if not gif_clear_frames:
                return_images.extend(inter_images)
            return_images.append(Image.open(gif_filename))
        inter_images = []
        
        return Processed(p, return_images, p.seed, "", all_prompts=all_prompts, infotexts=infotexts)