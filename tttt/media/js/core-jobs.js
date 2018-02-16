/* Core-jobs.js */

var preLoadTabUID = null;
function initPage() {
	// Set default disable buttons
	$('.action-panel button', detailPanel.elm).prop('disabled', $('.recipe-list', detailPanel.elm).children('div').length == 0);

	// Add autocomplete into name field
	var authors = getAuthor();
	var list = [];
	for (ix in authors) {
		list.push({label: authors[ix].name+" - "+authors[ix].email, value: authors[ix].email})
	}
	$('#id_username', detailPanel.elm).autocomplete({minLength: 0, source: list});

	// Save selected recipes into one hidden field.
	$('.action-panel form', detailPanel.elm).submit(function(){
		var res = [];
		var recipes = $('.recipe-list > div', detailPanel.elm);
        for (var ix=0, max=recipes.length; ix < max; ix++) {
					console.log($(recipes[ix]))
          res[res.length] = $(recipes[ix]).text().trim();
		};
		$('input[name="uids"]', detailPanel.elm).val(res.join(' '));
	});

  events.addEvent('DELETE',function() {
		this.data.box_el.removeClass('selected');
		this.data.button_el.remove();
		var ix = detailPanel.getIndexTab(this);
		var tab = detailPanel.getTab(ix+1);
		if (tab == null) {
			tab = detailPanel.getTab(ix-1)
		}
		tab.open();
		// Disable comment buttons, if no-recipe is selected.
		if ($('.recipe-list div', detailPanel.elm).length == 0) {
			$("button[data-action-field='action']", detailPanel.elm).attr('disabled',"");
		}
  });

	events.addEvent('UPDATE', function() {
			$('.filter-switch .btn', this.content_elm).click(function(){
				loadTasks($(this).closest('div.tab-panel').data('detailTab').data.id,
						  $(this).children('input').attr('name'));
			});
			$('.comentsSwitcher', this.content_elm).click(function(){
				$(this).toggleClass('glyphicon-chevron-down')
					   .toggleClass('glyphicon-chevron-right')
					   .parent().next('ul').toggle();
				return false;
			});
	});

	events.addEvent('HOVER', function(direct) {
		if (this.data.box_el == null) return;
		if (direct == 'IN') {
			this.data.box_el.addClass('light');
		} else {
			this.data.box_el.removeClass('light');
		}
	});

  var uid = window.location.hash.substring(1);
	if (uid.match(/^R:[0-9]+/) != null) {
		//previewRecipe(uid);
		var sElm = $("td[id='"+uid+"']");
        previewRecipe.apply(sElm.get(0), [null, true])
        saveDetailTab.apply(sElm.get(0))
        $('html, body').animate({
	        scrollTop: sElm.offset().top - 200
        }, {
            duration: 2000,
	    });
    }
}

function render_progressbar(data) {
	var tasks = data.tasks;
	var out = "";
	out += '<div class="progress myprogress">';
	if (tasks) {
		var lastStyle = "";
		var sumDuration = 0;
		var progressDuration = 0;
		var last_compleated = 0;
		var taskLength = tasks.length;
		for(ix in tasks) {
			if (tasks[ix].duration < 0) {
				sumDuration += 300;
			} else {
				sumDuration += tasks[ix].duration;
				last_compleated = ix;
			}
		}
		var deficit = 0;  // it solves the problem with realy small step.
		for(ix in tasks) {
			var task = tasks[ix];
			var status = "";
			var duration = task.duration < 0 ? 300 : task.duration;
			var step =  duration * 100 / sumDuration;
			if (step < 0.1) {
				deficit += 0.1 - step;
				step = 0.1;
			}
			if (step > 5*deficit) {
				step = step - deficit;
				deficit = 0;
			}
			progressDuration += duration;
			var icon = getTaskResultIcon(task, data);
			out += '<div class="progress-bar status-'+icon.status+'" role="progressbar" '+
				   'style="width: '+step+'%" title="'+icon.status.toUpperCase()+
				   ' - '+tasks[ix].test_name+
				   (task.duration < 0 ? '' : ' - '+Math.round(task.duration/60)+'min')+'" >';
			if (ix == 0) {
				out += '<div class="progres-rule first">0&nbsp;min</div>';
			}
			out += '<div class="progres-rule other '+(ix == last_compleated ? 'last':'')+'">'+Math.round(progressDuration/60)+'&nbsp;min</div>';
		    out += '</div>';
		}
	}
	out += '</div>';
	return out;
}

function render_job_comment(comments) {
	var message = "";
	if (comments.length > 0) {
		message += '<div><strong>Comments ('+(comments.length)+') <a href="#" class="glyphicon glyphicon-chevron-down comentsSwitcher"></a></strong>';
		message += '<ul class="nopoints coments-list">';
		for(ix in comments) {
			var icon = getCommentIcon(comments[ix].action);
			message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
						comments[ix].created_date+'&nbsp;&nbsp;'+
						comments[ix].content+
						'&nbsp;&nbsp;('+comments[ix].username+')</li>';
		}
		message += '</ul></div>';
	}
	return message;
}

function rednder_job_detail_tab(data) {
	var message = "";
	var recipeWhiteboard = "";
	if(data.whiteboard) {
		recipeWhiteboard = ' - '+data.whiteboard;
	}
	message += '<h4>'+data.job_name+' '+recipeWhiteboard+' ('+data.job.date+')&nbsp;&nbsp;'+
			   '<a class="glyphicon glyphicon-link" href="/job/'+data.job.template+'" title="Job detail"></a>&nbsp;&nbsp;'+
			   '<a href="https://' + BEAKER_SERVER + '/recipes/'+data.uid+'" class="glyphicon glyphicon-briefcase" title="Link to Beaker"></a>'+
			   '</h4>';
	message += render_progressbar(data)
	message += render_job_comment(data.comments)
	/*
	if (data.reschduled.length > 0) {

		for(ix in data.reschduled) {
			icon = getCommentIcon("rescheduled-job-link");
			var jid = data.reschduled[ix].uid.replace(/J:/,'');
			message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
						data.reschduled[ix].date+'&nbsp;&nbsp;'+
						'This recipe is new version of previous recipe (<a href="https://' + BEAKER_SERVER + '/jobs/'+jid+'">'+
						data.reschduled[ix].uid+'</a>)</li>';
		}
		message += '</ul><br>';

	}
	*/

	message += '<strong class="tasksLabel">Tasks ...loading... </strong>';
	message += '<div class="btn-group filter-switch" data-toggle="buttons">'+
			   '<label class="btn btn-primary btn-xs active"><input type="radio" name="errors" checked>Errors</label>'+
			   '<label class="btn btn-primary btn-xs"><input type="radio" name="all">&nbsp;&nbsp;All&nbsp;&nbsp;</label>'+
			   '</div>';
	message += '<div class="tasks-list scrolling elastic">';
	message += '<table class="table table-striped" data-counttasks="0"><tbody>';
	message += "</tbody></table></div>";
	return message;
}

function render_tasklist(tasks) {
	message = "";
	$.each(tasks, function(i, task){
    	var result = "";
    	var icon = getTaskResultIcon(task, task.recipe);
    	if (icon) {
    		result = '<span class="glyphicon glyphicon-'+icon.icon+'" style="color: '+icon.color+'" title="'+icon.title+'"></span>';
    	}

        message += '<tr>';
        message += '<td>'+result+'</td>';
        message += '<td>'+task.test.name+'&nbsp&nbsp'+
                   '<a class="glyphicon glyphicon-link" href="'+task.test.get_absolute_url+'#'+task.uid+'" title="Test detail"></a>&nbsp;&nbsp;'+
                   '<a href="https://' + BEAKER_SERVER + '/recipes/'+task.recipe.uid.replace("R:", "")+'#task'+task.uid.replace("T:", "")+'" class="glyphicon glyphicon-briefcase" title="Link to Beaker"></a>';
		if (task.logfiles.length > 0) {
			for (var ix in task.logfiles) {
				if (task.logfiles[ix].endsWith('TESTOUT.log')) {
					message += '&nbsp;&nbsp;<a href="' + STORAGE_URL + task.logfiles[ix] +'" class="octicon octicon-file-text openInModalWindow" title="TESTOUT.log"></a>';
				}
			}
		}
        message += '</td><td>';
        if (task.test.owner) {
			var owner = getAuthor(task.test.owner)
			if (owner != null) {
            	message += '<a href="mailto:'+owner.email+'">'+owner.name+"</a>";
			}
        } else {
        	message += '&nbsp;';
        }
        message += '</td></tr>';
        if(task.comments.length > 0) {
			  for(ix in task.comments) {
			  	 message += '<tr>';
			  	 message += '<td>&nbsp</td>';
			  	 message += '<td><span class="glyphicon glyphicon-info-sign"></span>&nbsp;&nbsp;'+
			  	            task.comments[ix].created_date+'&nbsp;&nbsp;'+
			  	            task.comments[ix].content+'</td>';
			  	 message += '<td>'+task.comments[ix].username+'</td>';
			  	 message += '</tr>';
			  }
        }
    });
    return message;
}

function loadTasks(id, filter) {
	//var tabC = detailPanel.getTab(id);
	var errors = '';
	if (filter == 'errors') errors = '&results=3,4,10,9'; // WARN, FAIL, NEW
	$.getJSON('/api/v1/task/?recipe='+id+errors+'&limit=500&ordering=id', function(data){
		if (id == null) {
			id = data.results[0].recipe;
		}
		var tab = detailPanel.getTab(id)
		if (tab != null) {
			$(".tasks-list tbody", tab.content_elm).html(render_tasklist(data.results));
			$(".tasksLabel", tab.content_elm).html('Tasks ('+data.count+')');
			$(".scrolling", tab.content_elm).scrollTop();
			detailPanel.doElastic(tab.content_elm);
			// Open modal window with TESTOUT.log
			$('.openInModalWindow', tab.contet_elm).click(function(){
				openModalWindow('<iframe id="modalIframe" src="'+$(this).attr('href')+'" width="100%" height="500"></iframe>',
							    $(this).parent('td').text().trim()+' - TESTOUT.log');
				return false;
			});
		}
	});
}

function previewRecipe(id, synced) {
	$('.dashboard-jobs td').removeClass('hover');
	if (!isNumber(id)) {
		id = $(this).attr("data-id");
	}
	$(this).addClass('hover');
    if(id) {
        var fce = $.getJSON;
        if (synced == true) {
            fce = getSyncJSON
        }
        fce("/api/v1/recipe/"+id+"/", function(data) {
			if (data.previous == null && data.results !=null) {
				// This is situation, when we open detail via UID.
				if (data.results.length == 0) {
					return 0;
				}
				data = data.results[0];
				$('td[data-id="'+data.id+'"]').addClass('hover');
			}
			var tab = detailPanel.getTab(data.id);
			if (tab == null) {
				tab = detailPanel.getTab(0);
			}
			tab.open()
			loadTasks(data.id, 'errors')
			//var tres = .result
			//if (data.statusbyuser == 11 || data.statusbyuser == 'waived') tres=11;
            var icons = [];
			icons[icons.length] = getResultRecipeIcon(data)
      if (data.job.is_running) {
				icons.push({icon: 'star', title: "System is still runnig.", color: "gold"});
      }
			var head = 'R:'+data.uid.replace("R:", "");
			for (var ix in icons) {
				head += '&nbsp<span class="glyphicon glyphicon-'+icons[ix].icon+'" style="color:'+icons[ix].color+'" title="'+icons[ix].title+'"></span>'
			}
			tab.update({
				id: data.id,
				head: head,
				head_title: data.job_name+' - '+data.whiteboard+' ('+data.job.date+')',
				content: rednder_job_detail_tab(data),
				status: data.result,
				box_el: $(".dashboard-jobs td[data-id='"+data.id+"']")
			});
        });
    }
}


function saveDetailTab(){
	var tab = detailPanel.getTab($(this).attr("data-id"));
	if (tab != null && detailPanel.getIndexTab(tab) > 0) {
		tab.delete();
		previewRecipe.apply(this)
		return false;
	}
	if (tab != null && tab.data.id == "preview") {
		return false;
	}
	tab = detailPanel.getTab(0);
	detailPanel.createDefaultTab();
	tab.data.box_el.addClass('selected');
	tab.open();
	// Add link to recipe list
	var button = $('<div class="btn action-button"></div>');
	$('.recipe-list', detailPanel.elm).append(button);
	tab.data.button_el = button;
	// btn-'+info.color)
	button.bind('click', function() {
			$(this).data('detailTab').delete()
		  })
		  .data('detailTab', tab)
		  .attr('title', tab.data.head_title)
		  .css({'background-color': tab.data.box_el.css('background-color'),
		        'background-image': tab.data.box_el.css('background-image'),
		        'background-repeat': tab.data.box_el.css('background-repeat')})
		  .hover(function() {
			   events.runEvent('HOVER', $(this).data('detailTab'), 'IN');
		   }, function() {
			   events.runEvent('HOVER', $(this).data('detailTab'), 'OUT');
		   })
		  .html(tab.data.head);
	// Enable comment buttons, if some recipe is selected.
	$("button[data-action-field='action']", detailPanel.elm).removeAttr('disabled');
}

function onHoverRecipe() {
    $("td.field-value").filter(':not(.status-)')
		.mouseenter(previewRecipe)
		.click(saveDetailTab);
}

function onLoad() {
    onHoverRecipe();
    initPage();
    //onHoverRecipe();
}

$(document).ready(onLoad);
