package junitTest; /*********************
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 16:34
 *
 *********************/

import org.junit.runner.RunWith;
import org.junit.runners.Suite;
import org.junit.runners.Suite.SuiteClasses;

/**
 * 测试套件类
 * 注解：
 * - @RunWith：指定单元测试执行类，默认使用Suit
 * - @SuiteClasses：“{}”括起来的测试类的所有测试方法被包装到一个测试套件中，都会被执行；
 */
@RunWith(Suite.class)
@SuiteClasses({A_ModelTest.class,B_ModelTest.class})
public class JUnitSuitTest {

}
