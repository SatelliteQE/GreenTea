
function selectMenu() {
  $('#manMenu li').each(function(){
    if ($('a', this).attr('href') == location.pathname) {
      $(this).addClass('active');
    }
  });
}

var events = {
    __events: {},
    addEvent: function(ev, fce) {
        if (this.__events[ev] == null) {
            this.__events[ev] = [];
        }
        this.__events[ev].push(fce)
    },
    runEvent: function() {
        arg = $.makeArray(arguments);
        var ev = arg.shift();
        if (isArray(this.__events[ev])) {
            var obj = arg.shift();
            for(var iLoop=0; iLoop < this.__events[ev].length; iLoop++) {
                this.__events[ev][iLoop].apply(obj, arg);
            }
        }
    }
}

function DetailTab(data) {
    this.head_elm = null;
    this.content_elm = null;
    this.parent_elm = data.detailPanel.elm;
    this.data = $.extend({}, data)
    /*
    {
      detailPanel: null,
      id: null,
      content: null
      head: null,
      head_title: ""
    }
    */

    this.__init__ = function() {
        var id = this.data.id;
        // Content
        this.content_elm = $('<div class="tab-panel" id="tab-detail-'+id+'">'+
                             this.data.content+'</div>')
        $('.tab-detail-content', this.parent_elm).append(this.content_elm);
        this.content_elm.data('detailTab', this);

        // Add header
        var newTab = $('<li><a href="#tab-detail-'+id+'" '+
                              'id="tab-head-'+id+'" '+
		                      'data-toggle="tab" '+
                              'title="'+this.data.head_title+'">'+this.data.head+'</a>'+
                              '<span class="glyphicon glyphicon-remove tab-detail-close"></span></li>');
        $('.tab-detail-header', this.parent_elm).prepend(newTab);
        $('.tab-detail-close', newTab).bind('click', function(){
            $(this).prevAll('a').data('detailTab').delete();
        });
        this.head_elm = $('.tab-detail-header a#tab-head-'+id)
        this.head_elm.data('detailTab', this);
        this.head_elm.bind('click', function() {
            $(this).data('detailTab').open();
        }).hover(function() {
             events.runEvent('HOVER', $(this).data('detailTab'), 'IN');
         }, function() {
             events.runEvent('HOVER', $(this).data('detailTab'), 'OUT');
         });
        this.data.detailPanel.registerTab(this)
        events.runEvent('CREATE', this)
    }

    this.update = function(ndata) {
        events.runEvent('UPDATE', this, ndata)
        for (key in ndata) {
            if (key == 'id') {
                if(ndata.id != this.data.id) {
                    this.data.id = ndata.id;
                    this.content_elm.attr('id', 'tab-detail-'+ndata.id);
                    this.head_elm.attr('id', 'tab-head-'+ndata.id)
                                 .attr('href', '#tab-detail-'+ndata.id);
                }
            } else if (key == 'content') {
                this.content_elm.html(ndata.content);
                this.data.content = ndata.content;
            } else if (key == 'head') {
                this.head_elm.html(ndata.head);
                this.data.head = ndata.head;
            } else if (key == 'head_title') {
                this.head_elm.attr('title', ndata.head_title);
                this.data.head_title = ndata.head_title;
            } else {
                this.data[key] = ndata[key];
            }
        }
        events.runEvent('UPDATE', this)
    }


    this.open = function() {
        this.content_elm.parent('div').children().removeClass('active');
        this.content_elm.addClass('active');
        this.data.detailPanel.doElastic(this.content_elm);
        this.head_elm.parents('ul').children().removeClass('active');
        this.head_elm.parent('li').addClass('active');
        events.runEvent('OPEN', this)
    }

    this.delete = function() {
		events.runEvent('DELETE', this)
		this.head_elm.parent('li').remove();
        this.head_elm = null;
		this.content_elm.remove();
        this.content_elm = null;
        this.data.detailPanel.unregisterTab(this);
        console.debug("Tab '"+this.data.id+"' was deleted.")
	};

    this.__init__();
}

function DetailPanel(elm) {
	this.elm = elm;
    this.tabs = [];
    /*
	this.func = {
		getInfoAboutTask: null,
		deleteTask: null,
		hoverTab: null,
	};*/
    this.default_tab = {
        id:'preview',
        content: '<br><p><strong>Fast preview:</strong> Move cursor on the job box and here, you can see informations about job.</p>        <p><strong>Keep detail of job:</strong> If you want to preserve informations about job here, click on the job box.</p>',
        head: 'Preview'
    }
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

    this.registerTab = function(tab) {
        this.tabs.unshift(tab);
    };

    this.unregisterTab = function(tab) {
        this.tabs.removeItem(this.getIndexTab(tab));
    };

    this.getIndexTab = function(tab) {
        return this.tabs.indexOf(tab);
    }

    this.getTab = function(index) {
        var ll = this.tabs.length;
        if (isNumber(index) && index < ll) {
            return this.tabs[index];
        } else if (isObject(index)) {
            for(var iLoop = 0; iLoop < ll; iLoop++) {
                var res = 1;
                for (x in index) {
                    var reg = RegExp(index[x]);
                    if (!reg.test(this.tabs[iLoop].head_elm.attr(x))) {
                        res = 0;
                    }
                }
                if (res == 1) {
                    return this.tabs[iLoop]
                }
            }
        } else {
            for(var iLoop = 0; iLoop < ll; iLoop++) {
                if (this.tabs[iLoop].data.id == index) {
                    return this.tabs[iLoop];
                }
            }
        }
        console.debug("This tab '"+index+"' does not found.");
    };

    this.openTab = function(tab) {
        if (isNumber(tab)) {
            tab = this.getTab(tab);
        }
        tab.open();
	};

    this.createDefaultTab = function() {
        var def = {detailPanel: this};
        var tab = new DetailTab($.extend(def, this.default_tab));
        this.openTab(tab);
    }

    // Method set bottom padding of page, for show bottom of page
	this.changePaddingOfPage = function() {
	 	$('body').css({paddingBottom: px(detailPanel.elm.height())});
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

    // it changes height of all .elastic elements for current size of detail panel
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

	this.init = function() {
		$('.header', this.elm)
		.bind('mousedown',this.__mouseDown)
		.bind('mousemove', this.__mouseMove);
		$('.header .visibilitySwitcher', this.elm)
		    .bind('click', this.switchDisplay);
		$('body').bind('mouseup', this.__mouseUp);
		this.doElastic($('#stab-detail', this.elm));
		this.changePaddingOfPage();
        this.createDefaultTab();
	};
	return this;
};
// ---------------------------END detailPanel ---------------------------------


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
