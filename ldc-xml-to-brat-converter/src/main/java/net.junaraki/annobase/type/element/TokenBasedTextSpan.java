package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.util.CollectionUtils;

/**
 * This class represents a span based on tokens.
 * 
 * @author Jun Araki
 */
public class TokenBasedTextSpan extends ElementAnnotation {

  private static final long serialVersionUID = -959720467295680500L;

  /** A list of tokens for this span */
  protected List<Token> tokens;

  /** A head word of this span, if any */
  protected Token headWord;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public TokenBasedTextSpan(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    tokens = new ArrayList<Token>();
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    // Expect super classes to compare 'annBase', 'typeName', and 'spans'.
    if (!super.equals(obj)) {
      return false;
    }
    if (!(obj instanceof ElementAnnotation)) {
      return false;
    }

    TokenBasedTextSpan that = (TokenBasedTextSpan) obj;
    if (!getTokens().equals(that.getTokens())) {
      return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + super.hashCode();
      for (Token token : tokens) {
        result = 31 * result + token.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  /**
   * Returns a head word using dependency annotation.
   * 
   * @return
   */
  public Token findHeadWordFromDependency() {
    if (numTokens() == 1) {
      return tokens.get(0);
    } else {
      List<Token> tokens = findTokens();
      if (tokens.size() == 1) {
        return tokens.get(0);
      }
    }

    // Get dependency nodes covered by this annotation.
    List<DependencyNode> nodes = getAnnotationBase().getAnnotationsCoveredBy(DependencyNode.class,
            this);

    // Now we need to decide partial ordering for tokens.
    List<DependencyNode> orderedNodes = new LinkedList<DependencyNode>();

    // Logger.debug(this);
    boolean foundPartialOrdering = false;
    for (int i = 0; i < nodes.size(); i++) {
      DependencyNode node1 = nodes.get(i);
      for (int j = i + 1; j < nodes.size(); j++) {
        DependencyNode node2 = nodes.get(j);

        if (node1.isAncestor(node2)) {
          foundPartialOrdering = true;

          if (orderedNodes.contains(node1)) {
            if (orderedNodes.contains(node2)) {
              int index1 = orderedNodes.indexOf(node1);
              int index2 = orderedNodes.indexOf(node2);
              if (index1 > index2) {
                // We need to reverse node1 and node2
                orderedNodes.set(index2, node1);
                orderedNodes.set(index1, node2);
              }
            } else {
              int index1 = orderedNodes.indexOf(node1);
              orderedNodes.add(index1 + 1, node2);
            }
          } else {
            if (orderedNodes.contains(node2)) {
              int index2 = orderedNodes.indexOf(node2);
              if (index2 > 0) {
                orderedNodes.add(index2 - 1, node1);
              } else {
                orderedNodes.add(0, node1);
              }
            } else {
              orderedNodes.add(node1);
              orderedNodes.add(node2);
            }
          }
        } else if (node2.isAncestor(node1)) {
          foundPartialOrdering = true;

          if (orderedNodes.contains(node1)) {
            if (orderedNodes.contains(node2)) {
              int index1 = orderedNodes.indexOf(node1);
              int index2 = orderedNodes.indexOf(node2);
              if (index2 > index1) {
                // We need to reverse node1 and node2
                orderedNodes.set(index1, node2);
                orderedNodes.set(index2, node1);
              }
            } else {
              int index1 = orderedNodes.indexOf(node1);
              if (index1 > 0) {
                orderedNodes.add(index1 - 1, node1);
              } else {
                orderedNodes.add(0, node1);
              }
            }
          } else {
            if (orderedNodes.contains(node2)) {
              int index2 = orderedNodes.indexOf(node2);
              orderedNodes.add(index2 + 1, node1);
            } else {
              orderedNodes.add(node2);
              orderedNodes.add(node1);
            }
          }
        }
      }
    }

    if (!foundPartialOrdering) {
      // Logger.warn("No head word found due to no partial ordering for " + this);
      return null;
    }

    Token headWord = orderedNodes.get(0).getToken();
    // Logger.debug("Head word for " + getAnnotationInfo(ann) + ": " + getAnnotationInfo(headWord));
    return headWord;
  }

  /**
   * Returns a list of tokens associated with the given annotation. Mostly, these tokens are the
   * ones covered by the annotation, but they could be tokens that covers the annotation.
   * 
   * @return
   */
  public List<Token> findAssociatedTokens() {
    List<Token> tokens = annBase.getAnnotationsCoveredBy(Token.class, this);
    if (CollectionUtils.isEmpty(tokens)) {
      // Occasionally, an entity mention (e.g., "UFC") is smaller a single token (e.g.,
      // "UFC-specific"). In such cases, we might want to recover the token for the entity
      // mention, but this demand depends on a task.
      tokens = annBase.getAnnotationsCovering(Token.class, this);
    }

    return tokens;
  }

  /**
   * Returns a mapping from indexes to contextual tokens surrounding this annotation within the
   * sliding window of the given size. The entire annotation is accessed by index 0. For example, if
   * a sentence has 4 tokens "[t1] [t2] [t3] [t4]", this annotation spans [t2] and [t3], and the
   * window size is 2, then this method returns a mapping from -1 to [t1], and one from 1 to [t4].
   * If an index is beyond tokens in the sentence, then the mapping does not have such indexes.
   * 
   * @param windowSize
   * @return
   */
  public Map<Integer, Token> getContextTokens(int windowSize) {
    Map<Integer, Token> contextTokens = new HashMap<Integer, Token>();

    if (numTokens() == 0) {
      setTokens(findAssociatedTokens());
    }

    Token firstToken = getFirstToken();
    Sentence sent = firstToken.getSentence();
    if (sent == null) {
      return contextTokens;
    }
    if (sent.numTokens() == 0) {
      return contextTokens;
    }

    int numTokens = sent.numTokens();
    List<Token> tokens = sent.getTokens();
    int currIndex = tokens.indexOf(firstToken);
    int begin = 1 - windowSize;
    for (int i = begin; i < 0; i++) {
      int index = currIndex + i;
      if (index >= 0) {
        contextTokens.put(i, tokens.get(index));
      }
    }

    Token lastToken = getLastToken();
    currIndex = tokens.indexOf(lastToken);
    int end = windowSize - 1;
    for (int i = 1; i <= end; i++) {
      int index = currIndex + i;
      if (index < numTokens) {
        contextTokens.put(i, tokens.get(index));
      }
    }

    return contextTokens;
  }

  /**
   * Returns tokens covered by this annotation.
   * 
   * @return
   */
  public List<Token> findTokens() {
    return getAnnotationBase().getAnnotationsCoveredBy(Token.class, this);
  }

  /**
   * Returns true if the given token is valid in the sense that it is included in this span.
   * 
   * @param token
   */
  public boolean isValidToken(Token token) {
    if (!token.getSourceDocument().equals(getSourceDocument())) {
      return false;
    }
    if (!token.coveredBy(this)) {
      return false;
    }

    return true;
  }

  /**
   * Returns the i-th token in this span.
   * 
   * @param index
   * @return
   */
  public Token getTokenAt(int index) {
    if (index < 0 || index >= numTokens()) {
      throw new IllegalArgumentException("Invalid index: " + index);
    }

    return getTokens().get(index);
  }

  public List<Token> getTokens() {
    return tokens;
  }

  public void setTokens(List<Token> tokens) {
    if (CollectionUtils.isEmpty(tokens)) {
      return;
    }

    // Occasionally, an entity mention (e.g., "UFC") is smaller a single token (e.g.,
    // "UFC-specific"). In such cases, we might want to recover the token for the entity mention.
    // Thus, we make the following setting lenient.
    // for (Token token : tokens) {
    // if (!isValidToken(token)) {
    // throw new IllegalArgumentException("Found an invalid token " + token);
    // }
    // }
    this.tokens = tokens;
  }

  /**
   * Returns the first token.
   * 
   * @return
   */
  public Token getFirstToken() {
    return tokens.get(0);
  }

  /**
   * Sets the given token to the first token of this annotation.
   * 
   * @param token
   */
  public void setFirstToken(Token token) {
    if (numTokens() == 0) {
      tokens.add(token);
    } else {
      tokens.set(0, token);
    }
  }

  public Token getLastToken() {
    return tokens.get(tokens.size() - 1);
  }

  /**
   * Adds the given token to this span.
   * 
   * @param token
   */
  public void addToken(Token token) {
    if (token == null) {
      return;
    }

    if (!isValidToken(token)) {
      throw new IllegalArgumentException("Found an invalid token " + token);
    }
    tokens.add(token);
  }

  /**
   * Adds the given tokens to this span.
   * 
   * @param tokens
   */
  public void addTokens(List<Token> tokens) {
    for (Token token : tokens) {
      addToken(token);
    }
  }

  /**
   * Returns the number of tokens in this sentence.
   * 
   * @return
   */
  public int numTokens() {
    return tokens.size();
  }

  /**
   * Returns the sentence of this annotation.
   * 
   * @return
   */
  public Sentence getSentence() {
    return getFirstToken().getSentence();
  }

  public Token getHeadWord() {
    return headWord;
  }

  public void setHeadWord(Token headWord) {
    this.headWord = headWord;
  }

}
