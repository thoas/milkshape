package cc.milkshape.navigation.issue{	import cc.milkshape.navigation.issue.cmd.OnLoadIssuesUI;	import cc.milkshape.navigation.generic.PrivateEventList;	import com.bourre.commands.FrontController;	public class IssuesFrontController extends FrontController 	{		private static var _oI:IssuesFrontController;		public static function getInstance():IssuesFrontController 		{			if (!_oI) _oI = new IssuesFrontController(new PrivateConstructorAccess());			return _oI;		}		public function IssuesFrontController(access:PrivateConstructorAccess)		{		}		public function init():void		{			pushCommandClass(PrivateEventList.onLoadIssuesUI, OnLoadIssuesUI);		}	}}internal class PrivateConstructorAccess {}