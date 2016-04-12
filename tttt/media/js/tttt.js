
function selectMenu() {
  $('#manMenu li').each(function(){
    if ($('a', this).attr('href') == location.pathname) {
      $(this).addClass('active');
    }
  });
}

function getCommentIcon(action) {
	if (action == 'mark waived') {
		return {icon: "hand-up", title: "This recipe was wavied."};
	} else if (action == "reshedule job") {
		return {icon: "refresh", title: "This job was rescheduled."};
	} else if (action == "return2beaker") {
		return {icon: "save", title: "This job was returned to beaker."};
	} else if (action == 'rescheduled-job-link') {
		return {icon: "refresh", title: "This recipe is new version of previous recipe.."};
	} else {
		return {icon: "info-sign", title: "Comment"};
	}
}

function DetailPanel(elm) {
	this.elm = elm;
	this.func = {
		getInfoAboutTask: null,
		deleteTask: null,
		hoverTab: null,
	};
	this.mouseEvents = {
		move: false,
		x: 0,
		y: 0,
		startY: 0,
		startX: 0
	};
	this.__mouseMove = function(event) {
		if (!detailPanel.mouseEvents.move) return;
		var diff = event.pageY - detailPanel.mouseEvents.y;
		detailPanel.elm.height(detailPanel.elm.height() - diff);
		detailPanel.mouseEvents.x = event.pageX;
		detailPanel.mouseEvents.y = event.pageY;
	};
	this.__mouseDown = function(event){
		if (detailPanel.elm.hasClass('small') ||
		    event.target.tagName == 'A') {
			event.stopImmediatePropagation();
			return;
		}
		detailPanel.mouseEvents.move = true;
		detailPanel.mouseEvents.x = event.pageX;
		detailPanel.mouseEvents.y = event.pageY;
		detailPanel.mouseEvents.startX = event.pageX;
		detailPanel.mouseEvents.startY = event.pageY;
	};
	this.__mouseUp = function(event) {
		if (!detailPanel.mouseEvents.move) return;
		detailPanel.mouseEvents.move = false;
		detailPanel.rememberDetail();
		detailPanel.doElastic($('#stab-detail', detailPanel.elm));
		detailPanel.changePaddingOfPage();
	};


	this.__hoverTabIn = function(event) {
          if (detailPanel.func.hoverTab != null) {
              detailPanel.func.hoverTab(event, 'IN');
          }
    };

    this.__hoverTabOut = function(event) {
          if (detailPanel.func.hoverTab != null) {
              detailPanel.func.hoverTab(event, 'OUT');
          }
    };

	this.__deleteDetailTab = function() {
		var link;
		if ($(this).hasClass('tab-detail-close')) {
			link = $(this).parent();
		} else {
			link = $(".tab-detail-header a[href='"+$(this).attr('data-href')+"']", detailPanel.elm);
		}
		if (detailPanel.func.deleteTask) {
			detailPanel.func.deleteTask(link);
		}
		$('.tab-detail-content '+link.attr('href'), detailPanel.elm).remove();
		$(".recipe-list div[data-href='"+link.attr('href')+"']").remove();
		if(link.parent().hasClass('active')) {
		    $(".tab-detail-header li:first a ").tab('show');
		}
		link.parent().remove();
	};

	this.__tabOpen = function(e){
       detailPanel.doElastic($($(e.target).attr('href'), detailPanel.elm));
    };

	this.changePaddingOfPage = function() {
		$('body').css({paddingBottom: px(detailPanel.elm.height())});
	};

	this.__changeRecipe = function(event) {
		var len = $(this).children('div').length;
		// This event is runned before removing of element.
		if (event.type == 'DOMNodeRemoved') {
			len = len - 1;
		}
		var buttons = $('.action-panel button', detailPanel.elm);
		if (len == 0) {
			buttons.prop('disabled', true);
		} else {
			buttons.prop('disabled', false);
		}
	};

	this.rememberDetail = function() {
		$.cookie('detailHidden', (detailPanel.elm.hasClass('small')?1:0), { expires: 365 });
		$.cookie('detailHeight', detailPanel.elm.height(), { expires: 365 });
	};

	this.isHidden = function() {
	     return this.elm.hasClass('small');
	};

	this.switchDisplay = function() {
	    detailPanel.elm.toggleClass('small');
        $(this).toggleClass('glyphicon-chevron-down')
               .toggleClass('glyphicon-chevron-up');
        detailPanel.rememberDetail();
        detailPanel.changePaddingOfPage();
	};

	this.doElastic = function(parent) {
		$('.elastic', parent).each(function(){
			var dp = $(this).closest('.panel-detail');
			var hh = $(this).offset().top - dp.offset().top;
			var height = Math.round(dp.height() - hh);
			if (height < 40) {
				height = 40;
			}
			$(this).height(height);
		});
	};

	this.updateDetailTab = function(data, tab) {
		var name = data.name.trim();
		var sname = name.replace(/:/g,'-');
		var line = name;
		var preview = false;
		// Tab
		if (data.icons) {
			for (ix in data.icons) {
				var titile = "";
				var ico = data.icons[ix];
				if (isObject(ico)) {
					title = ico.title;
					ico = ico.icon;
				}
				line += '&nbsp<span class="glyphicon glyphicon-'+ico+'" title="'+title+'"></span>';
			}
		}
		if (!tab) {
			tab = $('.tab-detail-header > li:first > a', this.elm);
			preview = true;
		}
		var oldHref = tab.attr('href');
		// Panel
		var panel = $('.tab-detail-content > '+oldHref, this.elm)
		    .attr('data-name', name)
		    .html(data.html);
		this.doElastic(panel);
		// Tab
		tab.html(line)
		   .attr('title', data.title)
		   .attr('data-status', data.status)
		   .attr('data-name', name);
        $('.tab-detail-header', this.elm).scrollTop(0);
		if(!preview) {
			tab.attr('href', '#tab-detail-'+sname)
			   .append('<span class="glyphicon glyphicon-remove tab-detail-close"></span>')
			   .on('shown.bs.tab', this.__tabOpen);
			panel.attr('id', 'tab-detail-'+sname);
			$('.tab-detail-close', tab).bind('click', this.__deleteDetailTab);
			// Button
			var info = this.func.getInfoAboutTask(data.status);
			var button = $('.recipe-list div[data-href="'+oldHref+'"]', this.elm);
			if (button.length == 0) {
				button = $('<div></div>');
				$('.recipe-list', this.elm).append(button);
				button.bind('click', this.__deleteDetailTab);
			}
			button.attr('class', 'btn btn-'+info.color)
			      .attr('title', data.title)
			      .attr('data-href', '#tab-detail-'+sname)
			      .attr('data-name', name)
			      .hover(this.__hoverTabIn, this.__hoverTabOut)
			      .html(line);
		} else {
			tab.tab('show');
		}
		return panel;
	};

	this.createNewDetailTab = function(ix) {
		// Add new blank tab
		var name = '';
		var sname = 'empty';
		var line = 'Preview';
		// Tab
		if (!ix) ix = 0;
		ix = Math.min(ix, $('.tab-detail-header li', this.elm).length);
		var newTab = $('<li><a href="#tab-detail-'+sname+'" '+
		                      'data-toggle="tab" '+
		                      'data-name="'+name+'">'+line+'</a></li>');
		if (ix > 1) {
		    console.log($('.tab-detail-header li:eq('+ix+')', this.elm));
			newTab.insertBefore($('.tab-detail-header li:eq('+ix+')', this.elm));
		} else {
			$('.tab-detail-header', this.elm).append(newTab);
		}
		$('.tab-detail-content', this.elm)
		    .append('<div class="tab-pane" id="tab-detail-'+sname+'"></div>');
		var link = newTab.children('a');
		link.hover(this.__hoverTabIn, this.__hoverTabOut);
		return link;
	};

	this.openDetailTab = function(num) {
		if (isNumber(num)) {
			num = $('.tab-detail-header li:eq('+num+') a', this.elm);
		}
		num.tab('show');
	};

	this.init = function() {
		$('.header', this.elm)
		.bind('mousedown',this.__mouseDown)
		.bind('mousemove', this.__mouseMove);
		$('.header .visibilitySwitcher', this.elm)
		    .bind('click', this.switchDisplay);
		$('body').bind('mouseup', this.__mouseUp);
		$('.recipe-list', this.elm)
		    .bind('DOMNodeInserted DOMNodeRemoved', this.__changeRecipe);
		this.doElastic($('#stab-detail', this.elm));
		this.changePaddingOfPage();
		$('.tab-detail-header a[data-toggle="tab"]', this.elm).hover(this.__hoverTabIn, this.__hoverTabOut);
	};
	return this;
};

function confirmSubmit() {
	this.__clickFrom = function(event) {
		if (!$(event.target).is('*[data-modalQuestion]')) return;
		$(this).data('clicked',$(event.target));
	};

	this.__submitFrom = function(event) {
		var link = $(this).data('clicked');
		if(link && link.is('[data-modalQuestion]')) {
			var modalBox = $('#panel-detailModal');
			var head = "";
			if(link.is('*[data-modalIcon]')) {
				head += '<span class="glyphicon '+link.attr('data-modalIcon')+'"></span>&nbsp;';
			}
			if(link.is('*[data-modalTitle]')) {
				head += link.attr('data-modalTitle');
			}
			if (head.length > 0) {
				$('.modal-header h4', modalBox).html(head);
			}
			$('.modal-body', modalBox).html(link.attr('data-modalQuestion'));
			$('.modal-footer button[data-return="1"]', modalBox).data('form', this)
				.click(function(){ $(this).data('form').submit(); });
			modalBox.modal({show: true});
			return false;
		}
	};

	// This is events for confirm box
	$("form").click(this.__clickFrom).submit(this.__submitFrom);
}

function actionSubmit() {
	this.__clickFrom = function(event) {
		if (!$(event.target).is('[data-action-field]')) return;
		$(this).data('clicked2', $(event.target));
	};

	this.__submitFrom = function(event) {
		var link = $(this).data('clicked2');
		if(link && link.is('[data-action-field]') && link.is('[data-action-value]')) {
			var field = link.attr('data-action-field');
			var value = link.attr('data-action-value');
			if (field.indexOf('.') < 0 && field.indexOf('#') < 0) {
				field = 'input[name="'+field+'"]';
			}
			$(field).val(value);
		}
	};

	// This is events for set parameters from submiter
	$("form").click(this.__clickFrom).submit(this.__submitFrom);
}


detailPanel = null;

function onLoad() {
  selectMenu();
  detailPanel = new DetailPanel($('.panel-detail'));
  detailPanel.init();
  confirmSubmit();
  actionSubmit();
}

$(document).ready(onLoad);
