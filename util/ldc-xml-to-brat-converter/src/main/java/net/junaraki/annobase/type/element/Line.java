package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

/**
 * A line annotation.
 * 
 * @author Jun Araki
 */
public class Line extends ElementAnnotation {

  private static final long serialVersionUID = 987954789227795432L;

  /** The line number of this line */
  private int lineNo;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public Line(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

  @Override
  public String toString() {
    return String.format("%s [%d,%d] [%d] [%s]", getTypeName(), getBegin(), getEnd(), lineNo,
            getText());
  }

  public int getLineNo() {
    return lineNo;
  }

  public void setLineNo(int lineNo) {
    this.lineNo = lineNo;
  }

}
