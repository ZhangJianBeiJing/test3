package junitTest; /*********************
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 17:23
 *
 *********************/

import org.junit.Ignore;
import org.junit.Test;

/**
 * 忽略测试
 * 注解：@Ignore
 * 描述：
 * - 作用在测试方法上，则不执行该方法，可用于想跳过执行失败,或抛出异常的方法；
 * - 作用在测试类上，则对整个测试类的所有测试方法均不执行；
 */

public class JUnitIgnoreTest {
    @Test
    public void test_1(){
        System.out.println("test one");
    }
    @Ignore
    @Test
    public void test_2(){
        System.out.println("test two");
    }
}
