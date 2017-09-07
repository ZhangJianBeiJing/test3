package observerModel;

/*********************   
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 09:53
 *
 *********************/

import java.util.Observable;
import java.util.Observer;

/**
 * 观察者
 * 实现java.util.Observer接口
 */
public class NumObserver implements Observer{
    /**
     * This method is called whenever the observed object is changed. An
     * application calls an <tt>Observable</tt> object's
     * <code>notifyObservers</code> method to have all the object's
     * observers notified of the change.
     *
     * @param o   the observable object.
     * @param arg an argument passed to the <code>notifyObservers</code>
     */
    @Override
    public void update(Observable o, Object arg) {
        NumObservable numObserver=(NumObservable) o;
        System.out.println("data has changed to:"+((NumObservable) o).getData());
    }
}
