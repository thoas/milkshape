package cc.milkshape.navigation.issue
{
    import cc.milkshape.navigation.generic.PrivateEventList;
    import cc.milkshape.navigation.generic.UIList;
    import cc.milkshape.navigation.generic.PluginsServiceList;
    import cc.milkshape.navigation.generic.cmd.LoadApplication;
    import cc.milkshape.framework.remoting.ProxyService;
    import cc.milkshape.navigation.issue.cmd.OnLoadIssuesUI;
    import cc.milkshape.navigation.issue.view.IssuesUI;

    import com.bourre.plugin.AbstractPlugin;

    import flash.display.Sprite;
    public class IssuesPlugin extends AbstractPlugin
    {
        private var _container:Sprite;

        public function IssuesPlugin(container:Sprite)
        {
            super();
            _container = container;
            ProxyService.getInstance().registerService(PluginsServiceList.ISSUE, new IssuePluginService(ProxyService.getInstance().gatewayURL)); 
            getController().pushCommandClass(PrivateEventList.onLoadIssuesUI, OnLoadIssuesUI);
            getController().pushCommandClass(PrivateEventList.loadApplication, LoadApplication);
            var issuesUI:IssuesUI = new IssuesUI(this, UIList.ISSUES, _container);
        }
    }
}