package eventUtils;

/**
 * 事件类
 */
public class Event {
    private String id;
    private String type;
    private Object param;

    public Event(String type) {
        this.id = IDGenerator.gen();
        this.type = type;
    }

    public Event(String type, Object param) {
        this.id = IDGenerator.gen();
        this.type = type;
        this.param = param;
    }

    public String getId() {
        return id;
    }

    public String getType() {
        return type;
    }

    public Object getParam() {
        return param;
    }
}
