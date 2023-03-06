// mouseover tooltips for various UI elements in the form of "UI element label"="Tooltip text".

gif2gif_titles = {
    "Upload GIF": "Click here to upload your GIF",
	"Desired FPS": "Target FPS; defaults to original FPS",
	"Interpolation frames": "Number of transition frames between key frames",
	"Loopback decay": "Factor change for every loop generation. <1 for noise falloff, >1 for noise rampup"
}


onUiUpdate(function(){
	gradioApp().querySelectorAll('span, button, select, p').forEach(function(span){
		tooltip = gif2gif_titles[span.textContent];

		if(!tooltip){
		    tooltip = gif2gif_titles[span.value];
		}

		if(!tooltip){
			for (const c of span.classList) {
				if (c in gif2gif_titles) {
					tooltip = gif2gif_titles[c];
					break;
				}
			}
		}

		if(tooltip){
			span.title = tooltip;
		}
	})

	gradioApp().querySelectorAll('select').forEach(function(select){
	    if (select.onchange != null) return;

	    select.onchange = function(){
            select.title = gif2gif_titles[select.value] || "";
	    }
	})
})
