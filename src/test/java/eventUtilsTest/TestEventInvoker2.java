package eventUtilsTest;

import eventUtils.Event;
import eventUtils.EventService;
import eventUtils.IEventConsumedCallback;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Date;
import java.util.InvalidPropertiesFormatException;
import java.util.Properties;
//import com.xxxx.fengine.

public class TestEventInvoker2 implements IEventConsumedCallback {
    /**
     * 回调方法实现
     *
     * @param event
     * @param result
     */
    @Override
    public void onEventFinished(Event event, Object result) {
        System.out.println("Event callback " + event.getId() + " at "
                + ((Date) result).toLocaleString());
    }
    public static void main(String args[]) throws Exception {

        String config_file = "/handlers.properties";
        FileInputStream inputStream = null;
        Properties props = new Properties();
        try {
            //inputStream = new FileInputStream(config_file);
            props.load(TestEventInvoker2.class.getResourceAsStream(config_file));

        } catch (InvalidPropertiesFormatException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (inputStream != null) {
                    inputStream.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        EventService.init(props);

        for (int i = 0; i < 10; i++) {
            TestEvent event = new TestEvent();
            EventService.fireEvent(event,new TestEventInvoker2());
            //EventService.fireEvent(event,new TestEventInvoker1());
        }

        Thread.sleep(5000);

        EventService.stop();
    }
}
