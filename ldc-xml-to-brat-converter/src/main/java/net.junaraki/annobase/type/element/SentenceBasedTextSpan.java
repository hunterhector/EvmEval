package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.util.CollectionUtils;

/**
 * This annotation represents a span based on sentences.
 * 
 * @author Jun Araki
 */
public class SentenceBasedTextSpan extends ElementAnnotation {

  private static final long serialVersionUID = -3356223766790799838L;

  /** A list of sentences for this span */
  protected List<Sentence> sents;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public SentenceBasedTextSpan(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    sents = new ArrayList<Sentence>();
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

    SentenceBasedTextSpan that = (SentenceBasedTextSpan) obj;
    List<Sentence> theseSents = getSentences();
    List<Sentence> thoseSents = that.getSentences();
    if (theseSents == null) {
      if (thoseSents != null) {
        return false;
      }
    } else {
      if (!theseSents.equals(thoseSents)) {
        return false;
      }
    }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + super.hashCode();
      for (Sentence sent : sents) {
        result = 31 * result + sent.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  /**
   * Returns true if the given sent is valid in the sense that it is included in this span.
   * 
   * @param sent
   */
  public boolean isValidSentence(Sentence sent) {
    if (!sent.getAnnotationBase().equals(getAnnotationBase())) {
      return false;
    }
    if (!sent.coveredBy(this)) {
      return false;
    }

    return true;
  }

  /**
   * Returns the i-th sent in this span.
   * 
   * @param index
   * @return
   */
  public Sentence getSentenceAt(int index) {
    int numSents = numSentences();
    if (index < 0 || index >= numSents) {
      throw new IndexOutOfBoundsException(String.format("Index: %d, Size: %d", index, numSents));
    }

    return getSentences().get(index);
  }

  public List<Sentence> getSentences() {
    return sents;
  }

  public void setSentences(List<Sentence> sents) {
    if (CollectionUtils.isEmpty(sents)) {
      return;
    }

    for (Sentence sent : sents) {
      if (!isValidSentence(sent)) {
        throw new IllegalArgumentException("Found an invalid sent " + sent);
      }
    }
    this.sents = sents;
  }

  /**
   * Adds the given sent to this span.
   * 
   * @param sent
   */
  public void addSentence(Sentence sent) {
    if (sent == null) {
      return;
    }

    if (!isValidSentence(sent)) {
      throw new IllegalArgumentException("Found an invalid sent " + sent);
    }
    sents.add(sent);
  }

  /**
   * Adds the given sents to this span.
   * 
   * @param sents
   */
  public void addSentences(List<Sentence> sents) {
    for (Sentence sent : sents) {
      addSentence(sent);
    }
  }

  /**
   * Returns the number of sents in this sentence.
   * 
   * @return
   */
  public int numSentences() {
    return sents.size();
  }

}
