package token;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;

import edu.stanford.nlp.ling.CoreAnnotations.CharacterOffsetBeginAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.CharacterOffsetEndAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

/**
 * A tokenizer using the Stanford CoreNLP tool.
 * 
 * @author Jun Araki
 */
public class Tokenizer {

  /** The Stanford CoreNLP tool to be used for sentence segmentation */
  private static StanfordCoreNLP stanfordCorenlp;

  static {
    // Initialize the Stanford CoreNLP tool.
    Properties props = new Properties();
    props.setProperty("annotators", "tokenize");
    stanfordCorenlp = new StanfordCoreNLP(props);
  }

  /**
   * Tokenizes the given text.
   * 
   * @param text
   * @return
   */
  public static List<String> tokenize(String text) {
    return tokenizeStanford(text);
  }

  /**
   * Tokenizes the given text using an additional explicit set of characters for separation.
   * 
   * @param text
   * @param separatorChars
   * @return
   */
  public static List<String> tokenize(String text, String separatorChars) {
    if (StringUtils.isEmpty(separatorChars)) {
      return tokenize(text);
    }

    List<String> newTokens = new ArrayList<String>();
    List<String> tokens = tokenizeStanford(text);
    for (String token : tokens) {
      if (!StringUtils.containsAny(token, separatorChars)) {
        // In this case, the token contains no characters for separation.
        newTokens.add(token);
        continue;
      }

      // The token contains a character for separation.
      newTokens.addAll(new ArrayList<String>(
              Arrays.asList(StringUtils.split(token, separatorChars))));
    }

    return newTokens;
  }

  /**
   * Tokenizes the given text, and returns tokens with their offsets.
   * 
   * @param text
   * @return
   */
  public static List<Token> tokenizeWithOffset(String text) {
    return tokenizeStanfordWithOffset(text);
  }

  /**
   * Tokenizes the given text using an additional explicit set of characters for separation, and
   * returns tokens with their offsets.
   * 
   * @param text
   * @param separatorChars
   * @return
   */
  public static List<Token> tokenizeWithOffset(String text, String separatorChars) {
    if (StringUtils.isEmpty(separatorChars)) {
      return tokenizeWithOffset(text);
    }

    List<Token> newTokens = new ArrayList<Token>();
    List<Token> tokens = tokenizeWithOffset(text);
    for (Token token : tokens) {
      if (!StringUtils.containsAny(token.getCoveredText(), separatorChars)) {
        // In this case, the token contains no characters for separation.
        newTokens.add(token);
        continue;
      }

      // The token contains a character for separation.
      List<Token> tmpTokens = new ArrayList<Token>();
      int begin = token.getBegin();
      int end = token.getEnd();
      String tmpStr = token.getCoveredText();
      while (StringUtils.containsAny(tmpStr, separatorChars)) {
        int index = StringUtils.indexOfAny(tmpStr, separatorChars);
        if (index > 0) {
          tmpTokens.add(new Token(token.getDocument(), begin, begin + index));
        }
        begin = begin + index + 1;  // Let's try a next piece of the sub-token.
        tmpStr = tmpStr.substring(index + 1);
      }
      // For the last token
      if (begin < end) {
        tmpTokens.add(new Token(token.getDocument(), begin, end));
      }

      if (!CollectionUtils.isEmpty(tmpTokens)) {
        newTokens.addAll(tmpTokens);
      }
    }

    return newTokens;
  }

  /**
   * Tokenizes the given text, and returns a list of tokens.
   * 
   * @param text
   * @return
   */
  private static List<String> tokenizeStanford(String text) {
    List<String> tokens = new ArrayList<String>();

    Annotation textAnn = new Annotation(text);
    stanfordCorenlp.annotate(textAnn);
    for (CoreMap tokenAnn : textAnn.get(TokensAnnotation.class)) {
      int begin = tokenAnn.get(CharacterOffsetBeginAnnotation.class);
      int end = tokenAnn.get(CharacterOffsetEndAnnotation.class);
      String token = text.substring(begin, end);
      tokens.add(token);
    }

    return tokens;
  }

  /**
   * Tokenizes the given text, and returns a list of tokens with a begin and end offset.
   * 
   * @param text
   * @return
   */
  private static List<Token> tokenizeStanfordWithOffset(String text) {
    List<Token> tokens = new ArrayList<Token>();

    Document doc = new Document(text);
    Annotation textAnn = new Annotation(text);
    stanfordCorenlp.annotate(textAnn);
    for (CoreMap tokenAnn : textAnn.get(TokensAnnotation.class)) {
      int begin = tokenAnn.get(CharacterOffsetBeginAnnotation.class);
      int end = tokenAnn.get(CharacterOffsetEndAnnotation.class);
      Token token = new Token(doc, begin, end);
      tokens.add(token);
    }

    return tokens;
  }

  /**
   * A simple tester.
   * 
   * @param args
   */
  public static void main(String[] args) {
    String str = "A test, (string).\nHello this is a 2nd sentence.\nHere is a quote: \"This is the quote.\"\nSentence 4. The Spanish author Cervantes wrote \"Don Quixote\".";
    List<String> tokensStanford = Tokenizer.tokenizeStanford(str);

    System.out.println("Sentences: " + str);

    System.out.print("Tokens by Stanford: ");
    for (int i = 0; i < tokensStanford.size(); i++) {
      String token = tokensStanford.get(i);
      if (i > 0) {
        System.out.print("/");
      }
      System.out.print(token);
    }
    System.out.println("");

    String separatorChars = "s";
    tokensStanford = Tokenizer.tokenize(str, separatorChars);
    System.out.print("Tokens by Stanford with additional separators '" + separatorChars + "': ");
    for (int i = 0; i < tokensStanford.size(); i++) {
      String token = tokensStanford.get(i);
      if (i > 0) {
        System.out.print("/");
      }
      System.out.print(token);
    }
    System.out.println("");

    System.out.println("Tokenization test:");
    List<Token> tokens = Tokenizer.tokenizeWithOffset(str, "t");
    for (Token token : tokens) {
      System.out.println(token);
    }
  }

}
