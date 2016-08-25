package converter;

/**
 * This class provides a simple logger to generate a log message to the standard
 * output or error.
 * 
 * @author Jun Araki
 */
public class Logger {

  /**
   * Prints out the specified message in the standard output.
   * 
   * @param message
   */
  public static void printStandardOutput(Object message) {
    System.out.println(message);
  }

  /**
   * Prints out the specified message in the standard error.
   * 
   * @param message
   */
  public static void printStandardError(Object message) {
    System.err.println(message);
  }

  /**
   * Logs the specified message.
   * 
   * @param message
   */
  public static void log(Object message) {
    printStandardOutput(message);
  }

  /**
   * Logs the specified message of the ERROR level.
   * 
   * @param message
   */
  public static void error(Object message) {
    printStandardError("[ERROR] " + message);
  }

  /**
   * Logs the specified message of the WARN level.
   * 
   * @param message
   */
  public static void warn(Object message) {
    printStandardError("[WARN] " + message);
  }

  /**
   * Logs the specified message of the INFO level.
   * 
   * @param message
   */
  public static void info(Object message) {
    printStandardOutput("[INFO] " + message);
  }

  /**
   * Logs the specified message of the DEBUG level.
   * 
   * @param message
   */
  public static void debug(Object message) {
    printStandardError("[DEBUG] " + message);
  }

}
