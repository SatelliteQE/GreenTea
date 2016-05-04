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
			$('.openInModalWindow', this.contet_elm).click(function(){
				openModalWindow('<iframe src="'+$(this).attr('href')+'" width="100%" height="500"></iframe>', $(this).html());
				return false;
			})
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
	if (uid.match(/^T:[0-9]+/) != null) {
		previewTask(uid);
	}
}

function render_task_detail_tab(data) {
    var message = "";
    var recipeWhiteboard = "";
    if(data.recipe.arch.name) {
        recipeWhiteboard += ' - '+data.recipe.arch.name;
    }
    var recipe_icon = getResultRecipeIcon(data.recipe);
    var task_icon = getTaskResultIcon(data)
	var status_icon = getTaskStatusIcon(data)
    message += '<h4>'+data.recipe.job_name+' '+recipeWhiteboard+' ('+data.recipe.job.date+')&nbsp;&nbsp;'+
       '<a class="glyphicon glyphicon-link" href="/jobs.html#R:'+data.recipe.uid+'" title="Job detail"></a>&nbsp;&nbsp;'+
       '<a href="https://' + BEAKER_SERVER + '/recipes/'+data.recipe.uid+'#'+data.uid+'" class="glyphicon glyphicon-briefcase" title="Link to Beaker"></a>'+
       '</h4>';
    message += '<table class="taskInfo">';
    message += '<tr><th>Test:</th><td><strong>'+data.test.name;
    if (data.test.repository_url.length > 0) {
        message += '&nbsp;&nbsp;<a href="'+data.test.repository_url+'" class="octicon octicon-mark-github"  target="_blank" title="The source code of the test"></a>';
    }
    if (data.test.detail_url.length > 0) {
        message += '&nbsp;&nbsp;<a href="'+data.test.detail_url+'" class="glyphicon glyphicon-list-alt"  target="_blank" title="Detail of the test"></a>';
    }
	message += '</strong></td></tr>';
	if (data.test.external_links != null && data.test.external_links.length > 0) {
		message += '<tr><th style="vertical-align: top">Test external information:</th><td>';
		var exlinks = data.test.external_links.split(';');
		for (var ix in exlinks) {
			message += '<a href="'+ exlinks[ix] +'">&nbsp;'+exlinks[ix]+'<span class="octicon octicon-link-external link-external"></span></a><br>';
		}
		message += '</td></tr>';
	}
    message += '<tr><th>Task / Recipe result:</th><td>'+
               '<span class="glyphicon glyphicon-'+task_icon.icon+'" style="color:'+task_icon.color+'" title="'+task_icon.title+'"></span>&nbsp;&nbsp;'+task_icon.status+'&nbsp;/&nbsp;&nbsp;'+
               '<span class="glyphicon glyphicon-'+recipe_icon.icon+'" style="color:'+recipe_icon.color+'" title="'+recipe_icon.title+'"></span>&nbsp;&nbsp;'+recipe_icon.status+'</td></tr>';
    message += '<tr><th>Status:</th><td>'+
			   '<span class="glyphicon glyphicon-'+status_icon.icon+'" style="color:'+status_icon.color+'" title="'+status_icon.title+'"></span>&nbsp;&nbsp;'+status_icon.status+'</td></tr>';
	if (data.logfiles.length > 0) {
		message += '<tr><th style="vertical-align: top">Logs:</th><td>';
		for (var ix in data.logfiles) {
			var name = data.logfiles[ix].substring(data.logfiles[ix].lastIndexOf('/')+1);
			message += '<a href="'+ STORAGE_URL + data.logfiles[ix] +'" class="glyphicon glyphicon-briefcase openInModalWindow">&nbsp;'+name+'</a><br>';
		}
		message += '</td></tr>';
	}
    message += '</table>';
    var sumComments = data.comments.length + data.recipe.comments.length;
    if (sumComments > 0) {
        message += '<strong>Comments ('+sumComments+'):</strong>';
        message += '<div class="comment-list scrolling elastic">'+
                   '<ul class="nopoints coments-list">';
        for(ix in data.comments) {
            var icon = getCommentIcon(data.comments[ix].action);
            message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
                       '<b>Task:</b>&nbsp;&nbsp;'+data.comments[ix].created_date+'&nbsp;&nbsp;'+
                        data.comments[ix].content+
                        '&nbsp;&nbsp;('+data.comments[ix].username+')</li>';
        }
        for(ix in data.recipe.comments) {
            var icon = getCommentIcon(data.recipe.comments[ix].action);
            message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
                       '<b>Recipe:</b>&nbsp;&nbsp;'+data.recipe.comments[ix].created_date+'&nbsp;&nbsp;'+
                        data.recipe.comments[ix].content+
                        '&nbsp;&nbsp;('+data.recipe.comments[ix].username+')</li>';
        }
        /*
        for(ix in data.reschduled) {
            icon = getCommentIcon("rescheduled-job-link");
            var jid = data.reschduled[ix].uid.replace(/J:/,'');
            message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
                        '<b>Recipe:</b>&nbsp;&nbsp;'+data.reschduled[ix].date+'&nbsp;&nbsp;'+
                        'This recipe is new version of previous recipe (<a href="https://' + BEAKER_SERVER + '/jobs/'+jid+'">'+
                        data.reschduled[ix].uid+'</a>)</li>';
        }
        */
        message += '</ul></div>';
    }
    return message;
}

function previewTask(id) {
	var api_url = "/api/v1/task/";
	$('.dashboard-tests td').removeClass('hover');
	if (!isNumber(id) && (id+"").match(/^T:[0-9]+/) != null) {
		// This is situation, when we open detail via UID.
		api_url += ("?uid="+id).replace('T:','');
		var sElm = $("td[id='"+id+"']");
		$('html, body').animate({
	        scrollTop: sElm.offset().top - 200
	    }, 2000);
	} else{
	    if (!isNumber(id)) {
	        id = $(this).attr("data-id");
	    }
		$(this).addClass('hover');
		api_url += id + "/";
	}
    if(id) {
        $.getJSON(api_url, function(data){
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

            var icons = [];
            icons[icons.length] = getTaskResultIcon(data);
            if (data.recipe.job.is_running) {
				icons.push({icon: 'star', title: "System is still runnig."});
            }
            /*
            if (data.reschduled.length > 0) {
				icons[icons.length] = {
					icon: 'refresh',
					title: "Job was "+data.reschduled.length+"-times rescheduled."
				};
            }
            */
            var head = 'T:'+data.uid;
			for (var ix in icons) {
				head += '&nbsp<span class="glyphicon glyphicon-'+icons[ix].icon+'" title="'+icons[ix].title+'"></span>'
			}
            tab.update({
				id: data.id,
				head: head,
				head_title: data.job_name+' - '+data.whiteboard+' ('+data.recipe.job.date+')',
                content: render_task_detail_tab(data),
				status: data.result,
				box_el: $(".dashboard-tests td[data-id='"+data.id+"']")
			});
        });
    }
}

function saveTaskPanel(){
    var tab = detailPanel.getTab(0);
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

function onHoverTask(){
    $("td.field-value").filter(':not(.status-)')
        .mouseenter(previewTask)
        .click(saveTaskPanel);
}

function setupAutoHeight(elm, h){
  elm.css({ height: h });
  elm.append("<a class='threedots'>show rest...</a>");
  $('.threedots', elm).click(
    function(){
      //elm.animate({ height: "auto" }, 250);
      elm.css({ height: "auto" });
      $('.threedots', elm).css({ display: "none" })
      return false;
    }
  )
}

function onLoad() {  
  onHoverTask();
  setupAutoHeight($("#byowner"), 300);
  setupAutoHeight($("#byrepo"), 150);
  setupAutoHeight($("#bygroup"), 150);
  initPage();
}

$(document).ready(onLoad);
