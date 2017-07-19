package eventUtilsTest;


import eventUtils.Event;
import eventUtils.IEventHandler;

import java.util.Date;

public class TestEventHandler implements IEventHandler {
    @Override
    public Object onEvent(Event event) {
        System.out.println("On event  " + event.getId() + " Type:" + event.getType());
        return new Date();
    }
}
