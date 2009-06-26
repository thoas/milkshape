﻿package{	import cc.milkshape.main.*;	import cc.milkshape.framework.Application;	import cc.milkshape.preloader.PreloaderKb;	import cc.milkshape.preloader.events.PreloaderEvent;	import cc.milkshape.user.Login;	import cc.milkshape.utils.Calcul;	import cc.milkshape.utils.MilkshapeMenu;	import cc.milkshape.utils.TableLine;	import cc.milkshape.utils.Constance;		import flash.display.Shape;	import flash.display.Sprite;	import flash.display.StageAlign;	import flash.display.StageScaleMode;	import flash.events.Event;	import flash.geom.ColorTransform;		import nl.demonsters.debugger.MonsterDebugger;

	[SWF(width='960', height='600', frameRate='31', backgroundColor='#191919')]		public class Main extends Application	{		private static var _instance:Main = null;		private const BAR_BG_COLOR:int = 0x0a0a0a;		private var _equalizer:Equalizer;		private var _menu:Menu;		private var _subMenu:SubMenu;		private var _login:Login;		private var _logo:Logo;		private var _fullscreen:Fullscreen;		private var _pageContainer:PreloaderKb;		private var _bottomBar:Shape;		private var _topBar:Shape;		private var _background:TableLine;				public function Main():void {			if(_instance != null) 				throw new Error("Cannot instance this class a second time, use getInstance instead.");			_instance = this;			var debugger:MonsterDebugger = new MonsterDebugger(this);			addEventListener(Event.ADDED_TO_STAGE, _handlerAddedToStage);		}				public static function getInstance():Main {			if(_instance == null)				new Main();			return _instance;		}				private function _handlerAddedToStage(e:Event):void		{			var mct:MilkshapeMenu = new MilkshapeMenu();// Menu contextuel personnalisé			contextMenu = mct.cm;						stage.align = StageAlign.TOP_LEFT;        	stage.scaleMode = StageScaleMode.NO_SCALE;        	stage.addEventListener(Event.RESIZE, _resize);        	        				_menu = new Menu(new Array(				{label: 'home', slug: 'home', url: Constance.HOME_SWF, background: true},				{label: 'about', slug: 'issue', url: Constance.ISSUE_SWF, background: false, params: {slug: '5x5'}},				{label: 'issues', slug: 'issues', url: Constance.ISSUES_SWF, background: true},				{label: 'artists', slug: 'artists', url: Constance.ARTISTS_SWF, background: true},				{label: 'contact', slug: 'contact', url: Constance.CONTACT_SWF, background: true}			));			_menu.addEventListener(PreloaderEvent.LOAD, loadSwf);						_subMenu = new SubMenu();			_subMenu.addEventListener(PreloaderEvent.INFO, loadSwf);						_fullscreen = new Fullscreen();						_equalizer = new Equalizer();						_login = new Login();						_logo = new Logo();						_bottomBar = new Shape();			_bottomBar.graphics.beginFill(BAR_BG_COLOR);			_bottomBar.graphics.drawRect(0, 0, stage.stageWidth, 33);			_bottomBar.graphics.endFill();						_topBar = new Shape();			_topBar.graphics.beginFill(BAR_BG_COLOR);			_topBar.graphics.drawRect(0, 0, stage.stageWidth, 60);			_topBar.graphics.endFill();						var errorArea:ErrorArea = new ErrorArea();						_pageContainer = new PreloaderKb();						_background = new TableLine(stage.stageWidth*2, stage.stageHeight*2, 100, 100, 0x202020);            // On colore les éléments du main            var mainColorTransform:ColorTransform = new ColorTransform();			mainColorTransform.color = 0xffdd00;			_logo.transform.colorTransform = mainColorTransform;			mainColorTransform.color = 0x999999;			_fullscreen.transform.colorTransform = mainColorTransform;			_equalizer.transform.colorTransform = mainColorTransform;			addChild(_pageContainer);			addChild(_bottomBar);			addChild(_topBar);			addChild(_menu);			addChild(_subMenu);			addChild(_login);			addChild(_logo);			addChild(_fullscreen);			addChild(_equalizer);			addChild(errorArea);						_itemsDisposition();						loadSwf(new PreloaderEvent(PreloaderEvent.LOAD, _menu.getMenuButton('home').option));		}				public function loadSwf(e:PreloaderEvent):void		{			if(e.option.background)				addChildAt(_background, 0);			else if(contains(_background))				removeChild(_background);								try {				_pageContainer.unloadMedia();			} catch(e:Error) {				trace(e.message);			}						try {				_pageContainer.params = e.option.params;				_pageContainer.loadMedia(e.option.url);			} catch(e:Error){				trace(e.message);			}		}				private function _itemsDisposition():void		{			ErrorArea.getInstance().x = 610;			ErrorArea.getInstance().y = 24;			_pageContainer.y = 60;			_background.x = -50;			_menu.x = 37;			_logo.x = 37;			_logo.y = 12;			_login.x = 275;			_login.y = 24;			_fullscreen.y = 12;			_equalizer.y = _fullscreen.y + 20;			_resize();		}				private function _resize(e:Event = null):void		{			_topBar.width = stage.stageWidth;						_bottomBar.y = stage.stageHeight - 33;			_bottomBar.width = stage.stageWidth;							_fullscreen.x = stage.stageWidth - 27;			_equalizer.x = _fullscreen.x;			_menu.y = stage.stageHeight - 21;						_subMenu.y = stage.stageHeight - 23;			_subMenu.x = stage.stageWidth - 70;		}	}}