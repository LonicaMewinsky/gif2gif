// mouseover tooltips for various UI elements

titles = {
    "Upload GIF": "Click here to upload your GIF",
	"Desired FPS": "Target FPS; defaults to original FPS",
	"Interpolation frames": "Number of transition frames between key frames",
	"Loopback decay": "Factor change for every loop generation. <1 for noise falloff, >1 for noise rampup"
}


onUiUpdate(function(){
	gradioApp().querySelectorAll('span, button, select, p').forEach(function(span){
		tooltip = titles[span.textContent];

		if(!tooltip){
		    tooltip = titles[span.value];
		}

		if(!tooltip){
			for (const c of span.classList) {
				if (c in titles) {
					tooltip = titles[c];
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
            select.title = titles[select.value] || "";
	    }
	})
})
