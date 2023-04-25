import copy
import modules.scripts as scripts
import modules.images
import gradio as gr
import numpy as np
import importlib
from PIL import Image
from modules.shared import opts, state
from modules.processing import Processed, process_images

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

def file_to_list(file_path):
    with Image.open(file_path) as im:
        frames = []
        try:
            while True:
                frames.append(im.copy())
                im.seek(len(frames))
        except EOFError:
            pass
    return frames

class Script(scripts.Script):
    def __init__(self):
        self.img2img_component = gr.Image()
        self.img2img_inpaint_component = gr.Image()
        return None

    def title(self):
        return "gif2gif"
    
    def show(self, is_img2img):
        return is_img2img

    def after_component(self, component, **kwargs):
        if component.elem_id == "img2img_image":
            self.img2img_component = component
        if component.elem_id == "img2maskimg":
            self.img2img_inpaint_component = component
        
    def ui(self, is_img2img):
        try:
            cnet_num = opts.data.get("control_net_max_models_num", 1)
        except:
            cnet_num = 0
        #Controls
        with gr.Row():
            with gr.Column():
                with gr.Tabs():
                    with gr.Tab("Settings"):
                        if cnet_num > 0:
                            cnet_targets = gr.Dropdown(label="Target ControlNet models", multiselect=True, choices=[str(x) for x in range(cnet_num)])
                        gif_format = gr.Dropdown(label="Format", choices=["gif", "apng", "webp"], value="gif")
                        gif_resize = gr.Checkbox(value = True, label="Resize result back to original dimensions")
                        gif_clear_frames = gr.Checkbox(value = True, label="Delete intermediate frames after GIF generation")
                        gif_common_seed = gr.Checkbox(value = True, label="For -1 seed, all frames in a GIF have common seed")
                    with gr.Tab("Information"):
                        fps_original = gr.Number(value=0, interactive = False, label = "Original FPS")
                        seconds_original = gr.Number(value=0, interactive = False, label = "Original total duration")
                        frames_original = gr.Number(value=0, interactive = False, label = "Original total frames")
                        duration_original = gr.State(value=0)
                    with gr.Tab("Inpainting", open = False):
                        with gr.Column():
                            inpaint_md = gr.Markdown("Before sending image, ensure img2img Inpaint tab is selected.")
                            send_firstframe = gr.Button("Send first frame to img2img Inpainting tab")
                            send_blend = gr.Button("Send blended image to img2img Inpainting tab")
            with gr.Column():
                upload_gif = gr.File(label="Upload GIF", visible=True, file_types = ['.gif','.webp','.apng'], file_count = "single")
                display_gif = gr.Image(label = "Preview GIF", Source="Upload", visible=False, interactive=True, type="filepath")
        
        def process_upload(file):
            try:
                init_gif = Image.open(file.name)
                ani_duration = 50
                try:
                    ani_duration = init_gif.info["duration"]
                except:
                    pass
                if init_gif.height < 480:
                    init_gif.resize((round(480*init_gif.width/init_gif.height), 480), Image.Resampling.LANCZOS)
                file_length = round((ani_duration * init_gif.n_frames)/1000, 2)
                file_fps = round(1000 / int(ani_duration), 2)
                return file.name, gr.Image.update(file.name, visible=True), gr.File.update(visible=False), file_fps, file_length, init_gif.n_frames, ani_duration
            except:
                print("gif2gif: Problem with loading animation.")
                return gr.Image.update(), gr.Image.update(), gr.File.update(), gr.Number.update(), gr.Number.update(), gr.Number.update(), gr.State.update()
        
        def clear_image():
            return gr.Image.update(value=None, visible=False), gr.File.update(value=None, visible=True), 0, 0, 0
        
        def make_blend(file):
            if file == None:
                return gr.Image.update() #none
            else:
                frames = file_to_list(file.name)
                frames = [x.convert("RGBA") for x in frames]
                blended = blend_images(frames)
                if blended.height < 480:
                    blended.resize((round(480*blended.width/blended.height), 480), Image.Resampling.LANCZOS)
                return blended
            
        def make_firstframe(file):
            if file == None:
                return gr.Image.update() #none
            else:
                frames = file_to_list(file.name)
                frame = frames[0].convert("RGBA")
                if frame.height < 480:
                    frame.resize((round(480*frame.width/frame.height), 480), Image.Resampling.LANCZOS)
                return frame
        
        upload_gif.upload(process_upload, inputs=[upload_gif], outputs=[self.img2img_component, display_gif, upload_gif, fps_original, seconds_original, frames_original, duration_original])
        display_gif.clear(clear_image, inputs=None, outputs=[display_gif, upload_gif, fps_original, seconds_original, frames_original])
        send_blend.click(make_blend, inputs=[upload_gif], outputs=[self.img2img_inpaint_component])
        send_firstframe.click(make_firstframe, inputs=[upload_gif], outputs=[self.img2img_inpaint_component])
        return cnet_targets, gif_resize, gif_clear_frames, gif_common_seed, frames_original, duration_original, upload_gif, gif_format
    
     #Main run
    def run(self, p, cnet_targets, gif_resize, gif_clear_frames, gif_common_seed, frames_original, duration_original, upload_gif, gif_format):
        #Check for ControlNet
        cnet_present = False
        try:
            cnet = importlib.import_module('extensions.sd-webui-controlnet.scripts.external_code', 'external_code')
            cnet_models = cnet.get_all_units_in_processing(p)
            cnet_targets = [int(x) for x in cnet_targets]
            cnet_present = True
        except:
            pass
        #Generate generation chunks (based on batch size) from input file
        try:
            raw_frames = file_to_list(upload_gif.name)
        except:
            print("Something went wrong with GIF. Processing still from img2img.")
            return None
        #Setup vars
        state.job_count = len(raw_frames) * p.n_iter
        p.do_not_save_grid = True
        p.do_not_save_samples = gif_clear_frames
        all_prompts = []
        infotexts = []
        return_files = []
        print(f"Will process {p.n_iter} GIF(s) with {state.job_count} total generations.")
        #Perform iterations
        for x in range(p.n_iter):
            copy_p = copy.copy(p)
            copy_p.n_iter = 1
            if(gif_common_seed and (copy_p.seed == -1)):
                modules.processing.fix_seed(copy_p)
            #Generate against frames
            gen_frames = []
            for frame in raw_frames:
                if state.skipped: state.skipped = False
                if state.interrupted: break
                state.job = f"{state.job_no + 1} out of {state.job_count}"
                copy_p.init_images = [frame] * copy_p.batch_size
                #Handle controlnets
                if cnet_present:
                    new_units = []
                    for i in range(len(cnet_models)):
                        if (i in cnet_targets):
                            nimg = np.array(frame.convert("RGB"))
                            bimg = np.zeros((frame.width, frame.height, 3), dtype = np.uint8)
                            cnet_models[i].image = [{"image" : nimg, "mask" : bimg}]
                        new_units.append(cnet_models[i])
                    cnet.update_cn_script_in_processing(p, new_units)
                #Generate
                proc = process_images(copy_p)
                if len(proc.images) > 1:
                    gen_frames.append(blend_images(proc.images))
                else:
                    gen_frames.append(proc.images[0])
                all_prompts += proc.all_prompts
                infotexts += proc.infotexts
            if(gif_resize):
                for i in range(len(gen_frames)):
                    gen_frames[i] = gen_frames[i].resize(raw_frames[0].size)
            #Save output
            out_filename = (modules.images.save_image(gen_frames[0], p.outpath_samples, "gif2gif", extension = gif_format)[0])
            file_info=""
            if opts.enable_pnginfo and infotexts[0] is not None:
                file_info = infotexts[0].replace('\n', ', ')
            print(f"gif2gif: Generating GIF to {out_filename}..")
            gen_frames[0].save(out_filename,
                save_all = True, append_images = gen_frames[1:], loop = 0,
                optimize = False, duration = duration_original, comment=file_info)
            return_files.append(out_filename)
        return Processed(copy_p, return_files, copy_p.seed, "", all_prompts=all_prompts, infotexts=infotexts)