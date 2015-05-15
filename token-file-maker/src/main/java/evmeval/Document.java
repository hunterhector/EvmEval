package evmeval;

import java.util.Arrays;

/**
 * This class represents a general document.
 * 
 * @author Jun Araki
 *
 */
public class Document {

  /** The text of this document.  This is a required field. */
  protected String text;

  /** The ID of this document.  This is an optional field. */
  protected String docId;

  /**
   * Public constructor.
   * 
   * @param text
   */
  public Document(String text) {
    this.text = text;
  }

  /**
   * Public constructor.
   * 
   * @param text
   * @param docId
   */
  public Document(String text, String docId) {
    this.text = text;
    this.docId = docId;
  }

  @Override
  public int hashCode() {
    return Arrays.hashCode(new Object[] { text, docId });
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    if (!(obj instanceof Document)) {
      return false;
    }

    Document thatDoc = (Document) obj;
    if (!text.equals(thatDoc.getText())) {
      return false;
    }

    if (docId == null) {
      if (thatDoc.getDocId() != null) {
        return false;
      }
    } else {
      if (!docId.equals(thatDoc.getDocId())) {
        return false;
      }
    }

    return true;
  }

  public String getText() {
    return text;
  }

  /**
   * Returns a partial text in the range of the given span.
   * 
   * @param span
   * @return
   */
  public String getText(Span span) {
    return text.substring(span.getBegin(), span.getEnd());
  }

  public String getDocId() {
    return docId;
  }

}
