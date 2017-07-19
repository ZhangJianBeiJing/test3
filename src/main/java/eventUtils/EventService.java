package eventUtils;

import java.util.*;
import java.util.concurrent.*;

/**
 *
 *事件服务类 单例模式
 *
 */
public class EventService {
    //事件队列
    private ConcurrentLinkedQueue<Event> events = new ConcurrentLinkedQueue<Event>();
    //事件被消费后的回调函数列表 key: Event.id value:EventConsumedCallback
    private ConcurrentHashMap<String, IEventConsumedCallback> eventCallbacks = new ConcurrentHashMap<String, IEventConsumedCallback>();
    //事件处理器列表 key:Event.type value:list<EventHandler>
    private ConcurrentHashMap<String, List<IEventHandler>>    eventHandlers  = new ConcurrentHashMap<String, List<IEventHandler>>();
    //线程池
    private ThreadPoolExecutor threadPool = new ThreadPoolExecutor(4, 10, 5000, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<Runnable>());              ;
    //事件结束标识符
    private boolean stopped = false;
    //事件消费线程类
    private Thread eventsConsumeThread;
    //事件服务类
    private static EventService instance;

    /**
     * 构造器私有化
     */
    private EventService() {
        //TODO
    }
    /**
     * 外部入口
     */
    public static EventService getInstance(){
        if(instance==null){
            instance=new EventService();
        }
        return instance;
    }

    /**
     * @author ligh4 2015年3月18日下午3:12:30
     * @param cfg properties like "handlerclassname = eventtype1,eventtype2"
     */
    synchronized public static void init(Properties cfg) {
        instance=EventService.getInstance();
        //加载事件处理器
        instance.loadHandlers(cfg);
        instance.eventsConsumeThread = new Thread(new Runnable() {
            @Override
            public void run() {
                instance.consumeEvents();
            }
        });
        //启动线程
        instance.eventsConsumeThread.start();
    }
    //关闭
    synchronized public static void stop() {
        instance.stopped = true;
        instance.threadPool.shutdown();
    }

    /**
     * 添加事件
     * @param event
     */
    synchronized public static void fireEvent(Event event) {

        instance.events.add(event);
    }

    /**
     * 添加事件及事件的回调类
     * @param event
     * @param callback
     */
    synchronized public static void fireEvent(Event event, IEventConsumedCallback callback) {
        instance.eventCallbacks.put(event.getId(), callback);
        fireEvent(event);
    }

    /**
     * 注册事件处理器
     *  1
     * @param eventType
     * @param handler
     */
    synchronized public static void registerEventHandler(String eventType, IEventHandler handler) {
        List<IEventHandler> handlers = instance.eventHandlers.get(eventType);
        if (handlers == null) {
            handlers = new ArrayList<IEventHandler>();
            instance.eventHandlers.put(eventType, handlers);
        }

        handlers = instance.eventHandlers.get(eventType);
        handlers.add(handler);
    }

    /**
     * 消费事件
     */
    synchronized private void consumeEvents() {
        //判断开关
        while (!stopped) {
            //有事件
            if (!events.isEmpty()) {
                Event event = events.poll();
                Object result = null;
                //获取事件处理器列表
                List<IEventHandler> handlers = eventHandlers.get(event.getType());
                //处理事件
                for (IEventHandler handler : handlers) {
                    result = handler.onEvent(event);
                }
                //获取回调接口实现类
                IEventConsumedCallback callback = eventCallbacks.get(event.getId());
                if (callback != null) {
                    //移除回调类
                    eventCallbacks.remove(event.getId());
                    //执行回调方法
                    callback.onEventFinished(event, result);
                }
            }
        }
    }

    /**
     * 加载处理器
     *  1 读取属性文件
     *  2 实例化事件处理器
     *  3 注册事件处理器
     * @param cfg
     */
    private void loadHandlers(Properties cfg) {
        if (cfg == null) {
            return;
        }
        //keys
        Enumeration<Object> keys = cfg.keys();
        while (keys.hasMoreElements()) {
            //property.key
            String fullClassName = keys.nextElement().toString();
            //property.value
            String eventTypes = cfg.getProperty(fullClassName);
            Object instance = null;
            try {
                //实例化事件处理器
                instance = Class.forName(fullClassName).newInstance();
            } catch (Exception e) {
                e.printStackTrace();
            }

            if (instance != null) {
                //分割字符串
                StringTokenizer tokenizer = new StringTokenizer(eventTypes, ",");
                while (tokenizer.hasMoreTokens()) {
                    String eventType = tokenizer.nextToken();
                    eventType = eventType.trim();
                    registerEventHandler(eventType, (IEventHandler) instance);

                }
            }

        }
    }

}
