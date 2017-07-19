package junitTest; /*********************
 *
 *@Author: Jian Zhang
 *@Date: 2017-07-17 15:19
 *
 *********************/

import org.junit.*;

/**
 * JUnit注解
 */
public class JUnitAnnotationTest {

    /**
     * 注解：@BeforeClass
     * 描述：
     * 1 修饰的方法为静态方法;
     * 2 类级别首先执行
     * 3 只执行一次
     */
    @BeforeClass
    public static void getConnection(){
        //TODO
        System.out.println("connecting to MYQL DataBase...");
    }
    @BeforeClass
    public static void getConnection2(){
        //TODO
        System.out.println("connecting to Oracle DataBase...");
    }

    /**
     * 注解：@Before
     * 描述：
     * 1 每个测试方法执行前均会执行该注解修饰的方法
     * 2
     */
    @Before
    public void preTest(){
        //TODO
        System.out.println("is preparing to begin the test...");
    }
    @Before
    public void _preTest(){
        //TODO
        System.out.println("is preparing to begin the test_...");
    }

    /**
     * 注解：@Test
     * 描述：测试方法
     * 注解@Test有两个参数：
     * - expected
     *   期待抛出的异常，值为异常类的class
     * - timeout
     *   测试超时时间，默认0s;
     */
    @Test()
    //expected =java.lang.NullPointerException.class,timeout =15000
    public void test_1(){
        //TODO
        System.out.println("tesing one");
    }
    @Test
    public void test_2(){
        //TODO
        System.out.println("tesing two");
    }
    @Test
    public void test_3(){
        //TODO
        System.out.println("tesing three");
    }

    /**
     * 注解：@After
     * 描述：每个测试方法执行之后均会执行一次该注解修饰的方法
     *
     */
    @After
    public void aftTest(){
        //TODO
        System.out.println("tesing is completed");
    }

    /**
     * 注解：@AfterClass
     * 描述：
     * 1 修饰的方法为静态方法
     * 2 类级别最后执行
     * 3 只执行一次
     */
    @AfterClass
    public static void closeConnection(){
        //TODO
        System.out.println("closing MYQL connection....");
    }
}
