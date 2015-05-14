package net.junaraki.annobase.type.element;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import net.junaraki.annobase.AnnotationBase;

/**
 * A token annotation.
 * 
 * @author Jun Araki
 */
public class Token extends ElementAnnotation {

  private static final long serialVersionUID = -3184300942811343383L;

  /** Part-of-speech tag */
  protected String pos;

  protected String lemma;

  protected Sentence sent;

  protected ConstituencyNode conNode;

  protected DependencyNode depNode;

  protected SemanticRolePredicateNode semRolePredNode;

  protected SemanticRoleArgumentNode semRoleArgNode;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public Token(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

  /**
   * Returns a mapping from indexes to contextual tokens surrounding this token within the sliding
   * window of the given size. The current token is accessed by index 0. If a sentence has three
   * tokens "[t1] [t2] [t3]", this token is [t2], and the window size is 2, then this method returns
   * a mapping from -1 to [t1], from 0 to [t2], and from 1 to [t3]. If an index is beyond tokens in
   * the sentence, then the mapping does not have such indexes.
   * 
   * @param windowSize
   * @return
   */
  public Map<Integer, Token> getContextTokens(int windowSize) {
    Map<Integer, Token> contextTokens = new HashMap<Integer, Token>();

    if (sent == null) {
      return contextTokens;
    }
    if (sent.numTokens() == 0) {
      return contextTokens;
    }

    int numTokens = sent.numTokens();
    List<Token> tokens = sent.getTokens();
    int currIndex = tokens.indexOf(this);
    int begin = 1 - windowSize;
    int end = windowSize - 1;
    for (int i = begin; i <= end; i++) {
      int index = currIndex + i;
      if (index >= 0 && index < numTokens) {
        contextTokens.put(i, tokens.get(index));
      }
    }

    return contextTokens;
  }

  /**
   * Returns the next token of this token in the same sentence.
   * 
   * @return
   */
  public Token getNextToken() {
    if (sent == null) {
      return null;
    }
    if (sent.numTokens() == 0) {
      return null;
    }

    int numTokens = sent.numTokens();
    List<Token> tokens = sent.getTokens();
    int currIndex = tokens.indexOf(this);
    if (currIndex < numTokens - 1) {
      return tokens.get(currIndex + 1);
    }
    return null;
  }

  /**
   * Returns the previous token of this token in the same sentence.
   * 
   * @return
   */
  public Token getPreviousToken() {
    if (sent == null) {
      return null;
    }
    if (sent.numTokens() == 0) {
      return null;
    }

    List<Token> tokens = sent.getTokens();
    int currIndex = tokens.indexOf(this);
    if (currIndex > 0) {
      return tokens.get(currIndex - 1);
    }
    return null;
  }

  /**
   * Returns true if this token is the first one in the sentence which it belongs to.
   * 
   * @return
   */
  public boolean isFirstToken() {
    if (sent == null) {
      return false;
    }
    if (sent.numTokens() == 0) {
      return false;
    }

    if (sent.getTokenAt(0).equals(this)) {
      return true;
    }

    return false;
  }

  /**
   * Returns true if this token is the last one in the sentence which it belongs to.
   * 
   * @return
   */
  public boolean isLastToken() {
    if (sent == null) {
      return false;
    }
    if (sent.numTokens() == 0) {
      return false;
    }

    if (sent.getTokenAt(sent.numTokens() - 1).equals(this)) {
      return true;
    }

    return false;
  }

  public String getPos() {
    return pos;
  }

  public void setPos(String pos) {
    this.pos = pos;
  }

  public String getLemma() {
    return lemma;
  }

  public void setLemma(String lemma) {
    this.lemma = lemma;
  }

  public Sentence getSentence() {
    return sent;
  }

  public void setSentence(Sentence sent) {
    this.sent = sent;
  }

  public ConstituencyNode getConstituencyNode() {
    return conNode;
  }

  public void setConstituencyNode(ConstituencyNode conNode) {
    this.conNode = conNode;
  }

  public DependencyNode getDependencyNode() {
    return depNode;
  }

  public void setDependencyNode(DependencyNode depNode) {
    this.depNode = depNode;
  }

  public SemanticRolePredicateNode getSemanticRolePredicateNode() {
    return semRolePredNode;
  }

  public void setSemanticRolePredicateNode(SemanticRolePredicateNode semRolePredNode) {
    this.semRolePredNode = semRolePredNode;
  }

  public SemanticRoleArgumentNode getSemanticRoleArgumentNode() {
    return semRoleArgNode;
  }

  public void setSemanticRoleArgumentNode(SemanticRoleArgumentNode semRoleArgNode) {
    this.semRoleArgNode = semRoleArgNode;
  }

}
