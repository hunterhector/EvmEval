package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

public class Chunk extends TokenBasedTextSpan {

  private static final long serialVersionUID = 8281334541581338144L;

  private String label;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public Chunk(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

  public String getLabel() {
    return label;
  }

  public void setLabel(String label) {
    this.label = label;
  }

}
