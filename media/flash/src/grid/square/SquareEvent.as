package grid.square
{
	import flash.events.Event;
	import grid.square.Square;
	
	public class SquareEvent extends Event
	{
		public static const SQUARE_CREATION:String = 'SQUARE_CREATION';
		public static const SQUARE_FOCUS:String = 'SQUARE_FOCUS';
		public static const SQUARE_OVER:String = 'SQUARE_OVER';
		private var _square:Square;
		
		public function SquareEvent(eventType:String, square:Square):void
		{
			super(eventType);
			_square = square;
		}

		public function get square():Square { return _square }
	}
}