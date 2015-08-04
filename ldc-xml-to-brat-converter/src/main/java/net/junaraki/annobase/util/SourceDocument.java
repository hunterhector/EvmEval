package net.junaraki.annobase.util;

import java.io.Serializable;

/**
 * This class represents a general-purpose document.
 * 
 * @author Jun Araki
 */
public class SourceDocument implements Serializable {

  private static final long serialVersionUID = -8209607085512999198L;

  /** The text of this document.  This is a required field. */
  protected final String text;

  /** The ID of this document.  This is an optional field. */
  protected String docId;

  /** Lazily initialized, cached hashCode */
  private volatile int hashCode;

  /**
   * Public constructor.
   * 
   * @param text
   */
  public SourceDocument(String text) {
    this.text = text;
  }

  /**
   * Public constructor.
   * 
   * @param text
   * @param docId
   */
  public SourceDocument(String text, String docId) {
    this.text = text;
    this.docId = docId;
  }

  @Override
  public String toString() {
    StringBuilder buf = new StringBuilder();
    if (docId != null && docId != "") {
      buf.append(docId);
      buf.append(System.lineSeparator());
    }
    buf.append(text);

    return buf.toString();
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + text.hashCode();
      if (docId != null && docId != "") {
        result = 31 * result + docId.hashCode();
      }
      hashCode = result;
    }

    return result;
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    if (!(obj instanceof SourceDocument)) {
      return false;
    }

    SourceDocument that = (SourceDocument) obj;
    if (!text.equals(that.getText())) {
      return false;
    }

    String thatDocId = that.getId();
    if (docId == null) {
      if (thatDocId != null) {
        return false;
      }
    } else {
      if (!docId.equals(thatDocId)) {
        return false;
      }
    }

    return true;
  }

  public String getText() {
    return text;
  }

  public String getText(int begin, int end) {
    return text.substring(begin, end);
  }

  /**
   * Returns a partial text in the range of the given span.
   * 
   * @param span
   * @return
   */
  public String getText(Span span) {
    return getText(span.getBegin(), span.getEnd());
  }

  public String getId() {
    return docId;
  }

}
