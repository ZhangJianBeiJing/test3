package junitTest; /*********************
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 17:32
 *
 *********************/

import org.junit.FixMethodOrder;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.Timeout;
import org.junit.runners.MethodSorters;

/**
 * 超时测试
 * 注解：Timeout @Rule
 * 描述：
 * - Timeout可作用在测试方法的@Test注解上，作为参数，指定单个测试方法的超时时间；
 * - @Rule作用在测试类的Timeout类型的属性上，作为测试类的全部测试方法的统一超时规则，只要有一个测试方法超时，便抛出异常，测试便失败；
 */
@FixMethodOrder(MethodSorters.DEFAULT)
public class JUnitTimeoutTest {

    /**
     * 设定统一超时规则
     */
    @Rule
    public Timeout timeout=new Timeout(5000);

    @Test(timeout = 1)
    public void testTimeout_0(){
        //TODO
        for(int i=0;i<10;i++){
            System.out.println(i);
        }
    }

    @Test(timeout = 1)
    public void testTimeout_1(){
        //TODO
        for(int i=0;i<10;i++){
            System.out.println(i);
        }
    }
}
