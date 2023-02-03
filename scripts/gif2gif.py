import copy
import os
import modules.scripts as scripts
import modules.images
import gradio as gr
import numpy as np
import tempfile
from PIL import Image, ImageSequence
from modules.processing import Processed, process_images
from modules.shared import state

with open(os.path.join(scripts.basedir(), "readme.md"), 'r') as file:
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
        self.orig_n_frames = 0
        self.orig_dimensions = (0,0)
        self.ready = False
        self.desired_fps = 0
        self.desired_interp = 0
        self.desired_duration = 0
        self.slowmo = False
        self.gif2gifdir = tempfile.TemporaryDirectory()
        self.img2img_component = gr.Image()
        return None

    def title(self):
        return "gif2gif"
    def show(self, is_img2img):
        return is_img2img
    
    def ui(self, is_img2img):
        #Controls
        with gr.Accordion("Click for Readme", open = False):
            gr.Markdown(mkd_inst)
        with gr.Box():    
            with gr.Column():
                upload_gif = gr.File(label="Upload GIF", file_types = ['.gif;.webm'], live=True, file_count = "single")
                display_gif = gr.Image(inputs = upload_gif, visible = False, label = "Preview GIF", type= "filepath")
                with gr.Row():
                    with gr.Column():
                        with gr.Box():
                            fps_slider = gr.Slider(1, 50, step = 1, label = "Desired FPS")
                            interp_slider = gr.Slider(label = "Interpolation frames", value = 0)
                            gif_resize = gr.Checkbox(value = True, label="Resize result back to original dimensions")
                            gif_clear_frames = gr.Checkbox(value = True, label="Delete intermediate frames after GIF generation")
                    with gr.Column():
                        with gr.Box():
                            fps_actual = gr.Slider(1, 50, step = 1, interactive = False, label = "Actual FPS")
       
        #Control functions
        def processgif(gif):
            try:
                init_gif = Image.open(gif.name)
                self.gif_name = gif.name
                self.orig_dimensions = init_gif.size
                self.orig_duration = init_gif.info["duration"]
                self.orig_n_frames = init_gif.n_frames
                self.orig_fps = round(1000 / int(init_gif.info["duration"]))
                self.ready = True
                return init_gif, gif.name, gr.Image.update(visible = True), self.orig_fps
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
                calcdur = (1000 / fps) / (interp_frames+1)
                if calcdur < 20:
                    calcdur = 20
                    self.slowmo = True
                self.desired_duration = calcdur
                gifbuffer = (f"{self.gif2gifdir.name}/previewgif.gif")
                previewgif = Image.open(self.gif_name)
                previewgif.save(gifbuffer, format="GIF", save_all=True, duration=self.desired_duration, loop=0)
                if interp:
                    interp(gifbuffer, self.desired_interp, self.desired_duration)
                return gifbuffer, 1000/self.desired_duration
        
        #Control change events
        fps_slider.change(fn=fpsupdate, inputs = [fps_slider, interp_slider], outputs = [display_gif, fps_actual])
        interp_slider.change(fn=fpsupdate, inputs = [fps_slider, interp_slider], outputs = [display_gif, fps_actual])
        upload_gif.upload(fn=processgif, inputs = upload_gif, outputs = [self.img2img_component, display_gif, display_gif, fps_slider])
        upload_gif.change(fn=cleargif, inputs = upload_gif, outputs = display_gif)

        return [gif_resize, gif_clear_frames]

    #Grab the img2img image component for change later
    #Maybe there's a better way to do this?
    def after_component(self, component, **kwargs):
        if component.elem_id == "img2img_image":
            self.img2img_component = component
            return self.img2img_component
    
    #Main run
    def run(self, p, gif_resize, gif_clear_frames, *args):
        try:
            inp_gif = Image.open(self.gif_name)
        except:
            print("Something went wrong with GIF. Processing still from img2img.") #need better error checking
            proc = process_images(p)
            return proc
        #TODO: Add logic for seeds. Same seed every set? Iterate?
        return_images = []
        all_prompts = []
        infotexts = []
        inter_images = []
        gif_n_iter = p.n_iter
        state.job_count = inp_gif.n_frames * gif_n_iter
        state.job_no = 0
        p.do_not_save_grid = True
        p.do_not_save_samples = gif_clear_frames
        p.n_iter = 1 #we'll be processing iters per-gif-set
        outpath = os.path.join(p.outpath_samples, "gif2gif")
        print(f"Will process {gif_n_iter} GIF(s) with {state.job_count} total frames.")
        for x in range(gif_n_iter):
            if state.skipped:
                state.skipped = False
            if state.interrupted:
                break
            for frame in ImageSequence.Iterator(inp_gif):
                if state.skipped:
                    state.skipped = False
                if state.interrupted:
                    break
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
            #First make temporary file via save_images, then save actual gif over it..
            #Probably a better way to do this, but this easily maintains file name and .txt file logic
            gif_filename = (modules.images.save_image(inp_gif, outpath, "gif2gif", extension = 'gif', info = infotexts[0])[0])
            print(f"gif2gif: Generating GIF to {gif_filename}..")
            inter_images[0].save(gif_filename,
                save_all = True, append_images = inter_images[1:], loop = 0,
                optimize = False, duration = self.desired_duration)
            print(f"gif2gif: Interpolating {gif_filename}..")
            interp(gif_filename, self.desired_interp, self.desired_duration)
            return_images.extend(inter_images)
            inter_images = []
        return Processed(p, return_images, p.seed, "", all_prompts=all_prompts, infotexts=infotexts)