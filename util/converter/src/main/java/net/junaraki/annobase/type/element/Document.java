package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

/**
 * This annotation represents an entire source document.
 * 
 * @author Jun Araki
 */
public class Document extends SentenceBasedTextSpan {

  private static final long serialVersionUID = -5723258305818279124L;

  private String uri;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public Document(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

  public String getUri() {
    return uri;
  }

  public void setUri(String uri) {
    this.uri = uri;
  }

}
