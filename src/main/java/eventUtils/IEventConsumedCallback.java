package eventUtils;

/**
 * 回调接口
 * @author ligh4 2015年3月16日下午4:34:04
 */
public interface IEventConsumedCallback {
    /**
     * 事件结束
     * @param event
     * @param result
     */
    public void onEventFinished(Event event, Object result);
}
