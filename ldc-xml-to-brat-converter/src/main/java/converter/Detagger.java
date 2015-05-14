package converter;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * This is a simple detagger that removes tags in the given text input.
 * 
 * @author Jun Araki
 */
public class Detagger {

  /**
   * Removes tags from the given text. Tags will be replaced white space.
   * 
   * @param text
   * @return
   */
  public static String detag(String text) {
    if (text == null) {
      return null;
    }

    String detaggedText = detag(text, true);
    if (text.length() != detaggedText.length()) {
      throw new RuntimeException(
              "Unexpectedly a resulting detagged text has length different from the original text");
    }

    return detaggedText;
  }

  /**
   * Removes tags from the given text. The second argument specifies whether tags will be replaced
   * with whitespace characters of the same length.
   * 
   * @param text
   * @param padWhitespace
   * @return
   */
  public static String detag(String text, boolean padWhitespace) {
    StringBuilder buf = new StringBuilder();

    char currChar, prevChar;
    boolean inTag = false; // <something> ... </something>
    for (int i = 0; i < text.length(); i++) {
      currChar = text.charAt(i);

      if (inTag) {
        // At this point, i should be 1 or more
        prevChar = text.charAt(i - 1);
        if (prevChar == '>') {
          inTag = false;
        }
      }

      if (currChar == '<') {
        inTag = true;
      }

      if (inTag) {
        if (padWhitespace) {
          buf.append(" ");
        }
        continue;
      }

      buf.append(currChar);
    }

    return buf.toString();
  }

  /**
   * Removes tags from the given text, except for the tags in the given tag set. The third argument
   * specifies whether tags will be replaced with whitespace characters of the same length.
   * 
   * @param text
   * @param tagSet
   * @param padWhitespace
   * @return
   */
  public static String detag(String text, Set<String> exceptionalTags, boolean padWhitespace) {
    StringBuilder buf = new StringBuilder();

    Set<String> tmp = new HashSet<String>();
    for (String exceptionalTag : exceptionalTags) {
      tmp.add("/" + exceptionalTag);
    }
    exceptionalTags.addAll(tmp);

    char currChar, prevChar;
    boolean inTag = false; // <something> ... </something>
    for (int i = 0; i < text.length(); i++) {
      currChar = text.charAt(i);

      if (inTag) {
        // At this point, i should be 1 or more
        prevChar = text.charAt(i - 1);
        if (prevChar == '>') {
          inTag = false;
        }
      }

      if (currChar == '<') {
        StringBuilder tagBuf = new StringBuilder();
        // Look ahead
        for (int j = i + 1; j < text.length(); j++) {
          char lookAheadChar = text.charAt(j);
          if (lookAheadChar == '>' || lookAheadChar == ' ') {
            break;
          }
          tagBuf.append(lookAheadChar);
        }
        if (!exceptionalTags.contains(tagBuf.toString())) {
          inTag = true;
        }
      }

      if (inTag) {
        if (padWhitespace) {
          buf.append(" ");
        }
        continue;
      }

      buf.append(currChar);
    }

    return buf.toString();
  }

  /**
   * A simple tester.
   * 
   * @param args
   */
  public static void main(String[] args) {
    String text = "test 1<TEST>test 2<TEST2>test 3</TEST2><TEST3>test 4</TEST3></TEST>test 5";
    System.out.println("Original: [" + text + "]");

    System.out.println("Detagged: [" + Detagger.detag(text) + "]");
    System.out.println("Detagged: [" + Detagger.detag(text, false) + "]");

    Set<String> exceptionalTags = new HashSet<String>(Arrays.asList("TEST2"));
    System.out.println("Detagged: [" + Detagger.detag(text, exceptionalTags, true) + "]");

    exceptionalTags = new HashSet<String>(Arrays.asList("TEST2", "TEST3"));
    System.out.println("Detagged: [" + Detagger.detag(text, exceptionalTags, true) + "]");

    exceptionalTags = new HashSet<String>(Arrays.asList("TEST", "TEST2"));
    System.out.println("Detagged: [" + Detagger.detag(text, exceptionalTags, true) + "]");
  }
}
