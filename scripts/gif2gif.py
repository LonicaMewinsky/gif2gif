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
from modules.shared import state

with open(os.path.join(scripts.basedir(), "instructions.txt"), 'r') as file:
    mkd_inst = file.read()

#Rudimentary interpolation
def interp(gif, iframes, dur):
    try:
        working_images = []
        resframes = []
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

class Script(scripts.Script):
    def __init__(self):
        self.gif_name = str()
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
        return None

    def title(self):
        return "gif2gif"
    def show(self, is_img2img):
        return is_img2img
    
    def ui(self, is_img2img):
        #Controls
        with gr.Box():    
            with gr.Column():
                upload_gif = gr.File(label="Upload GIF", file_types = ['.gif;.webm;'], live=True, file_count = "single")
                display_gif = gr.Image(inputs = upload_gif, visible = False, label = "Preview GIF", type= "filepath")
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
        with gr.Accordion("Click for Readme", open = False):
            gr.Markdown(mkd_inst)
        
        #Control functions
        def processgif(gif):
            try:
                init_gif = Image.open(gif.name)
                self.gif_name = gif.name
                #Need to also put images in img2img/inpainting windows (ui will not run without)
                #Gradio painting tools act weird with smaller images.. resize to 480 if smaller
                img_for_ui_path = (f"{self.gif2gifdir.name}/imgforui.gif")
                img_for_ui = init_gif
                if img_for_ui.height < 480:
                    img_for_ui = img_for_ui.resize((round(480*img_for_ui.width/img_for_ui.height), 480), Image.Resampling.LANCZOS)
                img_for_ui.save(img_for_ui_path)
                self.orig_dimensions = init_gif.size
                self.orig_duration = init_gif.info["duration"]
                self.orig_n_frames = init_gif.n_frames
                self.orig_total_seconds = round((self.orig_duration * self.orig_n_frames)/1000, 2)
                self.orig_fps = round(1000 / int(init_gif.info["duration"]), 2)
                self.ready = True
                return img_for_ui_path, img_for_ui_path, gif.name, gr.Image.update(visible = True), self.orig_fps, self.orig_fps, (f"{self.orig_total_seconds} seconds"), self.orig_n_frames
            except:
                print(f"Failed to load {gif.name}. Not a valid animated GIF?")
                return None
        
        def cleargif(up_val):
            if (up_val == None):
                self.gif_name = None
                self.ready = False
                return gr.Image.update(visible = False)        
        
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
                previewgif = Image.open(self.gif_name)
                previewgif.save(gifbuffer, format="GIF", save_all=True, duration=self.desired_duration, loop=0)
                if interp:
                    interp(gifbuffer, self.desired_interp, self.desired_duration)
                return gifbuffer, round(1000/self.desired_duration, 2), f"{self.desired_total_seconds} seconds", total_n_frames

        #Control change events
        fps_slider.change(fn=fpsupdate, inputs = [fps_slider, interp_slider], outputs = [display_gif, fps_actual, seconds_actual, frames_actual])
        interp_slider.change(fn=fpsupdate, inputs = [fps_slider, interp_slider], outputs = [display_gif, fps_actual, seconds_actual, frames_actual])
        upload_gif.upload(fn=processgif, inputs = upload_gif, outputs = [self.img2img_component, self.img2img_inpaint_component, display_gif, display_gif, fps_slider, fps_original, seconds_original, frames_original])
        upload_gif.change(fn=cleargif, inputs = upload_gif, outputs = display_gif)

        return [gif_resize, gif_clear_frames, gif_common_seed]

    #Grab the img2img image components for update later
    #Maybe there's a better way to do this?
    def after_component(self, component, **kwargs):
        if component.elem_id == "img2img_image":
            self.img2img_component = component
            return self.img2img_component
        if component.elem_id == "img2maskimg":
            self.img2img_inpaint_component = component
            return self.img2img_inpaint_component
    
    #Main run
    def run(self, p, gif_resize, gif_clear_frames, gif_common_seed, *args):
        try:
            inp_gif = Image.open(self.gif_name)
        except:
            print("Something went wrong with GIF. Processing still from img2img.")
            proc = process_images(p)
            return proc        
        return_images, all_prompts, infotexts, inter_images = [], [], [], []
        state.job_count = inp_gif.n_frames * p.n_iter
        p.do_not_save_grid = True
        p.do_not_save_samples = gif_clear_frames
        gif_n_iter = p.n_iter
        p.n_iter = 1 #we'll be processing iters per-gif-set
        outpath = os.path.join(p.outpath_samples, "gif2gif")
        print(f"Will process {gif_n_iter * p.batch_size} GIF(s) with {state.job_count * p.batch_size} total frames.")
        
        #Iterate batch count
        for x in range(gif_n_iter):
            if state.skipped: state.skipped = False
            if state.interrupted: break
            if(gif_common_seed and (p.seed == -1)):
                p.seed = random.randrange(100000000, 999999999)
            
            #Iterate frames
            for frame in ImageSequence.Iterator(inp_gif):
                if state.skipped: state.skipped = False
                if state.interrupted: break
                state.job = f"{state.job_no + 1} out of {state.job_count}"
                copy_p = copy.copy(p)
                copy_p.init_images = [frame] * p.batch_size
                proc = process_images(copy_p)
                inter_images += proc.images
                all_prompts += proc.all_prompts
                infotexts += proc.infotexts
            if(gif_resize):
                for i in range(len(inter_images)):
                    inter_images[i] = inter_images[i].resize(self.orig_dimensions)
            
            #Separate frames by batch size
            inter_batch = []
            for b in range(p.batch_size):
                for bi in inter_images[(b)::p.batch_size]:
                    inter_batch.append(bi)
                #First make temporary file via save_images, then save actual gif over it..
                #Probably a better way to do this, but this easily maintains file name and .txt file logic
                gif_filename = (modules.images.save_image(inp_gif, outpath, "gif2gif", extension = 'gif', info = infotexts[b])[0])
                print(f"gif2gif: Generating GIF to {gif_filename}..")
                inter_batch[0].save(gif_filename,
                    save_all = True, append_images = inter_batch[1:], loop = 0,
                    optimize = False, duration = self.desired_duration)
                if(self.desired_interp > 0):
                    print(f"gif2gif: Interpolating {gif_filename}..")
                    interp(gif_filename, self.desired_interp, self.desired_duration)
                return_images.extend(inter_batch)
                inter_batch = []
            inter_images = []
        return Processed(p, return_images, p.seed, "", all_prompts=all_prompts, infotexts=infotexts)