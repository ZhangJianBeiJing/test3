package observerModel;

/*********************   
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 09:46
 *
 *********************/

/**
 * 被观察者
 * - 继承java.util.Observable
 *
 * - 被观察者手动调用setChanged()和notifyObservers()方法后，就会自动通知
 *   被观察者的观察者列表中的所有观察者执行update()方法
 *
 * - 只有先调用setChanged()之后，notifyObservers()方法才会去调用update()方法
 */
public class NumObservable extends java.util.Observable{
    private int data;

    public void setData(int data){
        this.data=data;
        this.setChanged();
        //通知观察者
        this.notifyObservers(data);
    }
    public int getData(){
        return this.data;
    }
    public String toString(){
        return String.valueOf(this.data);
    }
}
