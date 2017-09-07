package observerModelTest;

import observerModel.NumObservable;
import observerModel.NumObserver;
import org.junit.Test;

/*********************
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 09:56
 *
 *********************/

/**
 * 测试类
 */
public class TestObserver {
    @Test
    public void testObservableModel(){
        //被观察者
        NumObservable numObservable=new NumObservable();
        //观察者
        NumObserver observer=new NumObserver();
        //将观察者添加到被观察者的观察者列表中
        numObservable.addObserver(observer);
        //改变数值
        numObservable.setData(100);
        numObservable.setData(200);
        numObservable.setData(300);
    }
}
