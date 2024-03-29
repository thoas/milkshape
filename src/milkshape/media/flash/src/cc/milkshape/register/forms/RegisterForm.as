package cc.milkshape.register.forms
{	
	import cc.milkshape.framework.buttons.SmallButton;
	import cc.milkshape.framework.forms.Formable;
	import cc.milkshape.framework.forms.fields.Checkbox;
	import cc.milkshape.framework.forms.fields.LabelInput;
	import cc.milkshape.register.RegisterController;
	import cc.milkshape.user.events.LoginEvent;
	
	import com.reintroducing.ui.AxisScroller;
	
	import fl.motion.easing.Sine;
	
	import flash.events.Event;
	import flash.events.MouseEvent;

	public class RegisterForm extends RegisterClp implements Formable
	{
		private var _registerController:RegisterController;
		private var _username:LabelInput;
		private var _email:LabelInput;
		private var _password:LabelInput;
		private var _confirmPassword:LabelInput;
		private var _invitationKey:LabelInput;
		private var _checkTerms:Checkbox;
		private var _submit:SmallButton;
		public function RegisterForm(registerController:RegisterController)
		{
			_registerController = registerController;
			_registerController.addEventListener(LoginEvent.ERROR, _error);
			_username = new LabelInput('USERNAME *');
			username.addChild(_username);
			_email = new LabelInput('EMAIL *');
			email.addChild(_email);
			_password = new LabelInput('PASSWORD *', true);
			password.addChild(_password);
			_confirmPassword = new LabelInput('CONFIRMATION *', true);
			confirmPassword.addChild(_confirmPassword);
			
			_checkTerms = new Checkbox("I've read and I accept the terms of use");
			checkTerms.addChild(_checkTerms);
			
			_submit = new SmallButton('I CONFIRM MY REGISTRATION', new PlusItem());
			submit.addChild(_submit);
			
			_submit.addEventListener(MouseEvent.CLICK, _submitHandler);
			
			addEventListener(Event.ADDED_TO_STAGE, _handlerAddedToStage);
		}
		
		private function _handlerAddedToStage(e:Event):void
		{
			var optionalObj:Object = {
				scrollType: "easing", 
				isTrackClickable: true, 
				continuousScroll: false,
				easeFunc: Sine.easeOut, 
				duration: .25,
				scaleScroller: true,
				autoHideControls: true
			};
			
			var scrollItems:ScrollItemsClp = new ScrollItemsClp();
			scrollItems.track.height = scrollArea.bg.height - 2;
			scrollArea.scroll.addChild(scrollItems);
			new AxisScroller(stage, scrollArea, scrollItems.scroller, scrollArea.content, scrollItems.track, scrollArea.mask, "y", optionalObj);
		
		}
		
		private function _submitHandler(e:MouseEvent):void
		{
			_registerController.signup(_username.text, _email.text, _password.text, _confirmPassword.text, ticket.text);
		}
		
		public function values():Object
		{
			return {
				'username': _username.text,
				'email': _email.text,
				'password': _password.text,
				'confirmPassword': _confirmPassword.text,
				'invitationKey': ticket.text
			};
		}
		
		public function reset():void
		{
			_username.blur();
			_password.blur();
			_confirmPassword.blur();
			_invitationKey.blur();
		}
		
		private function _error(e:LoginEvent):void
		{
			errorArea.text = '';
			for each(var error:String in e.result)
				errorArea.text += error + "\n";
		}
	}
}