package eventUtilsTest;

import eventUtils.Event;
import eventUtils.EventService;
import eventUtils.IEventConsumedCallback;

import java.util.Date;


public class TestEventInvoker implements IEventConsumedCallback {

    @Override
    public void onEventFinished(Event event, Object result) {
        System.out.println("Event callback " + event.getId() + " at "
                + ((Date) result).toLocaleString());

    }

    public static void main(String args[]) throws Exception {

        EventService.init(null);

        EventService.registerEventHandler(TestEvent.class.getSimpleName(), new TestEventHandler());

        for (int i = 0; i < 10; i++) {
            TestEvent event = new TestEvent();
            EventService.fireEvent(event, new TestEventInvoker());
        }

        Thread.sleep(5000);

        EventService.stop();
    }
}
